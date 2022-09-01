from setuptools import setup
from Cython.Build import cythonize
import sys

if sys.maxsize > 2 ** 32:
    setup(
        ext_modules = cythonize("dbpf64.pyx", language_level="3")
    )
else:
    setup(
        ext_modules = cythonize("dbpf32.pyx", language_level="3")
    )