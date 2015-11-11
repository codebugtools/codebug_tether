#!/usr/bin/env python3
# import os
# import sys
# parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, parentdir)
import time
import serial
import unittest
from codebug_tether.core import (CodeBug,
                                 CHANNEL_INDEX_IO_DIRECTION)
from codebug_tether.char_map import (CharSprite, StringSprite)


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
        self.assertEqual(self.codebug.get(CHANNEL_INDEX_IO_DIRECTION), 0xAA)

        self.codebug.set_leg_io(0, 1)
        self.codebug.set_leg_io(1, 0)
        self.codebug.set_leg_io(2, 1)
        self.codebug.set_leg_io(3, 0)
        self.codebug.set_leg_io(4, 1)
        self.codebug.set_leg_io(5, 0)
        self.codebug.set_leg_io(6, 1)
        self.codebug.set_leg_io(7, 0)
        self.assertEqual(self.codebug.get(CHANNEL_INDEX_IO_DIRECTION), 0x55)

        # safely back to inputs
        for i in range(7):
            self.codebug.set_leg_io(i, 1)

    def test_clear(self):
        self.codebug.clear()
        rows = self.codebug.get_bulk(0, 5)
        self.assertEqual(rows, (0,)*5)

    def test_set_row(self):
        for test_value in (0x0A, 0x15):
            for i in range(5):
                self.codebug.set_row(i, test_value)
            rows = self.codebug.get_bulk(0, 5)
            self.assertEqual(rows, (test_value,)*5)
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
        rows = self.codebug.get_bulk(0, 5)
        self.assertEqual(rows, (0x00, 0x1F, 0x00, 0x1F, 0x00))
        self.codebug.clear()

        for i in range(5):
            self.codebug.set_col(i, 0x15)
        rows = self.codebug.get_bulk(0, 5)
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
                self.assertEqual(self.codebug.get(y), 1 << (4-x))
                self.codebug.set_pixel(x, y, 0)

    def test_get_pixel(self):
        self.codebug.clear()
        for y in range(5):
            for x in range(5):
                for i in range(2):
                    self.codebug.set_pixel(x, y, i)
                    self.assertEqual(self.codebug.get_pixel(x, y), i)

    def test_get_set_buffer(self):
        v = tuple(range(255))
        self.codebug.set_buffer(0, v)
        self.assertEqual(self.codebug.get_buffer(0, len(v)), v)
        v = tuple(range(100))
        self.codebug.set_buffer(0, v, 100)
        self.assertEqual(self.codebug.get_buffer(0, 255),
                         tuple(range(100))+tuple(range(100))+tuple(range(100+100, 255)))
        self.assertEqual(self.codebug.get_buffer(0, 101, 100),
                         tuple(range(100))+(range(255)[200],))

    # def test_write_text(self):
    #     msg = "Hello, CodeBug!"
    #     delay = 0.025
    #     for i in range(len(msg) * 5 + 5):
    #         self.codebug.write_text(5 - i, 0, msg)
    #         time.sleep(delay)

    #     for i in range(len(msg) * 6 + 6):
    #         self.codebug.write_text(0, i - 5, msg, direction="down")
    #         time.sleep(delay)

    #     for i in range(len(msg) * 5 + 5):
    #         self.codebug.write_text(0 - i, 0, msg, direction="left")
    #         time.sleep(delay)

    #     for i in range(len(msg) * 6 + 6):
    #         self.codebug.write_text(0, i - 5, msg, direction="up")
    #         time.sleep(delay)


class TestSprites(unittest.TestCase):

    def test_string_sprite(self):
        s = StringSprite("hello")

        expected = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
                    [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
                    [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
                    [1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0]]
        self.assertEqual(s.pixel_state, expected)


if __name__ == "__main__":
    unittest.main()
