#!/usr/bin/env python

import os
import re

from setuptools import setup
from setuptools.dist import Distribution

PACKAGE_NAME = "petrelic"
SETUP_REQUIRE = ["pytest-runner", "cffi>=1.0.0"]
TEST_REQUIRE = ["pytest"]
INSTALL_REQUIRE = ["cffi>=1.0.0"]
DEV_REQUIRE = TEST_REQUIRE + ["sphinx", "sphinx_rtd_theme", "black"]
CFFI_MODULES = "petrelic/compile.py:_FFI"


class BinaryDistribution(Distribution):
    def is_pure(self):
        return False


# Import README as long description
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.rst")) as f:
    long_description = f.read()


# Obtain settings from __init__.py
with open(os.path.join(HERE, PACKAGE_NAME, "__init__.py")) as f:
    matches = re.findall(r"(__.+__) = \"(.*)\"", f.read())
    for var_name, var_value in matches:
        globals()[var_name] = var_value


setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=long_description,
    author=__author__,
    author_email=__email__,
    packages=['petrelic', 'petrelic.additive', 'petrelic.petlib'],
    package_data={
        'petrelic': ['libgmp.so', 'librelic.so'],
    },
    license=__license__,
    url=__url__,
    include_package_data=True,
    distclass=BinaryDistribution,
    install_requires=INSTALL_REQUIRE,
    setup_requires=SETUP_REQUIRE,
    tests_require=TEST_REQUIRE,
    extras_require={"dev": DEV_REQUIRE, "test": TEST_REQUIRE},
    cffi_modules=CFFI_MODULES,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires='>=3.6',
    zip_safe=False
)
