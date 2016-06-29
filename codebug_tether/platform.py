"""Functions for figuring out specific things about the current platform."""
import re
import os
import sys
import glob
import serial


def get_platform_serial_port():
    # setup DEFAULT_SERIAL_PORT which is different on Windows, MacOS,
    # Raspberry Pi 2 and Raspberry Pi 3
    if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
        # On Windows or OSX take the first serial port we can find
        def serial_ports():
            """ Lists serial port names

                :raises EnvironmentError:
                    On unsupported or unknown platforms
                :returns:
                    A list of the serial ports available on the system
            """
            if sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            elif (sys.platform.startswith('linux') or
                    sys.platform.startswith('cygwin')):
                # this excludes your current terminal "/dev/tty"
                ports = glob.glob('/dev/tty[A-Za-z0-9]*')
            elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
            else:
                raise EnvironmentError('Unsupported platform')

            result = []
            for port in ports:
                try:
                    s = serial.Serial(port)
                    s.close()
                    result.append(port)
                except (OSError, serial.SerialException):
                    pass
            return result
        # use the first one
        try:
            return serial_ports()[0]
        except IndexError:
            print('ERROR: Could not find any serial ports.', file=sys.stderr)
            return ''
    else:
        # otherwise assume we're on Raspberry Pi/Linux
        def get_rpi_revision():
            """Returns the version number from the revision line."""
            for line in open("/proc/cpuinfo"):
                if "Revision" in line:
                    return re.sub('Revision\t: ([a-z0-9]+)\n', r'\1', line)

        rpi_revision = get_rpi_revision()
        if (rpi_revision and
                (rpi_revision != 'Beta') and
                (int('0x'+rpi_revision, 16) >= 0xa02082)):
            # RPi 3 and above
            return '/dev/ttyS0'
        else:
            # RPi 2 and below
            return '/dev/ttyACM0'
