# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from codebug_tether import CodeBug
import time
import subprocess

# Mac
batteryCommand = ["pmset", "-g", "batt"]

def displayString(displayString):
	delay = 0.5
	if len(displayString) > 1:
		for i in range(len(displayString) * 5 + 5):
			cb.write_text(5 - i, 0, displayString)
			time.sleep(delay)
	else: 
		cb.write_text(0, 0, displayString)
		time.sleep(5)
	cb.clear()

if __name__ == '__main__':
    cb = CodeBug('/Users/tommacpherson-pope/codebug_tether/cblrx/cblrx')
    cb.clear()
    while True:
    	if cb.get_input("A"):
    		outputString = subprocess.check_output(batteryCommand)
    		batteryLife = outputString.split("\t")[1].split("%")
    		displayString(batteryLife)

    	elif cb.get_input("B"):
    		outputString = subprocess.check_output(batteryCommand)
    		batteryLife = int(outputString.split("\t")[1].split("%"))
    		for i in range(batteryLife/20):
    			cb.set_row(i,0b11111)
    			time.sleep(.1)

			for i in range(batteryLife%10):
				cb.set_led(i,(batteryLife/20)+1)
