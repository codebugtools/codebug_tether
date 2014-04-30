#!/usr/bin/env python3
# import os
# import sys
# parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, parentdir)
import time
import serial
import unittest
from codebug_loader.core import CodeBug


class TestCodeBugObject(unittest.TestCase):

    def setUp(self):
        self.codebug = CodeBug(serial.Serial('/dev/pts/5'))
        self.num_channels = 6

    # @unittest.skip
    def test_channels(self):
        """
            >>> codebug.channels[1].value = 2
            >>> codebug.channels[1].value
            2
        """
        for i in range(self.num_channels):
            self.codebug.channels[i].value = (i*i) % 0x1F

        for i in range(self.num_channels):
            self.assertEqual(self.codebug.channels[i].value, (i*i) % 0x1F)

    # @unittest.skip
    def test_channels_get_set(self):
        """
            >>> codebug.set(1, 2)
            >>> codebug.get(1)
            2
        """
        for i in range(self.num_channels):
            self.codebug.set(i, (i*i) % 0x1F)

        for i in range(self.num_channels):
            self.assertEqual(self.codebug.get(i), (i*i) % 0x1F)

    # @unittest.skip
    def test_channel_get_set_bulk(self):
        """
            >>> codebug.set_bulk(0, [1, 2, 3])
            >>> codebug.channels[1].value
            2
        """
        v = list(range(self.num_channels))
        self.codebug.set_bulk(0, v)
        self.assertEqual(tuple(self.codebug.get_bulk(0, len(v))),
                         tuple(v))

        v[2] = 0b11011
        v[3] = 0b01001
        self.codebug.set_bulk(2, v[2:4])
        self.assertEqual(tuple(self.codebug.get_bulk(0, 6)), tuple(v))

    @unittest.skip
    def test_channel_read_write(self):
        """
            >>> codebug.write(0x300, data)
            >>> codebug.read(0x300, 0x400)
        """
        v = list(range(self.num_channels))
        self.codebug.set_bulk(0, v)
        self.assertEqual(self.codebug.get_bulk(0, len(v)), v)

        v[2] = 0b01101
        v[3] = 0b01011
        self.codebug.set_bulk(2, v[2:4])
        self.assertEqual(self.codebug.get_bulk(0, 6), v)


if __name__ == "__main__":
    unittest.main()
