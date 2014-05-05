# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from codebug_tether import CodeBug
import time


if __name__ == '__main__':
    cb = CodeBug()
    cb.clear()
    for i in range(0x20):
        cb.set_row(0, i)
        time.sleep(1)
