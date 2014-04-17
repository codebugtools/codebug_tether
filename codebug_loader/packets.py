import struct


CMD_GET, CMD_SET, CMD_GET_BULK, CMD_SET_BULK, CMD_READ, CMD_WRITE = range(6)


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

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.channel_index &= 0b111
        return struct.pack('b', self.cmd_id << 5 | self.channel_index << 2)


class SetPacket(object):
    """SET packet for setting channel values.

    Structure:

        +--------+---------------+--------+--------+
        | cmd_id | channel index | unused | value  |
        +--------+---------------+--------+--------+
        | 3 bits | 3 bits        | 2 bits | 1 byte |
        +--------+---------------+--------+--------+

    """

    def __init__(self, channel_index, value):
        self.cmd_id = CMD_SET
        self.channel_index = channel_index
        self.value = value

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.channel_index &= 0b111
        self.value &= 0xff
        return struct.pack('bb',
                           self.cmd_id << 5 | self.channel_index << 2,
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

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.start_channel_index &= 0b111
        self.length &= 0xff
        return struct.pack('bb',
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

        +--------+---------------------+--------+--------+------------+
        | cmd_id | start channel index | unused | length | values     |
        +--------+---------------------+--------+--------+------------+
        | 3 bits | 3 bits              | 2 bits | 1 byte | 1+ byte(s) |
        +--------+---------------------+--------+--------+------------+

    """

    def __init__(self, start_channel_index, values):
        self.cmd_id = CMD_SET_BULK
        self.start_channel_index = start_channel_index
        self.length = len(values)
        self.values = values

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.start_channel_index &= 0b111
        self.length &= 0xff
        return struct.pack('bb',
                           self.cmd_id << 5 | self.start_channel_index << 2,
                           self.length) + bytes(self.values)


class ReadPacket(object):
    """READ packet for reading large chunks of memory.

    Structure:

        +--------+---------------+--------+
        | cmd_id | start address | length |
        +--------+---------------+--------+
        | 1 byte | 1 byte        | 1 byte |
        +--------+---------------+--------+

    """

    def __init__(self, start_address, length):
        self.cmd_id = CMD_READ
        self.start_address = start_address
        self.length = length

    def to_bytes(self):
        return struct.pack('bbb', self.cmd_id, self.start_address, self.length)


class WritePacket(object):
    """WRITE packet for

    Structure:

        +--------+---------------------+--------+--------+------------+
        | cmd_id | start channel index | unused | length | payload    |
        +--------+---------------------+--------+--------+------------+
        | 3 bits | 3 bits              | 2 bits | 1 byte | 1+ byte(s) |
        +--------+---------------------+--------+--------+------------+

    """

    def __init__(self, start_channel_index, payload):
        self.cmd_id = CMD_WRITE
        self.start_channel_index = start_channel_index
        self.length = len(payload)
        self.payload = payload

    def to_bytes(self):
        self.cmd_id &= 0b111
        self.start_channel_index &= 0b111
        self.length &= 0xff
        return struct.pack('bb',
                           self.cmd_id << 5 | self.start_channel_index << 2,
                           self.length) + self.payload
