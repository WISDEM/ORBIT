""""Distribution setup"""

import os

from setuptools import setup

import versioneer

ROOT = os.path.abspath(os.path.dirname(__file__))

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="ORBIT",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Offshore Renewables Balance of system and Installation Tool",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["ORBIT"],
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "pandas",
        "simpy-agents @ http://github.com/JakeNunemaker/simpy-agents/tarball/master#egg=v0.1.0",
        "marmot @ https://github.com/JakeNunemaker/marmot/tarball/master#egg=v0.2.3",
        "pyyaml",
        "geopy",
        "openmdao>= 2.0",
    ],
    extras_require={
        "dev": [
            "pre-commit",
            "pylint",
            "flake8",
            "black",
            "isort",
            "pytest",
            "pytest-cov",
            "pytest-xdist",
            "sphinx",
            "sphinx-rtd-theme",
        ]
    },
    test_suite="pytest",
    tests_require=["pytest", "pytest-xdist", "pytest-cov"],
)
