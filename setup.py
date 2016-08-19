#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(name = 'dragons_breath',
      description = 'Code to analyze the HST/WFC3 Dragons Breath Anomaly',
      author = 'Larissa Markwardt, Matthew Bourque, Space Telescope Science Institute',
      url = 'https://grit.stsci.edu/bourque/dragons_breath.git',
      packages = find_packages(),
      install_requires = ['matplotlib', 'numpy', 'sqlalchemy', 'astropy']
    )