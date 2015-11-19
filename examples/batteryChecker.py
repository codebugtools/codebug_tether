import time
import subprocess
from codebug_tether import CodeBug

# Mac
batteryCommand = ["pmset", "-g", "batt"]


def displayString(displayString):
    delay = 0.2
    if len(displayString) > 1:
        for i in range(len(displayString) * 5 + 5):
            cb.write_text(5 - i, 0, displayString)
            time.sleep(delay)
    else:
        cb.write_text(0, 0, displayString)
        time.sleep(5)
    cb.clear()


if __name__ == '__main__':
    cb = CodeBug('/dev/tty.usbmodemfa141')
    cb.clear()
    while True:
        if cb.get_input("A"):
            outputString = subprocess.check_output(batteryCommand)
            # print outputString
            batteryLife = outputString.split("\t")[1].split("%")[0]
            # print batteryLife
            displayString(batteryLife+'%')

        elif cb.get_input("B"):
            outputString = subprocess.check_output(batteryCommand)
            batteryLife = int(outputString.split("\t")[1].split("%")[0])
            # print batteryLife
            rows = batteryLife/20
            # print rows
            for i in range(rows):
                cb.set_row(i,0b11111)
                # time.sleep(.1)
            units = batteryLife%20
            # print units
            unitleds = ((units)/4)
            # print unitleds
            for i in range(unitleds):
                cb.set_led(i,rows,1)
            time.sleep(4)
            cb.clear()
