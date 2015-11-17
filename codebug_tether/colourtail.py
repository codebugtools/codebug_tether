"""Colour tails interface for CodeBug."""
from collections import namedtuple
from codebug_tether.core import (CHANNEL_INDEX_COLOURTAIL_LENGTH,
                                 CHANNEL_INDEX_COLOURTAIL_CONTROL)


RGBPixel = namedtuple('RGBPixel', ['red', 'green', 'blue'])


class CodeBugColourTail():
    """CodeBugColourTail stores and sends RGB pixel values to a connected
    CodeBug Colour Tail (strip of WS2812s).

    You can use either the CS pin on the extension port or leg 0 to output
    colour tail value.
    """

    pixel_buffer = []

    def __init__(self, codebug, use_leg_not_cs=False):
        self.codebug = codebug
        self.use_leg_not_cs = use_leg_not_cs

    def get_pixel(self, index):
        return self.pixel_buffer[index]

    def set_pixel(self, index, red, green, blue):
        self.pixel_buffer[index] = RGBPixel(red=red, green=green, blue=blue)

    def update(self):
        codebug_buffer = [value
                          for pixel in self.pixel_buffer
                          for value in (pixel.red, pixel.blue, pixel.green)]
        self.codebug.set_buffer(0, codebug_buffer)
        self.codebug.set_channel(CHANNEL_INDEX_COLOURTAIL_LENGTH,
                                 len(codebug_buffer))
