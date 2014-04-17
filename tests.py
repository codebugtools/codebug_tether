#!/usr/bin/env python3
# import os
# import sys
# parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, parentdir)
import unittest
from codebug_loader.core import CodeBug


class TestCodeBugObject(unittest.TestCase):

    def setUp(self):
        self.codebug = CodeBug()
        self.num_channels = 6

    def test_channels(self):
        """
            >>> codebug.channels[1].value = 2
            >>> codebug.channels[1].value
            2
        """
        for i in range(self.num_channels):
            self.codebug.channels[i].value = i*i

        for i in range(self.num_channels):
            self.assertEqual(self.codebug.channels[i].value, i*i)

    def test_channels_get_set(self):
        """
            >>> codebug.set(1, 2)
            >>> codebug.get(1)
            2
        """
        for i in range(self.num_channels):
            self.codebug.set(i, i*i)

        for i in range(self.num_channels):
            self.assertEqual(self.codebug.get(i), i*i)

    def test_channel_get_set_bulk(self):
        """
            >>> codebug.set_bulk(0, [1, 2, 3])
            >>> codebug.channels[1].value
            2
        """
        v = list(range(self.num_channels))
        self.codebug.set_bulk(0, v)
        self.assertEqual(self.codebug.get_bulk(0, len(v)), v)

        v[2] = 42
        v[3] = 43
        self.codebug.set_bulk(2, v[2:4])
        self.assertEqual(self.codebug.get_bulk(0, 6), v)


if __name__ == "__main__":
    unittest.main()
