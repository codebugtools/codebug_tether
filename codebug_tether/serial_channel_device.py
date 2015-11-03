'''
Useful for interacting with serial devices which use channels.
'''
import struct


ACK_BYTE = 0xCB

CMD_GET = 0
CMD_SET = 1
CMD_GET_BULK = 2
CMD_SET_BULK = 3
CMD_AND = 4
CMD_OR = 5
CMD_AND_BULK = 6
CMD_OR_BULK = 7


class SerialChannelDevice():
    """A serial device with channels to GET/SET."""

    def __init__(self, serial_port):
        self.serial_port = serial_port

    def get(self, channel_index):
        """Returns GetPacket as bytes.

        GET packet is for retreiving channel values.

            +--------+---------------+
            | cmd_id | channel index |
            +--------+---------------+
            | 3 bits | 5 bits        |
            +--------+---------------+

        """
        return self.transaction(
            struct.pack('B', (CMD_GET << 5) | (channel_index & 0x1f)))

    def set(self, channel_index, value):
        """Returns SetPacket as bytes.

        SET packet for setting channel values.

            +--------+---------------+--------+
            | cmd_id | channel index | value  |
            +--------+---------------+--------+
            | 3 bits | 5 bits        | 1 byte |
            +--------+---------------+--------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_SET << 5 | channel_index & 0x1f),
                        value))

    def get_bulk(self, channel_index, length):
        """GET BULK packet for retrieving multiple adjacent channel values
        in one go.

            +--------+---------------------+--------+
            | cmd_id | start channel index | length |
            +--------+---------------------+--------+
            | 3 bits | 5 bits              | 1 byte |
            +--------+---------------------+--------+

        """
        return self.transaction(
            struct.pack('BB',
                        (CMD_GET_BULK << 5 | channel_index & 0x1f),
                        length))

    def set_bulk(self, channel_index, values):
        """SET BULK packet for setting multiple adjacent channel values in
        one go.

            +--------+-----------------+-----+------------+
            | cmd_id | start ch. index | len | values     |
            +--------+-----------------+-----+------------+
            | 3 bits | 5 bits          | 1B  | 1+ byte(s) |
            +--------+-----------------+-----+------------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_SET_BULK << 5 | channel_index & 0x1f),
                        len(values)) + bytes(values))

    def and_mask(self, channel_index, mask):
        self.transaction(AndPacket(index, mask))
        """Returns AndPacket as bytes.

        AND packet for ANDing channel values.

            +--------+---------------+-----------+
            | cmd_id | channel index | AND mask  |
            +--------+---------------+-----------+
            | 3 bits | 5 bits        | 1 byte    |
            +--------+---------------+-----------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_AND << 5 | channel_index & 0x1f),
                        mask))

    def or_mask(self, channel_index, mask):
        """Returns OrPacket as bytes.

        OR packet for ORing channel values.

            +--------+---------------+----------+
            | cmd_id | channel index | OR mask  |
            +--------+---------------+----------+
            | 3 bits | 5 bits        | 1 byte   |
            +--------+---------------+----------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_OR << 5 | channel_index & 0x1f),
                        mask))

    def and_mask_bulk(self, channel_index, masks):
        """AND BULK packet for ANDing multiple adjacent channel values in
        one go.

            +--------+-----------------+-----+------------+
            | cmd_id | start ch. index | len | values     |
            +--------+-----------------+-----+------------+
            | 3 bits | 5 bits          | 1B  | 1+ byte(s) |
            +--------+-----------------+-----+------------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_AND_BULK << 5 | channel_index & 0x1f),
                        len(masks)) + bytes(masks))

    def or_mask_bulk(self, channel_index, masks):
        """OR BULK packet for setting multiple adjacent channel values in
        one go.

            +--------+-----------------+-----+------------+
            | cmd_id | start ch. index | len | values     |
            +--------+-----------------+-----+------------+
            | 3 bits | 5 bits          | 1B  | 1+ byte(s) |
            +--------+-----------------+-----+------------+

        """
        self.transaction(
            struct.pack('BB',
                        (CMD_OR_BULK << 5 | channel_index & 0x1f),
                        len(masks)) + bytes(masks))

    def set_channel_bit(self, channel_index, bit_index, state):
        """Sets a bit in a channel to state."""
        if state:
            self.or_mask(channel_index, 1 << bit_index)
        else:
            self.and_mask(channel_index, 0xff ^ (1 << bit_index))

    def get_channel_bit(self, channel_index, bit_index):
        """Returns a bit from a channel."""
        return (self.get(channel_index) >> bit_index) & 0x1

    def transaction(self, tx_bytes):
        """Sends a packet and waits for a response."""
        # Send the packet
        self.serial_port.write(tx_bytes)

        # CodeBug will always return an ACK byte
        assert self.serial_port.read(1)[0] == ACK_BYTE

        # GET commands will now have extra data returned
        if type(packet) == GetPacket:
            # just read 1 byte
            return struct.unpack('B', self.serial_port.read(1))[0]

        elif type(packet) == GetBulkPacket:
            return struct.unpack('B'*packet.length,
                                 self.serial_port.read(packet.length))
