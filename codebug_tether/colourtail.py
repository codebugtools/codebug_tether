"""Colour tails interface for CodeBug."""
from collections import namedtuple
from codebug_tether.core import (CHANNEL_INDEX_COLOURTAIL_LENGTH,
                                 CHANNEL_INDEX_COLOURTAIL_CONTROL)


# control
# bit 1
COLOURTAIL_CONTROL_GO_BUSY = 0x01
# bit 2
COLOURTAIL_CONTROL_INIT_NOT_UPDATE = 0x02
# bit 3-8 (init bits - only work when COLOURTAIL_CONTROL_INIT_NOT_UPDATE == 1)
COLOURTAIL_CONTROL_LEG0_NOT_CS = 0x04

PIXEL_BUFFER_SIZE = 50


RGBPixel = namedtuple('RGBPixel', ['red', 'green', 'blue'])


class CodeBugColourTail():
    """CodeBugColourTail stores and sends RGB pixel values to a connected
    CodeBug Colour Tail (strip of WS2812s).

    You can use either the CS pin on the extension port or leg 0 to output
    colour tail value.

    Example use:

        from codebug_tether import CodeBug
        from codebug_tether.colourtail import CodeBugColourTail

        codebug = CodeBug()
        colourtail = CodeBugColourTail(codebug)

        # using CS pin
        colourtail.init()
        colourtail.set_pixel(0, 255, 0, 0)  # red
        colourtail.set_pixel(1, 0, 255, 0)  # green
        colourtail.set_pixel(2, 0, 0, 255)  # blue
        colourtail.update()  # turn on the LEDs

        # use leg 0 instead
        colourtail.init(use_leg_0_not_cs=True)
        colourtail.update()

    You can set the pixel buffer manually like so:

        from codebug_tether import CodeBug
        from codebug_tether.colourtail import (CodeBugColourTail, RGBPixel)

        codebug = CodeBug()
        colourtail = CodeBugColourTail(codebug)

        # using CS pin
        colourtail.init()
        colourtail.pixel_buffer[0] = RGBPixel(255, 0, 0)
        colourtail.pixel_buffer[1] = RGBPixel(0, 255, 0)
        colourtail.pixel_buffer[1] = RGBPixel(0, 0, 255)
        colourtail.update()  # turn on the LEDs

    """

    pixel_buffer = [RGBPixel(0, 0, 0)]*PIXEL_BUFFER_SIZE

    def __init__(self, codebug):
        self.codebug = codebug

    def init(self, use_leg_0_not_cs=False):
        control = (COLOURTAIL_CONTROL_GO_BUSY |
                   COLOURTAIL_CONTROL_INIT_NOT_UPDATE)
        if use_leg_0_not_cs:
            control |= COLOURTAIL_CONTROL_LEG0_NOT_CS
        self.codebug.set(CHANNEL_INDEX_COLOURTAIL_CONTROL, control)

    def get_pixel(self, index):
        return self.pixel_buffer[index]

    def set_pixel(self, index, red, green, blue):
        self.pixel_buffer[index] = RGBPixel(red=red, green=green, blue=blue)

    def update(self):
        # WS2812 order is green, red, blue
        codebug_buffer = [value
                          for pixel in self.pixel_buffer[:PIXEL_BUFFER_SIZE]
                          for value in (pixel.green, pixel.red, pixel.blue)]
        control = COLOURTAIL_CONTROL_GO_BUSY
        self.codebug.set_buffer(0, bytes(codebug_buffer))
        self.codebug.set_bulk(CHANNEL_INDEX_COLOURTAIL_LENGTH,
                              bytes((len(self.pixel_buffer), control)))
