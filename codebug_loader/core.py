import codebug_loader.packets
import serial
import logging
logging.basicConfig(level=logging.DEBUG)


STUB_CHANNELS = [0] * 6


class CodeBug(object):
    """Represents a CodeBug."""

    class Channel(object):
        """A channel on a CodeBug."""
        def __init__(self, index):
            self.index = index

        @property
        def value(self):
            # logging.debug("CodeBug.Channel:Getting ch{}".format(self.index))
            get_packet = codebug_loader.packets.GetPacket(self.index)
            return tx_rx_packet(get_packet)

        @value.setter
        def value(self, v):
            # logging.debug("CodeBug.Channel:Setting ch{} to '{}'"
            #               .format(self.index, v))
            set_packet = codebug_loader.packets.SetPacket(self.index, v)
            tx_rx_packet(set_packet)

    def __init__(self):
        self.channels = [self.Channel(i) for i in range(6)]

    def get(self, index):
        return self.channels[index].value

    def set(self, index, v):
        self.channels[index].value = v

    def get_bulk(self, start_index, length):
        # return self.channels[index:index+length].value
        get_bulk_pkt = codebug_loader.packets.GetBulkPacket(start_index,
                                                            length)
        return tx_rx_packet(get_bulk_pkt)

    def set_bulk(self, start_index, values):
        # return self.channels[index:index+length].value
        set_bulk_pkt = codebug_loader.packets.SetBulkPacket(start_index,
                                                            values)
        tx_rx_packet(set_bulk_pkt)


def tx_rx_packet(packet):
    """Sends a packet and waits for a response."""
    global STUB_CHANNELS
    # STUB: still need to build all this
    if isinstance(packet, codebug_loader.packets.GetPacket):
        return STUB_CHANNELS[packet.channel_index]

    elif isinstance(packet, codebug_loader.packets.SetPacket):
        STUB_CHANNELS[packet.channel_index] = packet.value

    elif isinstance(packet, codebug_loader.packets.GetBulkPacket):
        return STUB_CHANNELS[packet.start_channel_index:packet.length]

    elif isinstance(packet, codebug_loader.packets.SetBulkPacket):
        start = packet.start_channel_index
        end = packet.start_channel_index + packet.length
        STUB_CHANNELS = (STUB_CHANNELS[:start] +
                         packet.values +
                         STUB_CHANNELS[end:])
