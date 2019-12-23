""""Distribution setup"""

import os

from setuptools import setup

ROOT = os.path.abspath(os.path.dirname(__file__))

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open(os.path.join(ROOT, "VERSION")) as version_file:
    __version__ = version_file.read().strip()

setup(
    name="ORBIT-dev",
    version=__version__,
    description="ORBIT Development Repo",
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
        "simpy",
        "pyyaml",
        "geopy",
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
            "sphinx-rtd-theme"
        ]
    },
    test_suite="pytest",
    tests_require=["pytest", "pytest-xdist", "pytest-cov"],
)
