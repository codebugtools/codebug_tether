# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from codebug_tether import CodeBug
import time

FOWARD = 0
CLOCKWISE = 1
ANTICLOCKWISE = -1

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

movement = WEST
# direction = FOWARD

snakeDirections = [FOWARD,FOWARD]

counter = 0
headX = 2
headY = 2
tailX = headX + len(snakeDirections)-1
tailY = headY

grid = [[0,0,0,0,0],
		[0,0,0,0,0],
		[0,0,0,0,0],
		[0,0,0,0,0],
		[0,0,0,0,0]]

def displayString(displayString):
	for i in range(len(displayString) * 5 + 5):
		cb.write_text(5 - i, 0, displayString)
		time.sleep(delay)	

def updateDisplay():
	b = 0
	for row in grid:
		b = 0
		for col in row:
			b = (b+col)*2
		b = b/2
		cb.set_row(row,b)

if __name__ == '__main__':
	cb = CodeBug('/dev/tty...')
	cb.clear()
	delay = 0.2
	while True:
		# if cb.get_input("A"):
		# 	direction = ANTICLOCKWISE
		# elif cb.get_input("B"):
		# 	direction = CLOCKWISE

		if counter %20:
			if cb.get_input("A"):
				if movement == NORTH:
					movement = WEST
				else:
					movement += ANTICLOCKWISE

			elif cb.get_input("B"):
				movement = (movement+CLOCKWISE)%3
		
		counter +=1
