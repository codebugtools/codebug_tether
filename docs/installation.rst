############
Installation
############
You can use the ``codebug_tether`` Python 3 API by either:

* Installing with ``pip``
* Copying the ``codebug_tether`` module into your project directory.


Setting up CodeBug
------------------
In order to communicate with CodeBug over Serial USB you need to program CodeBug with
``codebug_tether.cbg``. To do this, plug in CodeBug via USB --- it
should appear as a USB drive --- then copy onto it the
``codebug_tether.cbg`` file. CodeBug is now ready to be used via Serial USB.


Installing with ``pip``
-----------------------
.. warning:: Do not install ``codebug_tether`` with both ``apt-get``
             and ``pip`` as unexpected things will happen. Consider using
             virtual environments.

Make sure ``pip`` is installed::

    sudo apt-get install python3-pip

Install ``codebug_tether`` using ``pip``::

    sudo pip-3.2 install codebug_tether


Installing with ``pip`` (with Virtual Environments)
---------------------------------------------------
.. note :: Generally, it's best to install packages into a
           `virtual environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_
           when using ``pip`` so that they remain project specific.

Install ``virtualenv``::

    sudo pip-3.2 install virtualenv

Move into your project and create the virtual environment::

    cd my_project_directory/
    virtualenv-3.2 venv

Activate the virtual environment::

    source venv/bin/activate

You should notice that your command prompt has changed. ``pip`` will now
install all packages into the virtual environment instead of littering
your system files::

    pip install codebug_tether

Now you can work on your application with ``codebug_tether``. Once
you're done, deactivate the virtual environment::

    deactivate

You will not be able to use packages installed in the virtual environment
until you activate it again (`source venv/bin/activate`).


Using ``codebug_tether`` without installing
-----------------------------------------------
You may want to use ``codebug_tether`` without installing anything at
all. You can just download and include the ``codebug_tether`` package
in your project and start using it. The quickest way to do this is::

    git clone https://github.com/codebugtools/codebug_tether.git
    cp -r codebug_tether/codebug_tether myproject/
    cd myproject/
    python3
    >>> import codebug_tether
