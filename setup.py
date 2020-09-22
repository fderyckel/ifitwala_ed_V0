# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in ifitwala_dev/__init__.py
from ifitwala_ed import __version__ as version

setup(
	name='ifitwala_ed',
	version=version,
	description='sms',
	author='flipo',
	author_email='fderyckel@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
