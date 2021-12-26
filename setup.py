import setuptools

setuptools.setup(
    name="vartastorage",
    version="0.1.1",
    description="VARTA Battery",
    url="http://github.com/vip0r/vartastorage",
    author="edAndy",
    author_email="an-dy@gmx.de",
    license="APACHE",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    zip_safe=False,
    install_requires=[
        "pymodbus",
    ],
)