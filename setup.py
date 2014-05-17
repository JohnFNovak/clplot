from setuptools import setup  # , find_packages
# from setuptools.command.test import test as TestCommand
import io
# import codecs
import os
# import sys

import clplot

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

# long_description = read('README.txt', 'CHANGES.txt')


# class PyTest(TestCommand):
#     def finalize_options(self):
#         TestCommand.finalize_options(self)
#         self.test_args = []
#         self.test_suite = True

#     def run_tests(self):
#         import pytest
#         errcode = pytest.main(self.test_args)
#         sys.exit(errcode)

setup(
    name='clplot',
    version=clplot.__version__,
    url='http://github.com/JohnFNovak/clplot/',
    license='Public Domain',
    author='John F Novak',
    # tests_require=['pytest'],
    install_requires=['Matplotlib>1.0',
                      'numpy>1.0'],
    # cmdclass={'test': PyTest},
    author_email='john.franc.novak@gmail.com',
    description='a command line plotting utility written in python',
    # long_description=long_description,
    packages=['clplot'],
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'plot = clplot.clplot:main',
        ]
    },
    # test_suite='clplot.test.test_clplot',
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
    # extras_require={
    #     'testing': ['pytest'],
    # }
)
