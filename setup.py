from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='pyjobs',
    version=version,
    description="",
    long_description="",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='python tornado jobs',
    author='Winston Ferreira',
    author_email='winstonf88@gmail.com',
    url='https://github.com/winstonf88/pyjobs',
    license='GNU GENERAL PUBLIC LICENSE Version 2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'tornado',
        'beautifulsoup4',
    ],
    entry_points="""
        # -*- Entry points: -*-
        [console_scripts]
        pyjobs = pyjobs.app:server
    """,
)
