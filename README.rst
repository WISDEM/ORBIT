ORBIT
=====

Offshore Renewables Balance of system and Installation Tool

:Version: 0.3.0
:Authors: `Jake Nunemaker <https://www.linkedin.com/in/jake-nunemaker/>`_, `Matt Shields <https://www.linkedin.com/in/matt-shields-834a6b66/>`_, `Rob Hammond <https://www.linkedin.com/in/rob-hammond-33583756/>`_

This package is currently in a development state and it is only recommended for
preliminary analysis.

Installation
------------

Dependencies
~~~~~~~~~~~~

ORBIT requires:

- Python 3.7+
- SimPy (pip only)
- NumPy
- SciPy
- pandas
- Matplotlib

Additional packages needed for development:

- black (pip only)
- isort (pip only)
- pre-commit (pip only)
- pytest (``conda install -c conda-forge pre-commit``)
- pytest-xdist (pip only)
- pytest-cov (pip only)

Additional packages needed to build documentation:

- sphinx
- sphinx_rtd_theme (pip only)

Additional packages for easy iteration and running of code:

- jupyterlab (``conda install -c conda-forge jupyterlab``)


Environment Setup
-----------------

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

        conda create -n <environment_name> python=3.7 --no-default-packages

   To activate/deactivate the environment, use the following commands.

    .. code-block:: console

        conda activate <environment_name>
        conda deactivate <environment_name>

4. (Optional) Install the dependencies to your newly created conda environment using
   ``conda install <package>`` unless they are listed as "(pip only)", in which
   case use ``pip install <package>``.
    In general, when using the Anaconda suite it is best to find the conda
    specific installation command.
    When installing, be sure to use all lowercase letters in
    ``... install <package>`` unless otherwise noted.
5. Clone the repository:
   ``git clone https://github.nrel.gov/OffshoreAnalysis/ORBIT-dev.git``
6. Navigate to the top level of the repository
   (``<path-to-ORBIT>/ORBIT/``) and install ORBIT as an editable package
   with following command.

    .. code-block:: console

       # Note the "." at the end
       pip install -e .

       # OR if you are you going to be contributing to the code use
       pip install -e '.[dev]'
