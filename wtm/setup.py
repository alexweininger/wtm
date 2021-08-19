from setuptools import setup, find_packages

setup(
    name='wtm',
    version='0.1.0',
    py_modules=['init'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'wtm = init:cli',
        ],
    },
)