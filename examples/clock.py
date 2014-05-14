# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import datetime
from codebug_tether import CodeBug
import time
from random import randint

# if len(sys.argv) != 3:
# 	print "Give two numbers as arguments"
# 	sys.exit(1)

def displayString(displayString):
	for i in range(len(displayString) * 5 + 5):
		cb.write_text(5 - i, 0, displayString)
		time.sleep(delay)	

if __name__ == '__main__':
	cb = CodeBug('/dev/tty.usbmodemfa141')
	cb.clear()
	delay = 0.2
	while True:
		if cb.get_input("A"):
			now = datetime.datetime.now()
			timeString = "TIME: {}:{}".format(now.hour, now.minute)
			displayString(timeString)

		elif cb.get_input("B"):
			now = datetime.datetime.now()
			dateString = "DATE: {}/{}/{}".format(now.day, now.month, now.year)
			displayString(dateString)