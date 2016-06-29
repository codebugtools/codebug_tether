from __future__ import print_function
import time
import serial
import struct
from .i2c import *
from .serial_channel_device import SerialChannelDevice
from .platform import get_platform_serial_port


DEFAULT_SERIAL_PORT = get_platform_serial_port()

IO_DIGITAL_OUTPUT = 0
IO_DIGITAL_INPUT = 1
IO_ANALOGUE_INPUT = 2
IO_PWM_OUTPUT = 3

# CHANNEL_INDEX_ROW_0 = 0
# CHANNEL_INDEX_ROW_1 = 1
# CHANNEL_INDEX_ROW_2 = 2
# CHANNEL_INDEX_ROW_3 = 3
# CHANNEL_INDEX_ROW_4 = 4
(CHANNEL_INDEX_OUTPUT,
 CHANNEL_INDEX_LEG_INPUT,
 CHANNEL_INDEX_BUTTON_INPUT,
 CHANNEL_INDEX_ANALOGUE_CONF,
 CHANNEL_INDEX_ANALOGUE_INPUT,
 CHANNEL_INDEX_IO_DIRECTION_LEGS,
 CHANNEL_INDEX_IO_DIRECTION_EXT,
 CHANNEL_INDEX_PULLUPS,
 CHANNEL_INDEX_EXT_CONF,
 CHANNEL_INDEX_SPI_RATE,
 CHANNEL_INDEX_SPI_LENGTH,
 CHANNEL_INDEX_SPI_CONTROL,
 CHANNEL_INDEX_I2C_ADDR,
 CHANNEL_INDEX_I2C_LENGTH,
 CHANNEL_INDEX_I2C_CONTROL,
 CHANNEL_INDEX_UART_RX_OFFSET,
 CHANNEL_INDEX_UART_RX_LENGTH,
 CHANNEL_INDEX_UART_TX_OFFSET,
 CHANNEL_INDEX_UART_TX_LENGTH,
 CHANNEL_INDEX_UART_CONTROL,
 CHANNEL_INDEX_COLOURTAIL_LENGTH,
 CHANNEL_INDEX_COLOURTAIL_CONTROL,
 CHANNEL_INDEX_PWM_CONF_0,
 CHANNEL_INDEX_PWM_CONF_1,
 CHANNEL_INDEX_PWM_CONF_2,
 CHANNEL_INDEX_SERVO_PULSE_LENGTH,
 CHANNEL_INDEX_SERVO_CONF) = range(5, 32)

EXTENSION_CONF_IO = 0x01
EXTENSION_CONF_SPI = 0x02
EXTENSION_CONF_I2C = 0x04
EXTENSION_CONF_UART = 0x08

UART_TX_BUFFER_INDEX = 0
UART_RX_BUFFER_INDEX = 1

UART_TX_GO_BUSY_MASK = 0x01
UART_RX_GO_BUSY_MASK = 0x02
UART_BAUD_300 = 0 << 2
UART_BAUD_1200 = 1 << 2
UART_BAUD_2400 = 2 << 2
UART_BAUD_9600 = 3 << 2
UART_BAUD_10417 = 4 << 2
UART_BAUD_19200 = 5 << 2
UART_BAUD_57600 = 6 << 2
UART_BAUD_115200 = 7 << 2

UART_DEFAULT_BAUD = 9600

T2_PS_1_1 = 0
T2_PS_1_4 = 1
T2_PS_1_16 = 2


class InvalidBaud(Exception):
    pass


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

    def read_analogue(self, leg_index):
        """Reads the analogue value of the leg at leg_index. The leg must
        first be configured as an analogue input. For example:

            >>> codebug = CodeBug()
            >>> codebug.set_leg_io(0, IO_ANALOG_INPUT)
            >>> codebug.read_analogue(0)
            128

        """
        # set which leg to read (and do the read)
        self.set(CHANNEL_INDEX_ANALOGUE_CONF, leg_index)
        # return the value
        analogue_value = self.get(CHANNEL_INDEX_ANALOGUE_INPUT)
        return struct.unpack('B', analogue_value)[0]

    def set_pullup(self, input_index, state):
        """Sets the state of the input pullups. Turn off to enable touch
        sensitive pads (bridge GND and input with fingers).

            >>> codebug = CodeBug()
            >>> codebug.set_pullup(0, 1)  # input pad 0 <10K OHMS
            >>> codebug.set_pullup(2, 0)  # input pad 2 <22M OHMS touch sensitive

        """
        input_index = self._int_input_index(input_index)
        self.set_bit(CHANNEL_INDEX_PULLUPS, input_index, state)

    def set_output(self, output_index, state):
        """Sets the output index to state."""
        self.set_bit(CHANNEL_INDEX_OUTPUT, output_index, state)

    def get_output(self, output_index):
        """Returns the state of the output at index."""
        return self.get_bit(CHANNEL_INDEX_OUTPUT, output_index)

    def set_leg_io(self, leg_index, direction):
        """Sets the I/O direction of the leg at index. For example:

            >>> codebug = CodeBug()
            >>> codebug.set_leg_io(0, IO_DIGITAL_OUTPUT)
            >>> codebug.set_leg_io(0, IO_PWM_OUTPUT)
            >>> codebug.set_leg_io(1, IO_DIGITAL_INPUT)
            >>> codebug.set_leg_io(2, IO_ANALOG_INPUT)

        """
        if leg_index < 4:
            clear_mask = 0xff ^ (0b11 << leg_index * 2)
            direction_mask = (0b11 & direction) << leg_index * 2
            self.and_mask(CHANNEL_INDEX_IO_DIRECTION_LEGS, clear_mask)
            self.or_mask(CHANNEL_INDEX_IO_DIRECTION_LEGS, direction_mask)
        else:
            ext_index = leg_index - 4
            clear_mask = 0b11 << ext_index * 2
            direction_mask = (0b11 & direction) << ext_index * 2
            self.and_mask(CHANNEL_INDEX_IO_DIRECTION_EXT, clear_mask)
            self.or_mask(CHANNEL_INDEX_IO_DIRECTION_EXT, direction_mask)

    def pwm_on(self, t2_prescale, full_period, on_period):
        """Turns on the PWM generator with the given settings.

        Args:
            t2_prescale: One of T2_PS_1_1, T2_PS_1_4, T2_PS_1_16
                Scales down the 12MHz instruction clock by
                1, 4 or 16.
            full_period: 8-bit value - which is scaled up to 10-bits
                (<< 2) - to which timer 2 will count up to
                before resetting PWM output to 1.
            on_period: 10-bit value to which timer 2 will count up to
                before setting PWM output to 0. Use this with
                full_period to control duty cycle. For example:

                # 12MHz / 16 with 50% duty cycle
                codebug.pwm_on(T2_PS_1_16, 0xff, 0x200)

        """
        # full period
        self.set(CHANNEL_INDEX_PWM_CONF_0, full_period)
        self.set(CHANNEL_INDEX_PWM_CONF_1, on_period & 0xff)
        go_busy = 1
        top_two_bit_on_period = (on_period >> 8) & 0b11
        conf = go_busy << 4 | t2_prescale << 2 | top_two_bit_on_period
        self.set(CHANNEL_INDEX_PWM_CONF_2, conf)

    def pwm_freq(self, frequency):
        """Turns on the PWM generator with the given frequency. For example:

            >>> codebug = CodeBug()
            >>> codebug.set_leg_io(0, IO_PWM_OUTPUT)
            >>> codebug.pwm_freq(1046)
            >>> time.sleep(2)
            >>> codebug.pwm_off()

        """
        # calculate pwm settings
        # 12MHz / 16 = 750k ticks per second
        full_period = int(750000 / frequency) - 1
        # for 50% duty cycle: shift up by 2 then /(2 i.e. 50% duty cycle)
        # on_period = (full_period << 2) / 2;
        # this is quicker
        on_period = full_period << 1
        self.pwm_on(T2_PS_1_16, full_period, on_period)

    def pwm_off(self):
        """Turns off the PWM generator."""
        go_busy_off_mask = 0xff ^ (1 << 4)
        self.and_mask(CHANNEL_INDEX_PWM_CONF_2, go_busy_off_mask)

    def servo_set(self, servo_index, pulse_length):
        """Set the servo at servo_index to pulse_length. Make sure that
        the leg is configured as IO_DIGITAL_OUTPUT (0).
        """
        pulse_length_msb = 0xff & (pulse_length >> 8)
        pulse_length_lsb = 0xff & pulse_length
        conf_msb = ((servo_index & 0xf) << 4) | 0x01
        conf_lsb = ((servo_index & 0xf) << 4) | 0x00
        self.set_bulk(CHANNEL_INDEX_SERVO_PULSE_LENGTH,
                      bytes([pulse_length_msb, conf_msb]))
        self.set_bulk(CHANNEL_INDEX_SERVO_PULSE_LENGTH,
                      bytes([pulse_length_lsb, conf_lsb]))

    def clear(self):
        """Clears the pixels on CodeBug.

            >>> codebug = CodeBug()
            >>> codebug.clear()

        """
        self.set_bulk(0, bytes([0]*5))

    def fill(self):
        """Sets all pixels on.

            >>> codebug = CodeBug()
            >>> codebug.fill()

        """
        self.set_bulk(0, bytes([0x1f]*5))

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
            for i, row in enumerate(cb_rows):
                self.or_mask(i, bytes(row))

    def scroll_sprite(self, sprite, interval=0.1, direction='L'):
        """Scrolls a sprite.

        Args:
            sprite: The sprite to scroll.
            interval: The time delay between each movement in seconds.
                (optional)
            direction: The direction of the scroll ('L', 'R', 'U', 'D').

        """
        direction = direction.upper()[0]  # only take the first char
        if direction == 'L':
            for i in range(sprite.width+5):
                self.draw_sprite(5-i, 0, sprite)
                time.sleep(interval)
        elif direction == 'D':
            for i in range(sprite.height+5):
                self.draw_sprite(0, 5-i, sprite)
                time.sleep(interval)
        elif direction == 'R':
            for i in reversed(range(sprite.width+5)):
                self.draw_sprite(5-i, 0, sprite)
                time.sleep(interval)
        elif direction == 'U':
            for i in reversed(range(sprite.height+5)):
                self.draw_sprite(0, 5-i, sprite)
                time.sleep(interval)

    def config_extension_io(self):
        self.set(CHANNEL_INDEX_EXT_CONF, EXTENSION_CONF_IO)

    def config_extension_spi(self):
        self.set(CHANNEL_INDEX_EXT_CONF, EXTENSION_CONF_SPI)

    def config_extension_i2c(self):
        self.set(CHANNEL_INDEX_EXT_CONF, EXTENSION_CONF_I2C)

    def config_extension_uart(self):
        self.set(CHANNEL_INDEX_EXT_CONF, EXTENSION_CONF_UART)

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
        self.set_buffer(0, bytes(list(data)))
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

        Args:
            messages: The I2C messages.
            add_stop_last_message: Adds stop flag to the last
                I2CMessage.
            interval: Adds delay of `interval` seconds between I2C
                messages.

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
            self.set_buffer(0, bytes(msg.data))
            # set the i2c address, length and control all in one go
            self.set_bulk(CHANNEL_INDEX_I2C_ADDR,
                          bytes([msg.address, msg.length, msg.control]))
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

    def _get_uart_control_baud(self, baud):
        """Returns UART control value for given baud rate. Will raise
        InvalidBaud exception if baud is invalid.
        """
        baud_control = {300: 0 << 2,
                        1200: 1 << 2,
                        2400: 2 << 2,
                        9600: 3 << 2,
                        10417: 4 << 2,
                        19200: 5 << 2,
                        57600: 6 << 2,
                        115200: 7 << 2}
        if baud not in baud_control:
            raise InvalidBaud('{} is not a valid baud rate (valid baud '
                'rates: {}).'.format(baud, tuple(baud_control.keys())))
        else:
            return baud_control[baud]

    def uart_set_baud(self, baud):
        self.set(CHANNEL_INDEX_UART_CONTROL, self._get_uart_control_baud(baud))

    def uart_tx(self, data_bytes, baud=UART_DEFAULT_BAUD):
        """Transmits data bytes over UART. Use this if you just want to
        send X amount of data. Be sure to configure the extension pins
        first. For example:

            >>> from codebug_tether import CodeBug
            >>> codebug = CodeBug()
            >>> codebug.config_extension_uart()
            >>> # send 0xAA, 0xBB over UART
            >>> codebug.uart_tx(bytes((0xAA, 0xBB)))
            >>> # send 0xAA, 0xBB over UART at 300 baud
            >>> codebug.uart_tx(bytes((0xAA, 0xBB)), baud=300)

        """
        self.uart_tx_set_buffer(data_bytes)
        self.uart_tx_start(len(data_bytes))

    def uart_tx_start(self, length, offset=0, baud=UART_DEFAULT_BAUD):
        """Transmits 'length' data bytes from UART buffer starting at
        'offset' over UART. Be sure to configure the extension pins
        first. For example, you might want to fill the buffer with two
        commands (0xAA and 0xBB) which are sent over UART and only send
        one at a time:

            >>> from codebug_tether import CodeBug
            >>> codebug = CodeBug()
            >>> codebug.config_extension_uart()
            >>> codebug.uart_tx_set_buffer(bytes((0xAA, 0xBB)))
            >>> codebug.uart_tx_start(1, offset=0)  # send 0xAA over UART
            >>> codebug.uart_tx_start(1, offset=1)  # send 0xBB over UART
            >>> # send 0xAA over UART at 300 baud
            >>> codebug.uart_tx_start(1, offset=0, baud=300)

        """
        control = self._get_uart_control_baud(baud) | UART_TX_GO_BUSY_MASK
        self.set_bulk(CHANNEL_INDEX_UART_TX_OFFSET,
                      bytes((offset, length, control)))

    def uart_tx_set_buffer(self, data_bytes, offset=0):
        """Add data_bytes to the UART buffer at offset."""
        self.set_buffer(UART_TX_BUFFER_INDEX, data_bytes, offset)

    def uart_rx_start(self, length, baud=UART_DEFAULT_BAUD, offset=0):
        """Begins receiving on the UART. RX will stop when length data is
        reached. Be sure to configure the extension pins first. For example

            >>> from codebug_tether import CodeBug
            >>> codebug = CodeBug()
            >>> codebug.config_extension_uart()
            >>> codebug.uart_rx_start(2)  # ready to receive 2B over UART
            >>> # wait until data ready (alternatively, sleep X seconds)
            >>> while not codebug.uart_rx_is_ready():
            ...     pass
            ...
            >>> codebug.uart_rx_get_buffer(2)  # read out the two bytes

        """
        self.set_bulk(CHANNEL_INDEX_UART_RX_OFFSET, bytes((offset, length)))
        self.set(CHANNEL_INDEX_UART_CONTROL,
                 self._get_uart_control_baud(baud) | UART_RX_GO_BUSY_MASK)

    def uart_rx_is_ready(self):
        """Returns True if the UART has finished receiving data."""
        uart_control = self.get(CHANNEL_INDEX_UART_CONTROL)[0]
        return uart_control & UART_RX_GO_BUSY_MASK == 0

    def uart_rx_get_buffer(self, length, offset=0):
        """Returns data bytes from UART buffer."""
        return self.get_buffer(UART_RX_BUFFER_INDEX, length, offset)


def scale(x, from_low, from_high, to_low, to_high):
    # Hardware can only do 16bit maths
    def limit(v):
        max_value = 0x7fff
        min_value = -0x8000
        return max(min_value, min(max_value, v))
    x, from_low, from_high, to_low, to_high = map(
        limit, (x, from_low, from_high, to_low, to_high))
    # do the scale
    from_delta = from_high - from_low
    x_offset = x - from_low
    to_delta = to_high - to_low
    new_x = int((x_offset * to_delta) / from_delta)
    return to_low + new_x
