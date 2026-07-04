from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("termux_code_chee_fixed.py")
)
