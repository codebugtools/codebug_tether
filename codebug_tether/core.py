import os
import time
import serial
import struct
import codebug_tether.packets
from codebug_tether.char_map import (char_map, StringSprite)


DEFAULT_SERIAL_PORT = '/dev/ttyACM0'
NUM_CHANNELS = 7
OUTPUT_CHANNEL_INDEX = INPUT_CHANNEL_INDEX = 5
# Pullups for Port B (Register: WPUB)
PULLUP_CHANNEL_INDEX = 6


class CodeBugRaw(object):
    """Represents a CodeBug. Doesn't have fancy easy-to-use features."""

    def __init__(self, serial_port):
        self.serial_port = serial_port

    def get(self, index):
        get_packet = codebug_tether.packets.GetPacket(index)
        return tx_rx_packet(get_packet, self.serial_port)

    def set(self, index, v, or_mask=False, and_mask=False):
        set_packet = codebug_tether.packets.SetPacket(index,
                                                      v,
                                                      or_mask,
                                                      and_mask)
        tx_rx_packet(set_packet, self.serial_port)

    def get_bulk(self, start_index, length):
        get_bulk_pkt = codebug_tether.packets.GetBulkPacket(start_index,
                                                            length)
        return tx_rx_packet(get_bulk_pkt, self.serial_port)

    def set_bulk(self, start_index, values, or_mask=False, and_mask=False):
        set_bulk_pkt = codebug_tether.packets.SetBulkPacket(start_index,
                                                            values,
                                                            or_mask,
                                                            and_mask)
        tx_rx_packet(set_bulk_pkt, self.serial_port)


class CodeBug(CodeBugRaw):
    """Manipulates CodeBug over a USB serial connection."""
    # Adds fancy, easy-to-use features to CodeBugRaw.

    def __init__(self, serial_port=DEFAULT_SERIAL_PORT):
        super(CodeBug, self).__init__(serial.Serial(serial_port))

    def _int_input_index(self, input_index):
        """Returns an integer input index."""
        # 'A' is 4, 'B' is 5
        if isinstance(input_index, str):
            input_index = 4 if 'a' in input_index.lower() else 5
        return input_index

    def get_input(self, input_index):
        """Returns the state of an input. You can use 'A' and 'B' to
        access buttons A and B.

            >>> codebug = CodeBug()
            >>> codebug.get_input('A')  # switch A is pressed
            1
            >>> codebug.get_input(0)  # assuming pad 0 is connected to GND
            0

        """
        input_index = self._int_input_index(input_index)
        return (self.get(INPUT_CHANNEL_INDEX) >> input_index) & 0x1

    def set_pullup(self, input_index, state):
        """Sets the state of the input pullups. Turn off to enable touch
        sensitive pads (bridge GND and input with fingers).

            >>> codebug = CodeBug()
            >>> codebug.set_pullup(0, 1)  # input pad 0 <10K OHMS
            >>> codebug.set_pullup(2, 0)  # input pad 2 <22M OHMS touch sensitive

        """
        state = 1 if state else 0
        input_index = self._int_input_index(input_index)
        self.set(PULLUP_CHANNEL_INDEX, state << input_index, or_mask=True)

    def set_output(self, output_index, state):
        """Sets the output index to state (CodeBug only have outputs 1 and 3)
        """
        state = 1 if state else 0
        state <<= output_index
        # print(bin(state))
        self.set(OUTPUT_CHANNEL_INDEX, state, or_mask=True)

    def clear(self):
        """Clears the pixels on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.clear()

        """
        for row in range(5):
            self.set_row(row, 0)

    def set_row(self, row, val):
        """Sets a row of PIXELs on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.set_row(0, 0b10101)

        """
        self.set(row, val)

    def get_row(self, row):
        """Returns a row of pixels on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.get_row(0)
            21

        """
        return self.get(row)

    def set_col(self, col, val):
        """Sets an entire column of PIXELs on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.set_col(0, 0b10101)

        """
        # TODO add and_mask into set packet
        for row in range(5):
            state = (val >> (4 - row)) & 0x1  # state of column 1/0
            mask = 1 << (4 - col)  # bit mask to apply to row
            if state > 0:
                self.set(row, mask, or_mask=True)  # OR row with mask
            else:
                # TODO and_mask here
                mask ^= 0x1f
                self.set(row, self.get(row) & mask)  # AND row with mask

    def get_col(self, col):
        """Returns an entire column of PIXELs on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.get_col(0)
            21

        """
        c = 0
        for row in range(5):
            c |= (self.get_row(row) >> (4 - col)) << (4-row)
        return c

    def set_pixel(self, x, y, state):
        """Sets an PIXEL on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.set_pixel(0, 0, 1)

        """
        mask = 1 << (4 - x)  # bit mask to apply to row
        if state > 0:
            self.set(y, mask, or_mask=True)  # OR row with mask
        else:
            # TODO and_mask here
            mask ^= 0x1f
            self.set(y, self.get(y) & mask)  # AND row with mask

    def get_pixel(self, x, y):
        """Returns the state of an PIXEL on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.get_pixel(0, 0)
            1

        """
        return (self.get(y) >> (4 - x)) & 0x1

    def write_text(self, x, y, message, direction="right"):
        """Writes some text on CodeBug at PIXEL (x, y).

            >>> codebug = CodeBug()
            >>> codebug.write_text(0, 0, 'Hello, CodeBug!')

        """
        s = StringSprite(message, direction)
        self.clear()
        for row_i, row in enumerate(s.pixel_state):
            if (row_i - y) >= 0 and (row_i - y) <= 4:
                code_bug_pixel_row = 0
                for col_i, state in enumerate(row):
                    if col_i + x >= 0 and col_i + x <= 4:
                        code_bug_pixel_row |= state << 4 - (col_i + x)
                self.set(4-row_i+y, code_bug_pixel_row)


def tx_rx_packet(packet, serial_port):
    """Sends a packet and waits for a response."""
    # print("Writing {} ({})".format(packet, time.time()))
    # print("data", packet.to_bytes())
    serial_port.write(packet.to_bytes())
    if isinstance(packet, codebug_tether.packets.GetPacket):
        # just read 1 byte
        return struct.unpack('B', serial_port.read(1))[0]

    elif (isinstance(packet, codebug_tether.packets.SetPacket) or
          isinstance(packet, codebug_tether.packets.SetBulkPacket)):
        # just read 1 byte
        b = struct.unpack('B', serial_port.read(1))[0]
        assert (b == codebug_tether.packets.AckPacket.ACK_BYTE)

    elif isinstance(packet, codebug_tether.packets.GetBulkPacket):
        return struct.unpack('B'*packet.length,
                             serial_port.read(packet.length))
