#!/usr/bin/env python3
from setuptools import setup, find_packages

# read our README
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mif',
    url='https://github.com/agrif/mif/',
    description='reading and writing MIF files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Aaron Griffith',
    author_email='aargri@gmail.com',
    license='MIT',
    platforms=['any'],

    project_urls={
        'Source': 'https://github.com/agrif/mif/',
    },

    keywords='memory mif quartus',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    setup_requires=['setuptools_git >= 0.3', 'better-setuptools-git-version >= 1.0'],
    version_config={
        'version_format': '{tag}.dev{sha}',
    },

    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=['numpy', 'lark-parser'],
    python_requires='>=3.3',
    include_package_data=True,
    test_suite='tests',
)
