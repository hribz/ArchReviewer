from setuptools import setup, find_packages


setup(
    name='ArchReviewer',
    version="Beta",
    packages=find_packages(),

    install_requires=[
        'pyparsing==2.*',
        'enum34',
        'lxml>=3.4'
    ],

    entry_points={'console_scripts': [
        'ArchReviewer = src.archReviewer:main'
    ]}
)
