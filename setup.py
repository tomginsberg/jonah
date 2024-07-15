from setuptools import setup

setup(
    name='jonah',
    version='1.0',
    packages=['jonah'],
    install_requires=['pandas', 'openpyxl'],
    entry_points={
        'console_scripts': [
            'jonah=jonah.jonah:main',
        ]
    }
)
