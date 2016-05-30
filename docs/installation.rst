############
Installation
############

Setting up CodeBug
==================
In order to use CodeBug with codebug_tether you need to program CodeBug
with ``codebug_tether.cbg`` (|firmwaredownload|).

To do this, hold down button A and plug in CodeBug via USB --- it should
appear as a USB drive --- then copy the ``codebug_tether.cbg`` file onto it.
CodeBug is now ready to be used via serial USB. Press button B to exit
programming mode.

.. note:: When CodeBug is connected to a computer via USB is should now
          appear as a serial device. To reprogram CodeBug: hold down
          button A and (re)plug it into a USB port.

Install codebug_tether on Windows
=================================
.. note:: These instructions are based on `The Hitchhikers Guide to Python: Installing Python on Windows <http://docs.python-guide.org/en/latest/starting/install/win/>`_

Install Python
--------------
Download and install the latest version of Python 3 from `here <https://www.python.org/downloads/windows/>`_.
Make sure you tick the *Add Python 3 to environment variables* checkbox.

Install codebug_tether
----------------------
To install codebug_tether, open up a command prompt and type::

    pip install codebug_tether

Restart Windows and then open IDLE. Plug in CodeBug and type::

    >>> import codebug_tether
    >>> codebug = codebug_tether.CodeBug()
    >>> codebug.set_pixel(2, 2, 1)

The middle pixel on your CodeBug should light up.

See :ref:`examples-label` for more ways to use codebug_tether.


Install codebug_tether on OSX
=============================
.. note:: These instructions are based on `The Hitchhikers Guide to Python: Installing Python on Mac OS X <http://docs.python-guide.org/en/latest/starting/install/osx/>`_

Install Python
--------------
Download and install `Xcode <https://developer.apple.com/xcode/download/>`_ (if you haven't already) and then enable the command line tools by running (in a terminal)::

    xcode-select --install

Now install Homebrew (a package manager for OSX)::

    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

The script will explain what changes it will make and prompt you before the installation begins. Once you’ve installed Homebrew, insert the Homebrew directory at the top of your **PATH** environment variable. You can do this by adding the following line at the bottom of your ~/.profile file::

    export PATH=/usr/local/bin:/usr/local/sbin:$PATH

Now, we can install Python 3::

    brew install python3

This will take a minute or two.

Install codebug_tether
----------------------
To install codebug_tether, open up a terminal and type::

    pip install codebug_tether

To test it has worked, plug in CodeBug and open a Python shell by typing::

    python

Your command prompt should have changed to::

    >>> _

Now type::

    >>> import codebug_tether
    >>> codebug = codebug_tether.CodeBug()
    >>> codebug.set_pixel(2, 2, 1)

The middle pixel on your CodeBug should light up.

See :ref:`examples-label` for more ways to use codebug_tether.


Install codebug_tether on Linux
===============================
Install Python
--------------
Python should already be installed but for good measure::

    sudo apt-get install python3

To install pip, securely download `get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_.

Then run the following::

    sudo python3 get-pip.py


Install codebug_tether
----------------------
To install codebug_tether, open up a terminal and type::

    pip3 install codebug_tether

To test it has worked, plug in CodeBug and open a Python shell by typing::

    python3

Your command prompt should have changed to::

    >>> _

Now type::

    >>> import codebug_tether
    >>> codebug = codebug_tether.CodeBug()
    >>> codebug.set_pixel(2, 2, 1)

The middle pixel on your CodeBug should light up.

See :ref:`examples-label` for more ways to use codebug_tether.
