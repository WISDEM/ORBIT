ORBIT
=====

Offshore Renewables Balance of system and Installation Tool

|PyPI version| |PyPI downloads| |Apache 2.0| |image|

|Binder| |Pre-commit| |Black| |isort| |Ruff|

:Authors: `Jake Nunemaker <https://www.linkedin.com/in/jake-nunemaker/>`_, `Matt Shields <https://www.linkedin.com/in/matt-shields-834a6b66/>`_, `Rob Hammond <https://www.linkedin.com/in/rob-hammond-33583756/>`_, `Nick Riccobono <https://www.linkedin.com/in/nicholas-riccobono-674a3b43/>`_
:Documentation: `ORBIT Docs <https://wisdem.github.io/ORBIT/>`_

Installation
------------

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

Dependencies
~~~~~~~~~~~~

- Python 3.9, 3.10, 3.11
- marmot-agents
- SimPy
- NumPy
- Pandas
- SciPy
- Matplotlib
- OpenMDAO (>=3.2)
- python-benedict
- statsmodels
- PyYAML

Development Specific
~~~~~~~~~~~~~~~~~~~~

- pre-commit
- black
- isort
- ruff
- pytest
- pytest-cov
- sphinx
- sphinx-rtd-theme


Recommended packages for easy iteration and running of code:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- jupyterlab


.. |PyPI version| image:: https://badge.fury.io/py/orbit-nrel.svg
   :target: https://badge.fury.io/py/orbit-nrel
.. |PyPI downloads| image:: https://img.shields.io/pypi/dm/orbit-nrel?link=https%3A%2F%2Fpypi.org%2Fproject%2Forbit-nrel%2F
   :target: https://pypi.org/project/orbit-nrel/
.. |Apache 2.0| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
.. |image| image:: https://img.shields.io/pypi/pyversions/orbit-nrel.svg
   :target: https://pypi.python.org/pypi/orbit-nrel
.. |Binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/WISDEM/ORBIT/dev?filepath=examples
.. |Pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |isort| image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
   :target: https://pycqa.github.io/isort/
.. |Ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
