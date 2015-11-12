"""Handy I2C message building for CodeBug."""
from collections import namedtuple


# I2C messages
I2C_CONTROL_GO_BUSY = 0x01
I2C_CONTROL_SEND_ADDR = 0x02
I2C_CONTROL_MASTER_FINAL_ACK = 0x04
I2C_CONTROL_WAIT_FOR_ACK = 0x08
I2C_CONTROL_ACK_AFTER_READ = 0x10
I2C_CONTROL_START = 0x20
I2C_CONTROL_STOP = 0x40
I2C_CONTROL_READ_NOT_WRITE = 0x80


I2CMsg = namedtuple('I2CMsg', ['control', 'address', 'data', 'length'])


# I2C messages
def writing(address, data):
    """Returns a standard I2C write message. Address is limited to 7 bits."""
    return I2CMsg(control=(I2C_CONTROL_START |
                           I2C_CONTROL_SEND_ADDR |
                           I2C_CONTROL_WAIT_FOR_ACK |
                           I2C_CONTROL_STOP),
                  address=(0x3f & address),
                  data=data,
                  length=len(data))


def reading(address, length):
    """Returns a standard I2C read message. Address is limited to 7 bits."""
    return I2CMsg(control=(I2C_CONTROL_START |
                           I2C_CONTROL_SEND_ADDR |
                           I2C_CONTROL_WAIT_FOR_ACK |
                           I2C_CONTROL_STOP |
                           I2C_CONTROL_READ_NOT_WRITE),
                  address=(0x3f & address),
                  data=list(),
                  length=length)
