from setuptools import setup

setup(
    name='jonah',
    version='1.0',
    packages=['jonah'],
    install_requires=['pandas', 'openpyxl', 'streamlit'],
    entry_points={
        'console_scripts': [
            'jonah=jonah.jonah:main',
            'jonahpp=jonah.app:run_streamlit_app'
        ]
    }
)
