'''
Data structures and functions for converting between packets and raw bytes
for interaction with CodeBug Serial USB Tether.

Send packets to CodeBug over serial and CodeBug returns an ACK byte
followed by data, if requested. For example:

    get_ch1_pkt = packets.GetPacket(1)
    serial_tx(packets.packet_to_bytes(get_ch1_pkt))
    rx = serial_rx(2)
    assert(rx[0] == packets.ACK_BYTE)
    ch1_value = rx[1]

'''
import struct
from collections import namedtuple


ACK_BYTE = 0xCB

CMD_GET = 0
CMD_SET = 1
CMD_GET_BULK = 2
CMD_SET_BULK = 3
CMD_AND = 4
CMD_OR = 5
CMD_AND_BULK = 6
CMD_OR_BULK = 7


GetPacket = namedtuple('GetPacket', 'channel')
SetPacket = namedtuple('SetPacket', ['channel', 'value'])
GetBulkPacket = namedtuple('GetBulkPacket', ['channel', 'length'])
SetBulkPacket = namedtuple('SetBulkPacket', ['channel', 'values'])
AndPacket = namedtuple('AndPacket', ['channel', 'mask'])
OrPacket = namedtuple('OrPacket', ['channel', 'mask'])
AndBulkPacket = namedtuple('AndBulkPacket', ['channel', 'masks'])
OrBulkPacket = namedtuple('OrBulkPacket', ['channel', 'masks'])


def getpacket_to_bytes(packet):
    """Returns GetPacket as bytes.

    GET packet is for retreiving channel values.

        +--------+---------------+
        | cmd_id | channel index |
        +--------+---------------+
        | 3 bits | 5 bits        |
        +--------+---------------+

    """
    return struct.pack('B', (CMD_GET << 5) | (packet.channel & 0x1f))


def setpacket_to_bytes(packet):
    """Returns SetPacket as bytes.

    SET packet for setting channel values.

        +--------+---------------+--------+
        | cmd_id | channel index | value  |
        +--------+---------------+--------+
        | 3 bits | 5 bits        | 1 byte |
        +--------+---------------+--------+

    """
    return struct.pack('BB',
                       (CMD_SET << 5 | packet.channel & 0x1f),
                       packet.value)


def getbulkpacket_to_bytes(packet):
    """GET BULK packet for retrieving multiple adjacent channel values
    in one go.

        +--------+---------------------+--------+
        | cmd_id | start channel index | length |
        +--------+---------------------+--------+
        | 3 bits | 5 bits              | 1 byte |
        +--------+---------------------+--------+

    """
    return struct.pack('BB',
                       (CMD_GET_BULK << 5 | packet.channel & 0x1f),
                       packet.length)


def setbulkpacket_to_bytes(packet):
    """SET BULK packet for setting multiple adjacent channel values in
    one go.

        +--------+-----------------+-----+------------+
        | cmd_id | start ch. index | len | values     |
        +--------+-----------------+-----+------------+
        | 3 bits | 5 bits          | 1B  | 1+ byte(s) |
        +--------+-----------------+-----+------------+

    """
    return struct.pack('BB',
                       (CMD_SET_BULK << 5 | packet.channel & 0x1f),
                       len(packet.values)) + bytes(packet.values)


def andpacket_to_bytes(packet):
    """Returns AndPacket as bytes.

    AND packet for ANDing channel values.

        +--------+---------------+-----------+
        | cmd_id | channel index | AND mask  |
        +--------+---------------+-----------+
        | 3 bits | 5 bits        | 1 byte    |
        +--------+---------------+-----------+

    """
    return struct.pack('BB',
                       (CMD_AND << 5 | packet.channel & 0x1f),
                       packet.mask)


def orpacket_to_bytes(packet):
    """Returns OrPacket as bytes.

    OR packet for ORing channel values.

        +--------+---------------+----------+
        | cmd_id | channel index | OR mask  |
        +--------+---------------+----------+
        | 3 bits | 5 bits        | 1 byte   |
        +--------+---------------+----------+

    """
    return struct.pack('BB',
                       (CMD_OR << 5 | packet.channel & 0x1f),
                       packet.mask)


def andbulkpacket_to_bytes(packet):
    """AND BULK packet for ANDing multiple adjacent channel values in
    one go.

        +--------+-----------------+-----+------------+
        | cmd_id | start ch. index | len | values     |
        +--------+-----------------+-----+------------+
        | 3 bits | 5 bits          | 1B  | 1+ byte(s) |
        +--------+-----------------+-----+------------+

    """
    return struct.pack('BB',
                       (CMD_AND_BULK << 5 | packet.channel & 0x1f),
                       len(packet.masks)) + bytes(packet.masks)


def orbulkpacket_to_bytes(packet):
    """OR BULK packet for setting multiple adjacent channel values in
    one go.

        +--------+-----------------+-----+------------+
        | cmd_id | start ch. index | len | values     |
        +--------+-----------------+-----+------------+
        | 3 bits | 5 bits          | 1B  | 1+ byte(s) |
        +--------+-----------------+-----+------------+

    """
    return struct.pack('BB',
                       (CMD_OR_BULK << 5 | packet.channel & 0x1f),
                       len(packet.masks)) + bytes(packet.masks)


# defined at module so dict is only created once
P2B_FUNCTIONS = {GetPacket: getpacket_to_bytes,
                 SetPacket: setpacket_to_bytes,
                 GetBulkPacket: getbulkpacket_to_bytes,
                 SetBulkPacket: setbulkpacket_to_bytes,
                 AndPacket: andpacket_to_bytes,
                 OrPacket: orpacket_to_bytes,
                 AndBulkPacket: andbulkpacket_to_bytes,
                 OrBulkPacket: orbulkpacket_to_bytes}


def packet_to_bytes(packet):
    """Returns packet as bytes."""
    return P2B_FUNCTIONS[type(packet)](packet)
