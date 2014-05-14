# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from codebug_tether import CodeBug
import time
from random import randint

if len(sys.argv) != 3:
	print "Give two numbers as arguments"
	sys.exit(1)

def diceRoll():
	return randint(1,6)

if __name__ == '__main__':
	cb = CodeBug('/dev/tty.usbmodemfa141')
	cb.clear()
	delay = 0.2
	while True:
		if cb.get_input("A"):
			number = str(randint(int(sys.argv[1]), int(sys.argv[2])))
			for i in range(len(number) * 5 + 5):
				cb.write_text(5 - i, 0, number)
				time.sleep(delay)
			time.sleep(1)