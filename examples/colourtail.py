import time
import datetime
import codebug_tether
import codebug_tether.colourtail


if __name__ == '__main__':
    codebug = codebug_tether.CodeBug()

    codebug.set_row(4, 0b00100)
    codebug.set_row(3, 0b00100)
    codebug.set_row(2, 0b10101)
    codebug.set_row(1, 0b01110)
    codebug.set_row(0, 0b00100)

    colourtail = codebug_tether.colourtail.CodeBugColourTail(codebug)

    # using CS pin
    colourtail.init()
    colourtail.set_pixel(0, 255, 0, 0)  # red
    colourtail.set_pixel(1, 0, 255, 0)  # green
    colourtail.set_pixel(2, 0, 0, 255)  # blue
    colourtail.update()  # turn on the LEDs

    rgb = 'red'
    red = 0
    green = 0
    blue = 0
    i = 0
    while True:
        if rgb == 'red':
            red += 1
            if red >= 255:
                red = 0
                rgb = 'green'
        elif rgb == 'green':
            green += 1
            if green >= 255:
                green = 0
                rgb = 'blue'
        elif rgb == 'blue':
            blue += 1
            if blue >= 255:
                blue = 0
                rgb = 'red'
        colourtail.set_pixel(i, red, green, blue)
        colourtail.update()  # turn on the LEDs
        i = (i + 1) % 16
        time.sleep(0.005)
