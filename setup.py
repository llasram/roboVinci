from setuptools import setup, find_packages

setup(
    name = "robovinci",
    version = "0.1",
    package_dir = {'': 'src'},
    packages = ['robovinci'],
    install_requires = [
        'eventlet',
        'nose',
        'mock',
        ],
    )
