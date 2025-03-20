from setuptools import setup, Extension

module = Extension(
    "sum",  # Nombre del módulo
    sources=["sum.c"],  # Archivo fuente
)

setup(
    name="sum",
    version="1.0",
    description="A simple C extension for Python",
    ext_modules=[module],
)
