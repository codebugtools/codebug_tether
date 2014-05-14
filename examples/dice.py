# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from codebug_tether import CodeBug
import time
from random import randint

sprites = [[0b00000,
			0b00000,
			0b00100,
			0b00000,
			0b00000,],
		   [0b10000,
			0b00000,
			0b00000,
			0b00000,
			0b00001,],
		   [0b10000,
			0b00000,
			0b00100,
			0b00000,
			0b00001,],
		   [0b10001,
			0b00000,
			0b00000,
			0b00000,
			0b10001,],
		   [0b10001,
			0b00000,
			0b00100,
			0b00000,
			0b10001,],
		   [0b10001,
			0b00000,
			0b10001,
			0b00000,
			0b10001,]]

def diceRoll():
	return randint(0,5)

def drawSprite(number):
	sprite = sprites[number]
	for i, row in enumerate(sprite):
		cb.set_row(i, row)

if __name__ == '__main__':
    cb = CodeBug()
    cb.clear()
    while True:
    	if cb.get_input("A"):
    		cb.clear()
    		time.sleep(.5)
    		drawSprite(diceRoll())
    		time.sleep(1)



