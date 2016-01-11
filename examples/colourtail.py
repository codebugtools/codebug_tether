import time
import datetime
import codebug_tether
import codebug_tether.colourtail


if __name__ == '__main__':
    # initialise
    codebug = codebug_tether.CodeBug()
    colourtail = codebug_tether.colourtail.CodeBugColourTail(codebug)

    # draw arrow
    codebug.set_row(4, 0b00100)
    codebug.set_row(3, 0b00100)
    codebug.set_row(2, 0b10101)
    codebug.set_row(1, 0b01110)
    codebug.set_row(0, 0b00100)

    codebug.config_extension_io()

    # initialise the colourtail (using EXT_CS pin)
    colourtail.init()
    # colourtail.init(use_leg_0_not_cs=True)
    colourtail.set_pixel(0, 255, 0, 0)  # red
    colourtail.set_pixel(1, 0, 255, 0)  # green
    colourtail.set_pixel(2, 0, 0, 255)  # blue
    colourtail.set_pixel(3, 0, 255, 0)
    colourtail.set_pixel(4, 255, 0, 0)
    colourtail.update()  # turn on the LEDs



    # # do the loopy spiral thing
    # current_colour = 'red'
    # red = 0
    # green = 0
    # blue = 0
    # i = 0
    # num_leds = 5
    # while True:
    #     if current_colour == 'red':
    #         red += 1
    #         if red >= 255:
    #             red = 0
    #             current_colour = 'green'
    #     elif current_colour == 'green':
    #         green += 1
    #         if green >= 255:
    #             green = 0
    #             current_colour = 'blue'
    #     elif current_colour == 'blue':
    #         blue += 1
    #         if blue >= 255:
    #             blue = 0
    #             current_colour = 'red'
    #     colourtail.set_pixel(i, red, green, blue)
    #     colourtail.update()  # turn on the LEDs
    #     i = (i + 1) % num_leds
    #     time.sleep(0.005)
