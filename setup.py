from setuptools import setup  # , find_packages
import os

import clplot

here = os.path.abspath(os.path.dirname(__file__))

long_description = """
clplot - command line plotting utility

    This utility is a command line front end to the matplotlib plotting
        module. This utility handles reading the data from file and determining
        the structure of the data. The utility attempts to make reasonable
        plot output using a collection of assumptions and inferences from the
        data. In many cases, reasonable output can be produced by the utility
        with the user providing nothing more than file names.

    when install with setuptools (or variant), an executable 'plot' is added
        to the user's path.
"""

setup(
    name='commandlineplot',
    version=clplot.__version__,
    url='http://github.com/JohnFNovak/clplot/',
    license='Public Domain',
    author='John F Novak',
    install_requires=['Matplotlib>1.0',
                      'numpy>1.0'],
    author_email='john.franc.novak@gmail.com',
    description='a command line plotting utility written in python',
    long_description=long_description,
    packages=['clplot'],
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'plot = clplot.clplot:main',
        ]
    },
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Visualization'
        ]
)
