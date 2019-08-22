#!/usr/bin/env python3

import os
from setuptools import setup

base_dir = os.path.dirname(__file__)
with open(os.path.join(base_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='norman',
    version='0.1.0',
    description='AMR Normalization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/goodmami/norman',
    author='Michael Wayne Goodman',
    author_email='goodman.m.w@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
    keywords='nlp amr semantics graphs',
    py_modules=['norman'],
    setup_requires=['wheel >= 0.31.0'],
    install_requires=[
        'penman == 0.6.2',
        'smatch == 1.0.1'
    ]
)
