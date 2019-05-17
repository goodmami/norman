#!/usr/bin/env python3

from setuptools import setup


setup(
    name='norman',
    version='0.1.0',
    description='AMR Normalization',
    long_description='',
    url='',
    author='',
    author_email='',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
    keywords='nlp amr',
    py_modules=['norman'],
    install_requires=[
        'penman >= 0.6.2'
    ]
    # entry_points={
    #     'console_scripts': [
    #         'penman=...'
    #     ]
    # }
)
