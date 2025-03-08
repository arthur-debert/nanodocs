from setuptools import find_packages, setup

setup(
    name="nanodoc",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "nanodoc=nanodoc.nanodoc:main",
        ],
    },
)
