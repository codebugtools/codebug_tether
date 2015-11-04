import os
import time
import serial
import struct
from codebug_tether.serial_channel_device import SerialChannelDevice
from codebug_tether.char_map import (char_map, StringSprite)


DEFAULT_SERIAL_PORT = '/dev/ttyACM0'
OUTPUT_CHANNEL_INDEX = 5
LEG_INPUT_CHANNEL_INDEX = 6
BUTTON_INPUT_CHANNEL_INDEX = 7
IO_DIRECTION_CHANNEL = 8
# Pullups for Port B (Register: WPUB)
PULLUP_CHANNEL_INDEX = 9


class CodeBug(SerialChannelDevice):
    """Manipulates CodeBug over a USB serial connection."""
    # Adds fancy, easy-to-use features to CodeBugRaw.

    def __init__(self, serial_port=DEFAULT_SERIAL_PORT):
        super(CodeBug, self).__init__(serial.Serial(serial_port, timeout=2))

    def _int_input_index(self, input_index):
        """Returns an integer input index."""
        # 'A' is 8, 'B' is 9
        if isinstance(input_index, str):
            input_index = 8 if 'a' in input_index.lower() else 9
        return input_index

    def get_input(self, input_index):
        """Returns the state of an input. You can use 'A' and 'B' to
        access buttons A and B.

            >>> codebug = CodeBug()
            >>> codebug.get_input('A')  # switch A is pressed
            1
            >>> codebug.get_input(0)  # assuming leg 0 is connected to GND
            0
            >>> codebug.get_input(4)  # extension I/O pin 4 is connected to GND
            0

        """
        input_index = self._int_input_index(input_index)
        if input_index > 7:
            channel_index = BUTTON_INPUT_CHANNEL_INDEX
            input_index -= 8
        else:
            channel_index = LEG_INPUT_CHANNEL_INDEX
        return self.get_channel_bit(channel_index, input_index)

    def set_pullup(self, input_index, state):
        """Sets the state of the input pullups. Turn off to enable touch
        sensitive pads (bridge GND and input with fingers).

            >>> codebug = CodeBug()
            >>> codebug.set_pullup(0, 1)  # input pad 0 <10K OHMS
            >>> codebug.set_pullup(2, 0)  # input pad 2 <22M OHMS touch sensitive

        """
        input_index = self._int_input_index(input_index)
        self.set_channel_bit(PULLUP_CHANNEL_INDEX, input_index, direction)

    def set_output(self, output_index, state):
        """Sets the output index to state."""
        self.set_channel_bit(OUTPUT_CHANNEL_INDEX, output_index, state)

    def get_output(self, output_index):
        """Returns the state of the output at index."""
        return self.get_channel_bit(OUTPUT_CHANNEL_INDEX, output_index)

    def set_leg_io(self, leg_index, direction):
        """Sets the I/O direction of the leg at index."""
        self.set_channel_bit(IO_DIRECTION_CHANNEL, leg_index, direction)

    def clear(self):
        """Clears the pixels on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.clear()

        """
        self.set_bulk(0, [0]*5)

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
        return self.get(min(row, 5))  # only row channels

    def set_col(self, col, val):
        """Sets an entire column of PIXELs on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.set_col(0, 0b10101)

        """
        rows = self.get_bulk(0, 5)
        # clear col
        rows = [rows[i] & (0xff ^ (1 << (4-col))) for i in range(5)]
        # set cols
        val_bits = [(val >> i) & 1 for i in reversed(range(5))]
        rows = [rows[i] | (bit << (4-col)) for i, bit in enumerate(val_bits)]
        self.set_bulk(0, rows)

    def get_col(self, col):
        """Returns an entire column of PIXELs on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.get_col(0)
            21

        """
        rows = self.get_bulk(0, 5)
        c = 0
        for row in rows:
            c <<= 1
            col_bit = 1 & (row >> (4 - col))
            c |= col_bit
        return c

    def set_pixel(self, x, y, state):
        """Sets an PIXEL on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.set_pixel(0, 0, 1)

        """
        channel = min(y, 5)  # only row channels
        bit_index = 4 - x
        self.set_channel_bit(channel, bit_index, state)

    def get_pixel(self, x, y):
        """Returns the state of an PIXEL on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.get_pixel(0, 0)
            1

        """
        return (self.get(min(y, 5)) >> (4 - x)) & 0x1

    def write_text(self, x, y, message, direction="right", clear_first=True):
        """Writes some text on CodeBug at PIXEL (x, y).

            >>> codebug = CodeBug()
            >>> codebug.write_text(0, 0, 'Hello, CodeBug!')

        """
        rows = [0] * 5
        s = StringSprite(message, direction)

        for row_i, row in enumerate(s.pixel_state):
            if (row_i - y) >= 0 and (row_i - y) <= 4:
                code_bug_pixel_row = 0
                for col_i, state in enumerate(row):
                    if col_i + x >= 0 and col_i + x <= 4:
                        code_bug_pixel_row |= state << 4 - (col_i + x)
                rows[4-row_i+y] = code_bug_pixel_row

        if clear_first:
            self.set_bulk(0, rows)
        else:
            self.or_mask_bulk(0, rows)
