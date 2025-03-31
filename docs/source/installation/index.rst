.. _installation:

Installing ORBIT
================
As of version 0.5.2, ORBIT is now pip installable with ``pip install orbit-nrel``.

Development Setup
-----------------

The steps below are for more advanced users that would like to modify and
and contribute to ORBIT.

Environment
~~~~~~~~~~~

A couple of notes before you get started:
 - It is assumed that you will be using the terminal on MacOS/Linux or the
   Anaconda Prompt on Windows. The instructions refer to both as the
   "terminal", and unless otherwise noted the commands will be the same.
 - To verify git is installed, run ``git --version`` in the terminal. If an error
   occurs, install git using these `directions <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.
 - The listed installation process is intended to be the easiest for any OS
   to get started. An alternative setup that doesn't rely on Anaconda for
   setting up an environment can be followed
   `here <https://realpython.com/python-virtual-environments-a-primer/#managing-virtual-environments-with-virtualenvwrapper>`_.

Instructions
~~~~~~~~~~~~

1. Download the latest version of `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_
   for the appropriate OS. Follow the remaining `steps <https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation>`_
   for the appropriate OS version.
2. From the terminal, install pip by running: ``conda install -c anaconda pip``
3. Next, create a new environment for the project with the following.

    .. code-block:: console

        conda create -n <environment_name> python=3.10 --no-default-packages

   To activate/deactivate the environment, use the following commands.

    .. code-block:: console

        conda activate <environment_name>
        conda deactivate <environment_name>

4. Clone the repository:
   ``git clone https://github.com/WISDEM/ORBIT.git``
5. Navigate to the top level of the repository
   (``<path-to-ORBIT>/ORBIT/``) and install ORBIT as an editable package
   with following command.

    .. code-block:: console

       # Note the "." at the end
       pip install -e .

       # OR if you are you going to be contributing to the code or building documentation
       pip install -e '.[dev]'
6. (Development only) Install the pre-commit hooks to autoformat and lint code.

    .. code-block:: console

        pre-commit install
