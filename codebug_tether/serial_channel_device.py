'''
Useful for interacting with serial devices which use channels.
'''
import struct


ACK_BYTE = bytes((0xCB,))

CMD_GET = 0
CMD_SET = 1
CMD_GET_BULK = 2
CMD_SET_BULK = 3
CMD_AND = 4
CMD_OR = 5
CMD_GET_BUFFER= 6
CMD_SET_BUFFER = 7


class SerialChannelDevice():
    """A serial device with single-byte channels and several-byte
    buffers.

    Channels can be GET/SET individually or in bulk.

    Buffers can be GET/SET in bulk only.

    Consult device documentation for channel/buffer implementation.

    +------------------------------------------------------------------+
    | Serial Channel Device                                            |
    |                                                                  |
    | Channels (1B)  Buffers (XB)                                      |
    | +-----------+  +-----------+-----------+-----------+-----------+ |
    | |    ch0    |  |  buf0-0   |  buf0-1   |    ...    |  buf0-N   | |
    | +-----------+  +-----------+-----------+-----------+-----------+ |
    | |    ch1    |  +-----------+-----------+-----------+-----------+ |
    | +-----------+  |  buf1-0   |  buf1-1   |    ...    |  buf1-N   | |
    | |    ...    |  +-----------+-----------+-----------+-----------+ |
    | +-----------+                                                    |
    | |    chN    |                                                    |
    | +-----------+                                                    |
    +------------------------------------------------------------------+
    """

    def __init__(self, serial_port):
        self.serial_port = serial_port

    def get(self, channel_index):
        """Returns GetPacket as bytes.

        GET packet is for retreiving channel values.

            +--------+---------------+
            | cmd id | channel index |
            +--------+---------------+
            | 3 bits | 5 bits        |
            +--------+---------------+

        """
        self.transaction(
            struct.pack('B', (CMD_GET << 5) | (channel_index & 0x1f)))
        # Serial port will now contain channel data
        return self.serial_port.read(1)

    def set(self, channel_index, value):
        """Returns SetPacket as bytes.

        SET packet for setting channel values.

            +--------+---------------+--------+
            | cmd id | channel index | value  |
            +--------+---------------+--------+
            | 3 bits | 5 bits        | 1 byte |
            +--------+---------------+--------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_SET << 5 | channel_index & 0x1f),
                        value))

    def get_bulk(self, channel_index, length):
        """GET BULK packet for retrieving multiple adjacent channel
        values in one go.

            +--------+---------------------+--------+
            | cmd id | start channel index | length |
            +--------+---------------------+--------+
            | 3 bits | 5 bits              | 1 byte |
            +--------+---------------------+--------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_GET_BULK << 5 | channel_index & 0x1f),
                        length))
        # Serial port will now contain channel data
        return self.serial_port.read(length)

    def set_bulk(self, channel_index, value_bytes):
        """SET BULK packet for setting multiple adjacent channel values
        in one go.

            +--------+-----------------+-----+------------+
            | cmd id | start ch. index | len | values     |
            +--------+-----------------+-----+------------+
            | 3 bits | 5 bits          | 1B  | 1+ byte(s) |
            +--------+-----------------+-----+------------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_SET_BULK << 5 | channel_index & 0x1f),
                        len(value_bytes)) + value_bytes)

    def and_mask(self, channel_index, mask):
        """Returns AndPacket as bytes.

        AND packet for ANDing channel values.

            +--------+---------------+-----------+
            | cmd id | channel index | AND mask  |
            +--------+---------------+-----------+
            | 3 bits | 5 bits        | 1 byte    |
            +--------+---------------+-----------+

        """
        self.transaction(
            struct.pack('B', (CMD_AND << 5 | channel_index & 0x1f)) + \
            bytes((mask,)))

    def or_mask(self, channel_index, mask):
        """Returns OrPacket as bytes.

        OR packet for ORing channel values.

            +--------+---------------+----------+
            | cmd id | channel index | OR mask  |
            +--------+---------------+----------+
            | 3 bits | 5 bits        | 1 byte   |
            +--------+---------------+----------+

        """
        self.transaction(
            struct.pack('B', (CMD_OR << 5 | channel_index & 0x1f)) + \
            bytes((mask,)))

    def set_bit(self, channel_index, bit_index, state):
        """Sets a bit in a channel to state."""
        if state:
            self.or_mask(channel_index, 1 << bit_index)
        else:
            self.and_mask(channel_index, 0xff ^ (1 << bit_index))

    def get_bit(self, channel_index, bit_index):
        """Returns a bit from a channel."""
        value = struct.unpack('B', self.get(channel_index))[0]
        return (value >> bit_index) & 0x1

    def get_buffer(self, buffer_index, length, offset=0):
        """GET BUFFER packet for reading whole buffers.

            +--------+--------------+--------+--------+
            | cmd id | buffer index | offset | length |
            +--------+--------------+--------+--------+
            | 3 bits | 5 bits       | 1 byte | 1 byte |
            +--------+--------------+--------+--------+

        """
        self.transaction(
            struct.pack('BBB',
                        (CMD_GET_BUFFER << 5 | buffer_index & 0x1f),
                        offset,
                        length))
        # Serial port will now contain buffer data
        return self.serial_port.read(length)

    def set_buffer(self, buffer_index, value_bytes, offset=0):
        """SET BUFFER packet for setting whole buffers.

            +--------+--------------+--------+--------+------------+
            | cmd id | buffer index | offset | length | values     |
            +--------+--------------+--------+--------+------------+
            | 3 bits | 5 bits       | 1 byte | 1 byte | 1+ byte(s) |
            +--------+--------------+--------+--------+------------+

        """
        self.transaction(
            struct.pack('BBB',
                        (CMD_SET_BUFFER << 5 | buffer_index & 0x1f),
                        offset,
                        len(value_bytes)) + value_bytes)

    def transaction(self, tx_bytes):
        """Sends a packet and waits for a ACK response."""
        # Send the packet
        self.serial_port.write(tx_bytes)

        # CodeBug will always return an ACK byte
        assert self.serial_port.read(1) == ACK_BYTE
