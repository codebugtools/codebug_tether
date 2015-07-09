CodeBug Tether
==============
Can control CodeBug tethered over Serial USB.

Documentation: http://codebug-tether.readthedocs.org/


CodeBug Loader RX (cblrx)
=========================
This is a test receiver for the CodeBug loader.

In terminal 1:

    $ cd cblrx
    $ make
    $ ./cblrx
    Fake CodeBug serial port is: /dev/pts/4

In terminal 2:

    $ python3
    >>> from codebug_tether import CodeBug
    >>>
    >>> cb = CodeBug('/dev/pts/4')
    >>>
    >>> cb.set(0, 0b10101)

Watch terminal 1 change.
