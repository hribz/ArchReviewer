from setuptools import setup

setup(
    name='ArchReviewer',
    version="Beta",

    install_requires=[
        'statlib==1.2',
        'pyparsing==2.*',
        'lxml>=3.4'
    ],

    entry_points={'console_scripts': [
        'ArchReviewer = src.main:main',
    ]}
)
