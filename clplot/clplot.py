#!/usr/bin/env python

# A universal command line plotting script
#
# John Novak
# June 4, 2012 - July 19, 2012

# Run with: python plot.py
# or just: ./plot.py (after making it executable, obviously)

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
            # KN: Not needed. Make sure the struct is a list, and just have the
            # for loop, followed by Numbering = len(struct) > 1
            if len(struct) > 1:
                # make multiple plots, each with the name of the input file
                # followed by a _
                for i in range(len(struct)):
                    dic['currentstruct'] = i
                    dic['Numbering'] = True
                    x = readdat(struct, i, data)
                    unstruct_plot(np.array(x))
            else:
                # just make one plot, with the same name as the input file
                x = readdat(struct, 0, data)
                unstruct_plot(np.array(x))

    if dic['remnants']:
        plot(dic['remnants'], dic['remnanterrors'])

    if dic['LefttoPlot']:
        outputname = string.split(dic['currentfile'], ".")[0]
        if dic['numbered'] != 0:
            outputname = outputname+"_"+str(dic['numbered'])
        if dic['MULTIT']:
            outputname = outputname+"_tiled"
        if dic['multicountpile'] != 0:
            outputname = outputname+"_"+str(dic['multicountpile']+1)
        if dic['MULTIP']:
            outputname = outputname+"_multip"
        if dic['TYPE'][0] == ".":
            outputname = outputname+dic['TYPE']
        else:
            outputname = outputname+"."+dic['TYPE']
        plt.savefig(outputname)
        print"printed to", outputname


if __name__ == '__main__':
    """A Python program that takes a file or list of filesand creates plots of
    the data."""
    global dic  # All global values are being dumped in here
    dic = globe.dic
    main()
