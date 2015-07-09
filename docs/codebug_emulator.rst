################
CodeBug Emulator
################

Install the codebug_emulator with::

    $ sudo apt-get install codebug_emulator

and start it with::

    $ codebug-emulator

The emulator will open up a pseudo-terminal at `/dev/pts/*some-number*`
which you read/write to as a serial port; mimicing the behaviour of the real
CodeBug. You can use `codebug_tether` to talk to control the CodeBug Emulator
like so (assuming the emulator is at `/dev/pts/5`)::

    $ python3
    >>> import codebug_tether
    >>> codebug_emulator = codebug_tether.CodeBug('/dev/pts/5')
    >>> codebug_emulator.write_text(0, 0, "H")
