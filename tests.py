#!/usr/bin/env python3
# import os
# import sys
# parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, parentdir)
import time
import serial
import struct
import unittest
from codebug_tether.core import (CodeBug, CHANNEL_INDEX_IO_DIRECTION)
from codebug_tether.sprites import (Sprite, StringSprite)


class TestCodeBug(unittest.TestCase):

    def setUp(self):
        self.codebug = CodeBug()

    def test_get_input(self):
        # configure as inputs
        for i in range(7):
            self.codebug.set_leg_io(i, 1)
        # and just print them
        for i in ['A', 'B'] + list(range(8)):
            print("Input {} is {}".format(i, self.codebug.get_input(i)))

    def test_set_output(self):
        num_outputs = 8
        for i in range(num_outputs):
            self.codebug.set_leg_io(i, 0)  # set to output
            self.codebug.set_output(i, 1)  # set to ON

        # check that they are all on
        for i in range(num_outputs):
            self.assertEqual(self.codebug.get_output(i), 1)

        # then turn off again
        for i in range(num_outputs):
            self.codebug.set_output(i, 0)  # set to OFF

    def test_set_leg_io(self):
        self.codebug.set_leg_io(0, 0)
        self.codebug.set_leg_io(1, 1)
        self.codebug.set_leg_io(2, 0)
        self.codebug.set_leg_io(3, 1)
        self.codebug.set_leg_io(4, 0)
        self.codebug.set_leg_io(5, 1)
        self.codebug.set_leg_io(6, 0)
        self.codebug.set_leg_io(7, 1)
        value = struct.unpack('B',
                              self.codebug.get(CHANNEL_INDEX_IO_DIRECTION))[0]
        self.assertEqual(value, 0xAA)

        self.codebug.set_leg_io(0, 1)
        self.codebug.set_leg_io(1, 0)
        self.codebug.set_leg_io(2, 1)
        self.codebug.set_leg_io(3, 0)
        self.codebug.set_leg_io(4, 1)
        self.codebug.set_leg_io(5, 0)
        self.codebug.set_leg_io(6, 1)
        self.codebug.set_leg_io(7, 0)
        value = struct.unpack('B',
                              self.codebug.get(CHANNEL_INDEX_IO_DIRECTION))[0]
        self.assertEqual(value, 0x55)

        # safely back to inputs
        for i in range(7):
            self.codebug.set_leg_io(i, 1)

    def test_clear(self):
        self.codebug.clear()
        rows = struct.unpack('B'*5, self.codebug.get_bulk(0, 5))
        self.assertEqual(rows, (0,)*5)

    def test_set_row(self):
        for test_value in (0x0A, 0x15):
            for i in range(5):
                self.codebug.set_row(i, test_value)
            rows = self.codebug.get_bulk(0, 5)
            self.assertEqual(rows, bytes((test_value,)*5))
        self.codebug.clear()

    def test_get_row(self):
        for test_value in (0x0A, 0x15):
            self.codebug.set_bulk(0, (test_value,)*5)
            for i in range(5):
                self.assertEqual(self.codebug.get_row(i), test_value)
        self.codebug.clear()

    def test_set_col(self):
        for i in range(5):
            self.codebug.set_col(i, 0x0A)
        rows = struct.unpack('B'*5, self.codebug.get_bulk(0, 5))
        self.assertEqual(rows, (0x00, 0x1F, 0x00, 0x1F, 0x00))
        self.codebug.clear()

        for i in range(5):
            self.codebug.set_col(i, 0x15)
        rows = struct.unpack('B'*5, self.codebug.get_bulk(0, 5))
        self.assertEqual(rows, (0x1F, 0x00, 0x1F, 0x00, 0x1F))
        self.codebug.clear()

    def test_get_col(self):
        self.codebug.set_bulk(0, (0x00, 0x1F, 0x00, 0x1F, 0x00))
        for i in range(5):
            self.assertEqual(self.codebug.get_col(i), 0x0A)
        self.codebug.clear()
        self.codebug.set_bulk(0, (0x1F, 0x00, 0x1F, 0x00, 0x1F))
        for i in range(5):
            self.assertEqual(self.codebug.get_col(i), 0x15)
        self.codebug.clear()

    def test_set_pixel(self):
        self.codebug.clear()
        for y in range(5):
            for x in range(5):
                self.codebug.set_pixel(x, y, 1)
                value = struct.unpack('B', self.codebug.get(y))[0]
                self.assertEqual(value, 1 << (4-x))
                self.codebug.set_pixel(x, y, 0)

    def test_get_pixel(self):
        self.codebug.clear()
        for y in range(5):
            for x in range(5):
                for i in range(2):
                    self.codebug.set_pixel(x, y, i)
                    get_value = self.codebug.get_pixel(x, y)
                    self.assertEqual(get_value, i)

    def test_get_set_buffer(self):
        v = bytes(range(255))
        self.codebug.set_buffer(0, v)
        self.assertEqual(self.codebug.get_buffer(0, len(v)), v)
        v = bytes(range(100))
        self.codebug.set_buffer(0, v, 100)
        self.assertEqual(self.codebug.get_buffer(0, 255),
                         bytes(range(100))+bytes(range(100))+bytes(range(100+100, 255)))
        self.assertEqual(self.codebug.get_buffer(0, 101, 100),
                         bytes(range(100))+bytes((range(255)[200],)))

    def test_draw_sprite(self):
        self.codebug.clear()

        def fill_sprite(s):
            for x in range(s.width):
                for y in range(s.height):
                    s.set_pixel(x, y, 1)

        sprite = Sprite(4, 4)
        fill_sprite(sprite)

        self.codebug.draw_sprite(0, 0, sprite)
        self.assertEqual(self.codebug.get_row(4), 0x00)
        self.assertEqual(self.codebug.get_row(3), 0x1E)
        self.assertEqual(self.codebug.get_row(2), 0x1E)
        self.assertEqual(self.codebug.get_row(1), 0x1E)
        self.assertEqual(self.codebug.get_row(0), 0x1E)

        self.codebug.draw_sprite(1, 1, sprite)
        self.assertEqual(self.codebug.get_row(4), 0x0F)
        self.assertEqual(self.codebug.get_row(3), 0x0F)
        self.assertEqual(self.codebug.get_row(2), 0x0F)
        self.assertEqual(self.codebug.get_row(1), 0x0F)
        self.assertEqual(self.codebug.get_row(0), 0x00)

        sprite = Sprite(2, 3)
        fill_sprite(sprite)
        self.codebug.draw_sprite(0, 0, sprite)
        self.assertEqual(self.codebug.get_row(4), 0x00)
        self.assertEqual(self.codebug.get_row(3), 0x00)
        self.assertEqual(self.codebug.get_row(2), 0x18)
        self.assertEqual(self.codebug.get_row(1), 0x18)
        self.assertEqual(self.codebug.get_row(0), 0x18)

        sprite = Sprite(3, 3)
        fill_sprite(sprite)
        sprite.set_pixel(1, 2, 0) # key the sprite

        self.codebug.draw_sprite(0, 0, sprite)
        self.assertEqual(self.codebug.get_row(4), 0x00)
        self.assertEqual(self.codebug.get_row(3), 0x00)
        self.assertEqual(self.codebug.get_row(2), 0x14)
        self.assertEqual(self.codebug.get_row(1), 0x1C)
        self.assertEqual(self.codebug.get_row(0), 0x1C)

        self.codebug.draw_sprite(2, 2, sprite)
        self.assertEqual(self.codebug.get_row(4), 0x05)
        self.assertEqual(self.codebug.get_row(3), 0x07)
        self.assertEqual(self.codebug.get_row(2), 0x07)
        self.assertEqual(self.codebug.get_row(1), 0x00)
        self.assertEqual(self.codebug.get_row(0), 0x00)

        hello_str = StringSprite('Hello!')
        self.codebug.draw_sprite(0, 0, hello_str)
        self.assertEqual(self.codebug.get_row(4), 0x12)
        self.assertEqual(self.codebug.get_row(3), 0x12)
        self.assertEqual(self.codebug.get_row(2), 0x1E)
        self.assertEqual(self.codebug.get_row(1), 0x12)
        self.assertEqual(self.codebug.get_row(0), 0x12)
        self.codebug.draw_sprite(-7, 0, hello_str)
        self.assertEqual(self.codebug.get_row(4), 0x03)
        self.assertEqual(self.codebug.get_row(3), 0x11)
        self.assertEqual(self.codebug.get_row(2), 0x19)
        self.assertEqual(self.codebug.get_row(1), 0x01)
        self.assertEqual(self.codebug.get_row(0), 0x1B)


class TestSprites(unittest.TestCase):

    def test_string_sprite(self):
        expected = [[1, 1, 1, 1, 1],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 0, 0],
                    [1, 1, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 1, 1, 0, 0],
                    [1, 0, 1, 1, 0],
                    [1, 0, 1, 1, 0],
                    [1, 0, 1, 0, 0],
                    [0, 0, 0, 0, 0],
                    [1, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [1, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 1, 1, 0, 0],
                    [1, 0, 0, 1, 0],
                    [1, 0, 0, 1, 0],
                    [0, 1, 1, 0, 0],
                    [0, 0, 0, 0, 0]]
        s = StringSprite("hello")
        self.assertEqual(s.pixel_state, expected)

    def test_rotate90(self):

        def fill_sprite(s):
            for x in range(s.width):
                for y in range(s.height):
                    s.set_pixel(x, y, 1)

        s = Sprite(5, 5)
        # key the sprite so that looks like this:
        # 1 1 0 1 1
        # 1 1 0 1 1
        # 1 1 1 1 0
        # 1 1 1 1 1
        # 1 1 1 1 1
        fill_sprite(s)
        s.set_pixel(2, 4, 0)
        s.set_pixel(2, 3, 0)
        s.set_pixel(4, 2, 0)
        expected = [[1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 0, 0],
                    [1, 1, 1, 1, 1],
                    [1, 1, 0, 1, 1]]
        self.assertEqual(s.pixel_state, expected)

        # rotate 90deg
        s2 = s.clone()
        s2.rotate90(1)
        expected = [[1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [0, 1, 1, 1, 1],
                    [1, 1, 0, 1, 1],
                    [1, 1, 0, 1, 1]]
        self.assertEqual(s2.pixel_state, expected)

        # rotate 180deg
        s2 = s.clone()
        s2.rotate90(2)
        expected = [[1, 1, 0, 1, 1],
                    [1, 1, 1, 1, 1],
                    [0, 0, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1]]
        self.assertEqual(s2.pixel_state, expected)

        # rotate 270deg
        s2 = s.clone()
        s2.rotate90(3)
        expected = [[1, 1, 0, 1, 1],
                    [1, 1, 0, 1, 1],
                    [1, 1, 1, 1, 0],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1]]
        self.assertEqual(s2.pixel_state, expected)

    def test_invert(self):

        def fill_sprite(s):
            for x in range(s.width):
                for y in range(s.height):
                    s.set_pixel(x, y, 1)

        s = Sprite(5, 5)
        # key the sprite so that looks like this:
        # 1 1 0 1 1
        # 1 1 0 1 1
        # 1 1 1 1 0
        # 1 1 1 1 1
        # 1 1 1 1 1
        fill_sprite(s)
        s.set_pixel(2, 4, 0)
        s.set_pixel(2, 3, 0)
        s.set_pixel(4, 2, 0)
        expected = [[1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 0, 0],
                    [1, 1, 1, 1, 1],
                    [1, 1, 0, 1, 1]]
        self.assertEqual(s.pixel_state, expected)

        s2 = s.clone()
        s2.invert_vertical()
        expected = [[1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [0, 0, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 0, 1, 1]]
        self.assertEqual(s2.pixel_state, expected)

        s2 = s.clone()
        s2.invert_horizontal()
        expected = [[1, 1, 0, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 0, 0],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1]]
        self.assertEqual(s2.pixel_state, expected)


if __name__ == "__main__":
    unittest.main()
