########
Examples
########

Basics
======

::

    >>> import codebug_tether

    >>> codebug = codebug_tether.CodeBug()  # create a CodeBug object

    >>> codebug.set_pixel(2, 1, 1)  # turn on the LED at (2, 1)
    >>> codebug.set_pixel(0, 0, 0)  # turn off the LED at (0, 0)
    >>> codebug.get_pixel(0, 1)     # return the LED state at (0, 1)
    1

    >>> codebug.clear()  # turn off all LEDs

    >>> codebug.set_row(0, 5)        # set row 0 to 5  (binary: 00101)
    >>> codebug.set_row(1, 0x1a)     # set row 1 to 26 (binary: 11010)
    >>> codebug.set_row(2, 0b10101)  # set row 2 to 21 (binary: 10101)
    >>> bin(codebug.get_row(2))
    '0b10101'

    >>> codebug.set_col(0, 0x1f)  # turn on all LEDs in column 0
    >>> codebug.get_col(0)
    31

    >>> codebug.get_input('A')  # returns the state of button 'A'
    0
    >>> codebug.get_input(0)  # returns the state of input 0
    0

    >>> codebug.set_leg_io(0, 0)  # set leg 0 to output
    >>> codebug.set_output(0, 1)  # turn leg 0 'on' (1)


.. note:: You can specify a different serial device for CodeBug by passing
          the class a string. For example, OSX users might use:
          ``codebug = codebug_tether.CodeBug('/dev/tty.USBmodem')``.


Sprites
=======
You can use the sprites library to quickly draw things on CodeBug's display.

::

    >>> import codebug_tether
    >>> import codebug_tether.sprite

    >>> # create a 3x3 square with the middle pixel off
    >>> square_sprite = codebug_tether.sprite.Sprite(3, 3)
    >>> square_sprite.set_row(0, 0b111)
    >>> square_sprite.set_row(1, 0b101)
    >>> square_sprite.set_row(2, 0b111)

    >>> # draw it in the middle of CodeBug
    >>> codebug = codebug_tether.CodeBug()
    >>> codebug.draw_sprite(1, 1, square_sprite)

    >>> # write some text
    >>> message = codebug_tether.sprite.StringSprite('Hello CodeBug!')
    >>> codebug.draw_sprite(0, 0, message)
    >>> # move it along
    >>> codebug.draw_sprite(-2, 0, message)


Colour Tail
===========
You can control Colour Tails (WS2812's) attached to CodeBug. By default,
ColourTails attach to the CS pin on the extension header. You can also
configure ColourTails to be driven from leg 0.

::

    >>> import codebug_tether
    >>> import codebug_tether.colourtail

    >>> codebug = codebug_tether.CodeBug()
    >>> colourtail = codebug_tether.colourtail.CodeBugColourTail(codebug)

    >>> # draw arrow pointing to the Colour Tail
    >>> codebug.set_row(4, 0b00100)
    >>> codebug.set_row(3, 0b00100)
    >>> codebug.set_row(2, 0b10101)
    >>> codebug.set_row(1, 0b01110)
    >>> codebug.set_row(0, 0b00100)

    >>> # initialise the colourtail (using EXT_CS pin)
    >>> colourtail.init()
    >>> colourtail.set_pixel(0, 255, 0, 0)  # red
    >>> colourtail.set_pixel(1, 0, 255, 0)  # green
    >>> colourtail.set_pixel(2, 0, 0, 255)  # blue
    >>> colourtail.update()  # turn on the LEDs

    >>> # initialise the colourtail (using LEG_0 pin)
    >>> colourtail.init(use_leg_not_cs=True)
    >>> colourtail.set_pixel(0, 255, 0, 0)  # red
    >>> colourtail.set_pixel(1, 255, 0, 0)  # red
    >>> colourtail.set_pixel(2, 0, 255, 0)  # green
    >>> colourtail.set_pixel(3, 0, 255, 0)  # green
    >>> colourtail.set_pixel(4, 0, 0, 255)  # blue
    >>> colourtail.set_pixel(5, 0, 0, 255)  # blue
    >>> colourtail.update()  # turn on the LEDs


Extension Header
================
You can use the extension header to drive SPI and I2C buses.

.. DANGER::
   Powering CodeBug from 5V USB means that devices connected to the
   extension header will also be powered with 5V USB.
   DO NOT USE THIS TO POWER DEVICES WHICH REQUIRE LESS THAN 5V.

Connect your SPI/I2C device onto the SPI/I2C lines::

    +                                +
     +        Back of CodeBug       +
      +                            +
       +--------------------------+
       | CodeBug Extension Header |
       +--------------------------+
        |    |    |    |    |    |
        CS  GND  SDO  SCL SDI/A VCC

    +----------+---------------------+
    | Pin Name | Function            |
    +----------+---------------------+
    | CS       | Chip Select         |
    | GND      | Ground (0v)         |
    | SDO      | SPI MOSI            |
    | SCL      | SPI/I2C Clock       |
    | SDI/A    | SPI MISO / I2C data |
    | VCC      | V+ (3V3, 5V)        |
    +----------+---------------------+

You can configure the extension header mode with the following methods::

    >>> import codebug_tether

    >>> codebug = codebug_tether.CodeBug()

    >>> codebug.config_extension_spi()  # configure extension as SPI
    >>> codebug.config_extension_i2c()  # configure extension as I2C
    >>> codebug.config_extension_io()   # reset extension as normal I/O

SPI
---
::

    >>> import codebug_tether

    >>> codebug = codebug_tether.CodeBug()
    >>> codebug.config_extension_spi()

    >>> # send three bytes (get three bytes back -- SPI is duplex)
    >>> codebug.spi_transaction(bytes(0x12, 0x34, 0x56))
    b'\xff\xff\xff'


I2C
::

    >>> import codebug_tether
    >>> from codebug_tether.i2c import (reading, writing)
    >>>
    >>> # example I2C address
    >>> i2c_addr = 0x1C
    >>>
    >>> # setup
    >>> codebug = codebug_tether.CodeBug()
    >>> codebug.config_extension_i2c()

Single byte read transaction (read reg 0x12)::

    >>> codebug.i2c_transaction(writing(i2c_addr, 0x12), # reg addr
                                reading(i2c_addr, 1))    # read 1 reg
    (42,)

Multiple byte read transaction (read regs 0x12-0x17)::

    >>> codebug.i2c_transaction(writing(i2c_addr, 0x12), # reg addr
                                reading(i2c_addr, 6))    # read 6 reg
    (65, 87, 47, 91, 43, 60)

Single byte write transaction (write value 0x34 to reg 0x12)::

    >>> codebug.i2c_transaction(writing(i2c_addr, 0x12, 0x34))

Multiple byte write transaction (write values 0x34, 0x56, 0x78 to reg 0x12)::

    >>> codebug.i2c_transaction(
            writing(i2c_addr, 0x12, 0x34, 0x56, 0x78))
