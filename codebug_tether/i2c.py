"""Handy I2C message building for CodeBug."""
# I2C messages
I2C_CONTROL_GO_BUSY = 0x01
I2C_CONTROL_SEND_ADDR = 0x02
I2C_CONTROL_MASTER_FINAL_ACK = 0x04
I2C_CONTROL_WAIT_FOR_ACK = 0x08
I2C_CONTROL_ACK_AFTER_READ = 0x10
I2C_CONTROL_START = 0x20
I2C_CONTROL_STOP = 0x40
I2C_CONTROL_READ_NOT_WRITE = 0x80


class I2CMessage():
    """Data structure for building I2C message patterns."""

    def __init__(self, control, address, data, length):
        self.control = control
        self.address = address
        self.data = data
        self.length = length


# I2C messages
def writing(address, *data):
    """Returns a standard I2C write message. Address is limited to 7 bits."""
    return I2CMessage(control=(I2C_CONTROL_START |
                               I2C_CONTROL_SEND_ADDR |
                               I2C_CONTROL_WAIT_FOR_ACK |
                               I2C_CONTROL_GO_BUSY),
                      address=(0x3f & address),
                      data=data,
                      length=len(data))


def reading(address, length):
    """Returns a standard I2C read message. Address is limited to 7 bits."""
    return I2CMessage(control=(I2C_CONTROL_START |
                               I2C_CONTROL_SEND_ADDR |
                               I2C_CONTROL_WAIT_FOR_ACK |
                               I2C_CONTROL_ACK_AFTER_READ |
                               I2C_CONTROL_READ_NOT_WRITE |
                               I2C_CONTROL_GO_BUSY),
                      address=(0x3f & address),
                      data=list(),
                      length=length)
