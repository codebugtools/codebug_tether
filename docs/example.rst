########
Examples
########

Basic usage
===========

::

    >>> import codebug_tether

    >>> codebug = codebug_tether.CodeBug()  # instantiate a CodeBug object

    >>> codebug.set_row(0, 5)        # set row 0 to 5  (binary: 00101)
    >>> codebug.set_row(1, 0x1a)     # set row 1 to 26 (binary: 11010)
    >>> codebug.set_row(2, 0b10101)  # set row 2 to 21 (binary: 10101)
    >>> bin(codebug.get_row(2))
    '0b10101'

    >>> codebug.clear()  # turn off all LEDs

    >>> codebug.set_col(0, 0x1f)  # turn on all LEDs in column 0
    >>> codebug.get_col(0)
    31

    >>> codebug.set_led(2, 1, 1)  # turn on the LED at (2, 1)
    >>> codebug.set_led(0, 0, 0)  # turn off the LED at (0, 0)
    >>> codebug.get_led(0, 1)     # return the LED state at (0, 1)
    1

    >>> codebug.get_input('A')  # returns the state of button 'A'
    0
    >>> codebug.get_input(0)  # returns the state of input 0
    0

    >>> msg = "Hello, CodeBug!"
    >>> codebug.write_text(0, 0, msg)  # write a message at (0, 0)
    >>> codebug.write_text(-3, 0, msg, direction="right")
    >>> codebug.write_text(0, 0, msg, direction="down")  # message going down

.. note:: You can specify a different serial device for CodeBug by passing
          the class a string. For example, OSX users might use:
          ``codebug = codebug_tether.CodeBug('/dev/tty.USBmodem')``.
