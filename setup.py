from setuptools import find_packages, setup

setup(
    name="nanodoc",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "nanodoc=nanodoc.nanodoc:main",
        ],
    },
)
