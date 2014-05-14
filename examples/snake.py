# only needed for testing
import os
import sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

from codebug_tether import CodeBug
import time

gridSize = 4

FOWARD = 0
CLOCKWISE = 1
ANTICLOCKWISE = -1

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

directions = ["NORTH","EAST","SOUTH","WEST"]

movement = WEST
# direction = FOWARD

snakeDirections = [WEST,WEST,WEST]

counter = 0
levelcounter = 0
headX = 2
headY = 2
snakeLength = len(snakeDirections)
tailX = headX + snakeLength -1
tailY = headY
gameOver = False

# debug_directions = [FOWARD,CLOCKWISE,CLOCKWISE,FOWARD,FOWARD,CLOCKWISE,CLOCKWISE,FOWARD,ANTICLOCKWISE,ANTICLOCKWISE,FOWARD,FOWARD,FOWARD]

if __name__ == '__main__':
	cb = CodeBug('/dev/tty.usbmodemfa141')
	cb.clear()
	delay = 0.2
	for i, x in enumerate(snakeDirections):
		cb.set_led(headX+i,headY, 1)
	cb.set_led(headX+1,headY, 1)

	while not gameOver:
		if counter % 2500000 == 2490000:
			if cb.get_input("A"):
			# if debug_directions[0] == ANTICLOCKWISE:
				if movement == NORTH:
					movement = WEST
				else:
					movement += ANTICLOCKWISE

			elif cb.get_input("B"):
			# elif debug_directions[0] == CLOCKWISE:
				movement = (movement+CLOCKWISE)%4
			# del debug_directions[0]	

			print directions[movement]
			print directions[snakeDirections[-1]]

			snakeDirections = [movement] + snakeDirections
			if movement == NORTH:
				headY += 1
			elif movement == EAST:
				headX += 1
			elif movement == SOUTH:
				headY -= 1
			else:
				headX -= 1

			if headX > -1 and headX <= gridSize and headY > -1 and headY <= gridSize:
				if cb.get_led(headX, headY):
					print "You hit yourself!"
					gameOver = True

				cb.set_led(headX, headY, 1)

				if levelcounter%10 != 2:
					del snakeDirections[-1]
					cb.set_led(tailX, tailY, 0)
					if snakeDirections[-1] == NORTH:
						tailY += 1
					elif snakeDirections[-1] == EAST:
						tailX += 1
					elif snakeDirections[-1] == SOUTH:
						tailY -= 1
					else:
						tailX -= 1
				levelcounter +=1	
			else:
				print "You hit a wall!"
				gameOver = True

		counter +=1
