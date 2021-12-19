from setuptools import setup, find_packages

setup(
    name="vartastorage",
    version="0.1.0",
    description="VARTA Battery",
    url="http://github.com/vip0r/vartastorage",
    author="edAndy",
    author_email="an-dy@gmx.de",
    license="APACHE",
    packages=['vartastorage'],
    zip_safe=False,
    install_requires=[
        "pymodbus",
    ],
)