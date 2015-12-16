"""Handy I2C message building for CodeBug."""
# I2C messages
I2C_CONTROL_GO_BUSY = 0x01
I2C_CONTROL_SEND_ADDR = 0x02
I2C_CONTROL_MASTER_FINAL_ACK = 0x04
I2C_CONTROL_WAIT_FOR_ACK = 0x08
I2C_CONTROL_ACK_AFTER_READ = 0x10
I2C_CONTROL_STOP = 0x20
I2C_CONTROL_START = 0x40
I2C_CONTROL_READ_NOT_WRITE = 0x80


class CodeBugI2CMaster():
    """Performs I2C I/O transactions on the CodeBug I2C bus.

    Transactions are performed by passing one or more I2C I/O messages
    to the transaction method of the I2CMaster.  I2C I/O messages are
    created with the reading and writing functions defined in the
    `codebug_tether.i2c module`.

    CodeBugI2CMaster acts as a context manager, allowing it to be used in a
    with statement. This is for compatibility with other I2CMasters,
    which this is intended to be used in place of. On its own there is
    no need to use this as a context manager.

    For example:

        import codebug_tether
        from codebug_tether.i2c import (I2CMaster, writing)

        codebug = codebug_tether.CodeBug()

        with I2CMaster(codebug) as i2c:
            i2c.transaction(writing(0x20, bytes([0x01, 0xFF])))

    """
    def __init__(self, codebug):
        """
        :param codebug: The CodeBug through which to send I2C data.
        :type codebug: `codebug_tether.core.CodeBug`
        """
        self.codebug = codebug

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def transaction(self, *msgs):
        """Perform an I2C I/O transaction. I2CMasters usually return one
        bytes array per read operation. Since CodeBug is only capable of one
        it doens't normally do this.
        """
        return [bytes(self.codebug.i2c_transaction(*msgs))]


class I2CMessage():
    """Data structure for building I2C message patterns."""

    def __init__(self, control, address, data, length):
        self.control = control
        self.address = address
        self.data = data
        self.length = length


# I2C message generators (feel free to go ahead and form your own I2C messages)
def writing_bytes(addr, *data_bytes):
    """An I2C I/O message that writes one or more bytes of data.

    Each byte is passed as an argument to this function.

        writing_bytes(addr, 1, 2, 3)

    """
    return writing(addr, data_bytes)


def writing(address, data_bytes):
    """Returns a standard I2C write message. Address is limited to 7 bits.

    The bytes are passed to this function as a sequence.

        writing_bytes(addr, (1, 2, 3))

    """
    data = bytes(data_bytes)
    return I2CMessage(control=(I2C_CONTROL_START |
                               I2C_CONTROL_SEND_ADDR |
                               I2C_CONTROL_WAIT_FOR_ACK |
                               I2C_CONTROL_GO_BUSY),
                      address=(0x7f & address),
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
                      address=(0x7f & address),
                      data=list(),
                      length=length)
