import struct


CMD_GET = 0
CMD_SET = 1
CMD_GET_BULK = 2
CMD_SET_BULK = 3
CMD_READ = 4
CMD_WRITE = 5
CMD_ACK = 6


class AckPacket(object):
    """ACK for set/write packets (client waits for ack, otherwise timing
    gets out of sync)

    Structure:

        +--------+--------+
        | cmd_id | unused |
        +--------+--------+
        | 3 bits | 5 bits |
        +--------+--------+

    """

    ACK_BYTE = CMD_ACK << 5

    def __init__(self):
        self.cmd_id = CMD_ACK

    def __str__(self):
        return "ack"

    def __repr__(self):
        return "<AckPacket()>"

    def to_bytes(self):
        self.cmd_id &= 0b111
        return struct.pack('B', self.cmd_id << 5)



class GetPacket(object):
    """GET packet for retreiving channel values.

    Structure:

        +--------+---------------+--------+
        | cmd_id | channel index | unused |
        +--------+---------------+--------+
        | 3 bits | 3 bits        | 2 bits |
        +--------+---------------+--------+

    """

    def __init__(self, channel_index):
        self.cmd_id = CMD_GET
        self.channel_index = channel_index

    def __str__(self):
        return "get ch{}".format(self.channel_index)

    def __repr__(self):
        return "<GetPacket(channel_index={})>".format(self.channel_index)

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.channel_index &= 0b111
        return struct.pack('B', self.cmd_id << 5 | self.channel_index << 2)


class SetPacket(object):
    """SET packet for setting channel values. When OR mask is set,
    0 bits are ignored and only 1's are set.

    Structure:

        +--------+---------------+---------+----------+--------+
        | cmd_id | channel index | OR mask | AND mask | value  |
        +--------+---------------+---------+----------+--------+
        | 3 bits | 3 bits        | 1 bits  | 1 bit    | 1 byte |
        +--------+---------------+---------+----------+--------+

    """

    def __init__(self, channel_index, value, or_mask=False, and_mask=False):
        self.cmd_id = CMD_SET
        self.channel_index = channel_index
        self.value = value
        self.or_mask = int(or_mask)
        self.and_mask = int(and_mask)

    def __str__(self):
        return "set ch{} to {}".format(self.channel_index, self.value)

    def __repr__(self):
        return "<SetPacket(channel_index={},value={},or_mask={},and_mask={})>"\
            .format(self.channel_index,
                    hex(self.value),
                    self.or_mask,
                    self.and_mask)

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.channel_index &= 0b111
        self.value &= 0xff
        self.or_mask &= 0x1
        self.and_mask &= 0x1
        return struct.pack('BB',
                           (self.cmd_id << 5 |
                            self.channel_index << 2 |
                            self.or_mask << 1 |
                            self.and_mask),
                           self.value)


class GetBulkPacket(object):
    """GET BULK packet for retrieving multiple adjacent channel values
    in one go.

    Structure:

        +--------+---------------------+--------+--------+
        | cmd_id | start channel index | unused | length |
        +--------+---------------------+--------+--------+
        | 3 bits | 3 bits              | 2 bits | 1 byte |
        +--------+---------------------+--------+--------+

    """

    def __init__(self, start_channel_index, length):
        self.cmd_id = CMD_GET_BULK
        self.start_channel_index = start_channel_index
        self.length = length

    def __str__(self):
        return "get {} channels from ch{}".format(self.length,
                                                  self.start_channel_index)

    def __repr__(self):
        return "<GetBulkPacket(start_channel_index={},length={})>".format(
            self.start_channel_index,
            self.length)

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.start_channel_index &= 0b111
        self.length &= 0xff
        return struct.pack('BB',
                           self.cmd_id << 5 | self.start_channel_index << 2,
                           self.length)


class SetBulkPacket(object):
    """SET BULK packet for setting multiple adjacent channel values in
    one go. Just provide this class with the values and the length
    will be inferred.

    Example:

        # creates a packet which sets channels 1, 2, 3 to 7, 8 and 9
        packet = SetBulkPacket(1, bytes(7, 8, 9))

    Structure:

        +--------+-----------------+---------+----------+-----+------------+
        | cmd_id | start ch. index | OR mask | AND mask | len | values     |
        +--------+-----------------+---------+----------+-----+------------+
        | 3 bits | 3 bits          | 1 bit   | 1 bit    | 1B  | 1+ byte(s) |
        +--------+-----------------+---------+----------+-----+------------+

    """

    def __init__(self,
                 start_channel_index,
                 values,
                 or_mask=False,
                 and_mask=False):
        self.cmd_id = CMD_SET_BULK
        self.start_channel_index = start_channel_index
        self.length = len(values)
        self.values = values
        self.or_mask = int(or_mask)
        self.and_mask = int(and_mask)

    def __str__(self):
        return "set {} channels from ch{} to {}".format(
            self.length, self.start_channel_index, self.values)

    def __repr__(self):
        s = "<SetBulkPacket(start_channel_index={},length={},values={})>"
        return s.format(self.start_channel_index, self.length, self.values)

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.start_channel_index &= 0b111
        self.length &= 0xff
        self.or_mask &= 0x1
        self.and_mask &= 0x1
        return struct.pack('BB',
                           (self.cmd_id << 5 |
                            self.start_channel_index << 2 |
                            self.or_mask << 1 |
                            self.and_mask),
                           self.length) + bytes(self.values)


# class ReadPacket(object):
#     """READ packet for reading large chunks of memory.

#     Structure:

#         +--------+--------+---------------+--------+
#         | cmd_id | unused | start address | length |
#         +--------+--------+---------------+--------+
#         | 3 bits | 5 bits | 1 byte        | 1 byte |
#         +--------+--------+---------------+--------+

#     """

#     def __init__(self, start_address, length):
#         self.cmd_id = CMD_READ
#         self.start_address = start_address
#         self.length = length

#     def __str__(self):
#         return "read {} bytes from {}".format(self.length, self.start_address)

#     def __repr__(self):
#         s = "<ReadPacket(start_address={},length={})>"
#         return s.format(self.start_address, self.length)

#     def to_bytes(self):
#         return struct.pack('BBB',
#                            self.cmd_id << 5,
#                            self.start_address,
#                            self.length)


# class WritePacket(object):
#     """WRITE packet for writing large chunks of memory. Payload is in bytes.

#     Structure:

#         +--------+--------+---------------+--------+------------+
#         | cmd_id | unused | start address | length | payload    |
#         +--------+--------+---------------+--------+------------+
#         | 3 bits | 5 bits | 1 byte        | 1 byte | 1+ byte(s) |
#         +--------+--------+---------------+--------+------------+

#     """

#     def __init__(self, start_address, payload):
#         self.cmd_id = CMD_WRITE
#         self.start_address = start_address
#         self.length = len(payload)
#         self.payload = payload

#     def __str__(self):
#         return "write {} bytes to {}".format(self.length,
#                                              self.start_address)

#     def __repr__(self):
#         s = "<WritePacket(start_address={},length={},values={})>"
#         return s.format(self.start_address, self.length, self.values)

#     def to_bytes(self):
#         self.cmd_id &= 0b111
#         self.start_address &= 0xff
#         self.length &= 0xff
#         return struct.pack('BBB',
#                            self.cmd_id << 5,
#                            self.start_address,
#                            self.length) + self.payload
