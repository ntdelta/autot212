from setuptools import setup, find_packages

setup(
    name="autot212",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "autot212=autot212.main:main",
        ],
    },
)