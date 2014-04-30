import os
import time
import codebug_loader.packets
import serial
import struct
import logging
logging.basicConfig(level=logging.DEBUG)


STUB_CHANNELS = [0] * 6


class CodeBug(object):
    """Represents a CodeBug."""

    class Channel(object):
        """A channel on a CodeBug."""
        def __init__(self, index, codebug_inst):
            self.index = index
            self.cbinst = codebug_inst

        @property
        def value(self):
            # logging.debug("CodeBug.Channel:Getting ch{}".format(self.index))
            get_packet = codebug_loader.packets.GetPacket(self.index)
            return tx_rx_packet(get_packet, self.cbinst.serial_port)

        @value.setter
        def value(self, v):
            # logging.debug("CodeBug.Channel:Setting ch{} to '{}'"
            #               .format(self.index, v))
            set_packet = codebug_loader.packets.SetPacket(self.index, v)
            tx_rx_packet(set_packet, self.cbinst.serial_port)

    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.channels = [self.Channel(i, self) for i in range(6)]

    def get(self, index):
        return self.channels[index].value

    def set(self, index, v):
        self.channels[index].value = v

    def get_bulk(self, start_index, length):
        # return self.channels[index:index+length].value
        get_bulk_pkt = codebug_loader.packets.GetBulkPacket(start_index,
                                                            length)
        return tx_rx_packet(get_bulk_pkt, self.serial_port)

    def set_bulk(self, start_index, values):
        # return self.channels[index:index+length].value
        set_bulk_pkt = codebug_loader.packets.SetBulkPacket(start_index,
                                                            values)
        tx_rx_packet(set_bulk_pkt, self.serial_port)


def tx_rx_packet(packet, serial_port):
    """Sends a packet and waits for a response."""
    # global STUB_CHANNELS
    # # STUB: still need to build all this
    # if isinstance(packet, codebug_loader.packets.GetPacket):
    #     return STUB_CHANNELS[packet.channel_index]

    # elif isinstance(packet, codebug_loader.packets.SetPacket):
    #     STUB_CHANNELS[packet.channel_index] = packet.value

    # elif isinstance(packet, codebug_loader.packets.GetBulkPacket):
    #     return STUB_CHANNELS[packet.start_channel_index:packet.length]

    # elif isinstance(packet, codebug_loader.packets.SetBulkPacket):
    #     start = packet.start_channel_index
    #     end = packet.start_channel_index + packet.length
    #     STUB_CHANNELS = (STUB_CHANNELS[:start] +
    #                      packet.values +
    #                      STUB_CHANNELS[end:])

    # debug
    # os.system('clear')
    # for row in STUB_CHANNELS[:5]:
    #     print("{:05b}".format(row).replace("0", "-").replace("1", "#"))

    # print("Writing {} ({})".format(packet, time.time()))
    # print("data", packet.to_bytes())
    serial_port.write(packet.to_bytes())
    if isinstance(packet, codebug_loader.packets.GetPacket):
        # just read 1 byte
        return struct.unpack('B', serial_port.read(1))[0]

    elif (isinstance(packet, codebug_loader.packets.SetPacket) or
          isinstance(packet, codebug_loader.packets.SetBulkPacket)):
        # just read 1 byte
        assert (struct.unpack('B', serial_port.read(1))[0] ==
                codebug_loader.packets.AckPacket.ACK_BYTE)

    elif isinstance(packet, codebug_loader.packets.GetBulkPacket):
        # read `length` bytes
        # print("len", packet.length)
        return struct.unpack('B'*packet.length,
                             serial_port.read(packet.length))
