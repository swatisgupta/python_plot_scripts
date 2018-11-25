#!/usr/bin/python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

tautf_extension = Extension(
    name="pytautf",
    sources=["pytautf.pyx"],
    libraries=["pytautf"],
    library_dirs=["lib"],
    include_dirs=["lib"]
)

setup(
    name="pytautf",
    ext_modules=cythonize([tautf_extension])
)
