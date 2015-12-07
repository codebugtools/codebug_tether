import os
import time
import serial
import struct
from codebug_tether.i2c import *
from codebug_tether.serial_channel_device import SerialChannelDevice


DEFAULT_SERIAL_PORT = '/dev/ttyACM0'

CHANNEL_INDEX_OUTPUT = 5
CHANNEL_INDEX_LEG_INPUT = 6
CHANNEL_INDEX_BUTTON_INPUT = 7
CHANNEL_INDEX_IO_DIRECTION = 8
CHANNEL_INDEX_PULLUPS = 9
CHANNEL_INDEX_EXT_CONF = 10
CHANNEL_INDEX_SPI_RATE = 11
CHANNEL_INDEX_SPI_LENGTH = 12
CHANNEL_INDEX_SPI_CONTROL = 13
CHANNEL_INDEX_I2C_ADDR = 14
CHANNEL_INDEX_I2C_LENGTH = 15
CHANNEL_INDEX_I2C_CONTROL = 16
CHANNEL_INDEX_COLOURTAIL_LENGTH = 17
CHANNEL_INDEX_COLOURTAIL_CONTROL = 18

EXTENSION_CONF_IO = 0
EXTENSION_CONF_SPI = 1
EXTENSION_CONF_I2C = 2


class CodeBug(SerialChannelDevice):
    """Manipulates CodeBug over a USB serial connection."""

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
            channel_index = CHANNEL_INDEX_BUTTON_INPUT
            input_index -= 8
        else:
            channel_index = CHANNEL_INDEX_LEG_INPUT
        return self.get_bit(channel_index, input_index)

    def set_pullup(self, input_index, state):
        """Sets the state of the input pullups. Turn off to enable touch
        sensitive pads (bridge GND and input with fingers).

            >>> codebug = CodeBug()
            >>> codebug.set_pullup(0, 1)  # input pad 0 <10K OHMS
            >>> codebug.set_pullup(2, 0)  # input pad 2 <22M OHMS touch sensitive

        """
        input_index = self._int_input_index(input_index)
        self.set_bit(CHANNEL_INDEX_PULLUPS, input_index, direction)

    def set_output(self, output_index, state):
        """Sets the output index to state."""
        self.set_bit(CHANNEL_INDEX_OUTPUT, output_index, state)

    def get_output(self, output_index):
        """Returns the state of the output at index."""
        return self.get_bit(CHANNEL_INDEX_OUTPUT, output_index)

    def set_leg_io(self, leg_index, direction):
        """Sets the I/O direction of the leg at index."""
        self.set_bit(CHANNEL_INDEX_IO_DIRECTION, leg_index, direction)

    def clear(self):
        """Clears the pixels on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.clear()

        """
        self.set_bulk(0, [0]*5)

    def fill(self):
        """Sets all pixels on.

            >>> codebug = CodeBug()
            >>> codebug.fill()

        """
        self.set_bulk(0, [0x1f]*5)

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
        row = self.get(min(row, 5))  # only row channels
        return struct.unpack('B', row)[0]

    def set_col(self, col, val):
        """Sets an entire column of PIXELs on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.set_col(0, 0b10101)

        """
        rows = struct.unpack('B'*5, self.get_bulk(0, 5))
        # clear col
        rows = [rows[i] & (0xff ^ (1 << (4-col))) for i in range(5)]
        # set cols
        val_bits = [(val >> i) & 1 for i in reversed(range(5))]
        rows = [rows[i] | (bit << (4-col)) for i, bit in enumerate(val_bits)]
        self.set_bulk(0, bytes(rows))

    def get_col(self, col):
        """Returns an entire column of PIXELs on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.get_col(0)
            21

        """
        rows = struct.unpack('B'*5, self.get_bulk(0, 5))
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
        self.set_bit(channel, bit_index, state)

    def get_pixel(self, x, y):
        """Returns the state of an PIXEL on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.get_pixel(0, 0)
            1

        """
        channel = min(y, 5)
        bit_index = 4 - x
        return self.get_bit(channel, bit_index)

    def draw_sprite(self, x, y, sprite, clear_first=True):
        """Draws a sprite at (x, y) on CodeBug's 5x5 display."""
        cb_display_sprite = sprite.get_sprite(-x, -y, 5, 5)
        cb_rows = [cb_display_sprite.get_row(y)
                   for y in range(cb_display_sprite.height)]
        if clear_first:
            self.set_bulk(0, bytes(cb_rows))
        else:
            self.or_mask_bulk(0, bytes(cb_rows))

    def config_extension_io(self):
        self.set(CHANNEL_INDEX_EXT_CONF, EXTENSION_CONF_IO)

    def config_extension_spi(self):
        self.set(CHANNEL_INDEX_EXT_CONF, EXTENSION_CONF_SPI)

    def config_extension_i2c(self):
        self.set(CHANNEL_INDEX_EXT_CONF, EXTENSION_CONF_I2C)

    def spi_transaction(self,
                        data,
                        cs_idle_high=1,
                        input_sample_middle=1,
                        spi_mode=0):
        """Run an SPI transaction using the extensions pins. Be sure to
        configure the extension pins first.

        Example:

            >>> import codebug_tether
            >>>
            >>> # setup
            >>> codebug = codebug_tether.CodeBug()
            >>> codebug.config_extension_spi()
            >>>
            >>> # transaction
            >>> tx = bytes((0x01, 0x02, 0x03))  # transmit this data
            >>> rx = codebug.spi_transaction(tx)  # transaction returns data
            >>> print(rx)
            b'\xff\xff\xff'

        """
        # control channel
        spi_mode = (spi_mode & 0x03) << 3
        input_sample_middle = (input_sample_middle & 1) << 2
        cs_idle_high = (cs_idle_high & 1) << 1
        go = 0x01
        control = spi_mode | input_sample_middle | cs_idle_high | go
        # put data into the buffer
        self.set_buffer(0, list(data))
        # set the length and control channels in one go
        self.set_bulk(CHANNEL_INDEX_SPI_LENGTH, bytes([len(data), control]))
        # return data from buffer
        return self.get_buffer(0, len(data))

    def i2c_transaction(self,
                        *messages,
                        add_stop_last_message=True,
                        interval=0):
        """Run an I2C transaction using the extensions pins. Be sure to
        configure the extension pins first.

        :param add_stop_last_message: Adds stop flag to the last I2CMessage.
        :type add_stop_last_message: boolean
        :param interval: Adds delay of `interval` seconds between I2C messages.
        :type interval: interger

        Example:

            >>> import codebug_tether
            >>> from codebug_tether.i2c import (reading, writing)
            >>>
            >>> # example I2C address
            >>> i2c_addr = 0x1C
            >>>
            >>> # setup
            >>> codebug = codebug_tether.CodeBug()
            >>> codebug.config_extension_i2c()

        Single byte read transaction (read reg 0x12)

            >>> codebug.i2c_transaction(writing(i2c_addr, 0x12), # reg addr
                                        reading(i2c_addr, 1))    # read 1 reg
            (42,)

        Multiple byte read transaction (read regs 0x12-0x17)

            >>> codebug.i2c_transaction(writing(i2c_addr, 0x12), # reg addr
                                        reading(i2c_addr, 6))    # read 6 reg
            (65, 87, 47, 91, 43, 60)

        Single byte write transaction (write value 0x34 to reg 0x12)

            >>> codebug.i2c_transaction(writing(i2c_addr, 0x12, 0x34))

        Multiple byte write transaction
        (write values 0x34, 0x56, 0x78 to reg 0x12)

            >>> codebug.i2c_transaction(
                    writing(i2c_addr, 0x12, 0x34, 0x56, 0x78))

        """
        # Can't use a tuple here because `+=` inside `send_msg` implicitly
        # declares rx_buffer as a local variable (to send_msg).
        rx_buffer = list()

        def send_msg(msg):
            """Sends a single i2c message."""
            # print("send_msg")
            # print("address", hex(msg.address))
            # print("msg.data", msg.data)
            # print("length", msg.length)
            # print("control", bin(msg.control))
            # print()
            self.set_buffer(0, msg.data)
            # set the i2c address, length and control all in one go
            self.set_bulk(CHANNEL_INDEX_I2C_ADDR,
                          [msg.address, msg.length, msg.control])
            # if reading, add data to rx_buffer
            if msg.control & I2C_CONTROL_READ_NOT_WRITE:
                values = struct.unpack('B'*msg.length,
                                       self.get_buffer(0, msg.length))
                rx_buffer.extend(values)
            time.sleep(interval)

        if add_stop_last_message:
            # send all messages except for the last one
            for message in messages[:-1]:
                send_msg(message)

            # add stop control flag to the last message
            messages[-1].control |= I2C_CONTROL_STOP
            send_msg(messages[-1])

        else:
            # send all messages
            for message in messages:
                send_msg(message)

        return tuple(rx_buffer)
