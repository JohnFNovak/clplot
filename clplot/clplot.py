#!/usr/bin/env python

# A universal command line plotting script
#
# John Novak
# June 4, 2012 - July 19, 2012

# Run with: python clplot.py
# or just: ./clplot.py (after making it executable, obviously)

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import numpy as np
import matplotlib.pyplot as plt
import string
import globe
from structure import *
from helpers import *
from plot import *
from data_handler import *


def main():
    dic = globe.dic
    read_flags()

    if dic['MULTIT'] and dic['layout']:
        if (dic['layout'][0]*dic['layout'][1] < int(dic['MULTIT'])):
            print "The layout that you specified was too small"
            dic['layout'] = plot_arragnement()
        else:
            print "We are using the layout you specified:", dic['layout'][0],
            print "by", dic['layout'][1]
    if dic['MULTIT'] and not dic['layout']:
        dic['layout'] = plot_arragnement()

    if dic['outputs'] and (len(dic['outputs']) !=
                           len(dic['files'])) and not (dic['MULTIT'] or
                                                       dic['MULTIP']):
        print "If you are going to specify output names",
        print "you must specify one output file per input file."

    for filename in dic['files']:
        print "plotting", filename
        dic['currentfile'] = filename
        dic['sys_err'] = dic['sys_err_default']
        if len(filename.split('# ')) == 2:
            dic['sys_err'] = float(filename.split('# ')[1])
            filename = filename.split('# ')[0]
        if dic['outputs']:
            dic['currentoutput'] = dic['outputs'].pop(0)
        dic['numbered'] = 0

        # Now read data file
        data = read_data(filename)

        # Make decisions about what is in the file
        if len(data) > 0:
            struct = detect_blocks(data)

            # KN: This can be done far more efficiently using a filter()
            # function. Either specify a one liner using a lambda function or
            # write a function that returns True or False
            struct, data = remove_empties(struct, data)

            # Plot the stuff
            for i in range(len(struct)):
                dic['currentstruct'] = i
                dic['Numbering'] = len(struct) > 1
                x = readdat(struct, i, data)
                unstruct_plot(np.array(x))

    if dic['remnants']:
        plot(dic['remnants'], dic['remnanterrors'], Force=True)


if __name__ == '__main__':
    """A Python program that takes a file or list of filesand creates plots of
    the data."""
    dic = globe.dic
    main()
