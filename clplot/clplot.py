# !/usr/bin/python

# A universal command line plotting script
#
# John Novak
# June 4, 2012 - July 19, 2012

# Run with: python plot.py
# or just: ./plot.py (after making it executable, obviously)

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import sys
import numpy as np
import matplotlib.pyplot as plt
import string
import globe
from structure import *
from helpers import *
from plot import *
from data_handler import *


def main():
    global dic

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


def read_flags():
    global dic
    case = 0  # 0 is reading files, 1 is outputs, 2 is formats, etc

    if len(sys.argv) == 1:
        givehelp(0)

    for flag in sys.argv[1:]:
        # performance tweak: Check if the flag has a dash in it first,
        # otherwise its a filename, i.e. "if '-' in flag: "
        if "-f" == flag:
            # format flag
            case = 2
        elif "-i" == flag:
            # input file flag
            case = 0
        elif "-o" == flag:
            # output file flag
            case = 1
        elif "-t" == flag:
            # output type flag
            case = 3
        elif "-mp" == flag:
            # multiplot pile flag
            case = 4
        elif "-mt" == flag:
            # multiplot tile flag
            case = 5
        elif "-h" == flag[:2]:
            givehelp(1)
        elif "-c" == flag:
            case = 6
        elif "-s" == flag:
            case = 7
        elif "-xr" == flag:
            case = 8
        elif "-yr" == flag:
            case = 9
        elif "-xl" == flag:
            case = 10
        elif "-yl" == flag:
            case = 11
        elif "-logx" == flag:
            dic['x_log'] = True
            if dic['x_range']:
                if dic['x_range'][0] <= 0:
                    dic['x_range'] = None
        elif "-logy" == flag:
            dic['y_log'] = True
            if dic['y_range']:
                if dic['y_range'][0] <= 0:
                    dic['y_range'] = None
        elif '-layout' == flag:
            case = 12
        elif '-cs' == flag:
            case = 13
        elif '-fontsize' == flag:
            case = 14
        elif '-systematic' == flag:
            case = 15
        elif '-xscaled' == flag:
            case = 16
        elif '-yscaled' == flag:
            case = 17
        elif '-markersize' == flag:
            case = 18
        elif '-alpha' == flag:
            case = 19
        elif '-columnsfirst' == flag:
            dic['columnsfirst'] = True
        elif "-legend" == flag:
            dic['legend'] = True
        elif '-bands' == flag:
            dic['errorbands'] = True
        elif '-grid' == flag:
            dic['grid'] = True
        elif '-sys_err' == flag:
            dic['plot_sys_err'] = True
        elif '-norm' == flag:
            dic['norm'] = True
        elif "-" == flag[0] and case != 7 and case != 8 and case != 9:
            case = -1
            print "flag", flag, "not recognized"
        else:
            # if there is not a flag, and we are reading filenames or formats
            if case == 0:
                dic['files'].append(flag)
            if case == 1:
                dic['outputs'].append(flag)
            if case == 2:
                dic['formats'].append(flag)
            if case == 3:
                dic['TYPE'] = flag
            if case == 4:
                dic['MULTIP'] = flag  # number of plots per plot
            if case == 5:
                dic['MULTIT'] = flag  # number of plots per plot
            if case == 6:
                dic['Ucolor'].append(flag)
            if case == 7:
                dic['Ustyle'].append(flag)
            if case == 8:
                dic['x_range'] = map(float, flag.split(":"))
            if case == 9:
                dic['y_range'] = map(float, flag.split(":"))
            if case == 10:
                dic['x_label'] = flag
            if case == 11:
                dic['y_label'] = flag
            if case == 12:
                dic['layout'] = tuple(map(int, flag.split(":")))
            if case == 13:
                dic['colorstyle'].append(flag)
            if case == 14:
                dic['fontsize'] = float(flag)
            if case == 15:
                dic['sys_err_default'] = float(flag)
            if case == 16:
                dic['xscaled'] = float(flag)
            if case == 17:
                dic['yscaled'] = float(flag)
            if case == 18:
                dic['default_marker_size'] = float(flag)
            if case == 19:
                dic['alpha'] = float(flag)
            if case == -1:
                print "ignoring", flag


def parse_legend():
    global dic
    # delimiters = ['/', '-', '.', '/', '-', '.']
    delimiters = ['/', '-']

    for divider in delimiters:
        tester = dic['labels'][0].split(divider)

        # From the front
        for i in dic['labels']:
            if len(i.split(divider)) > len(tester):
                tester = i.split(divider)
        hold = [0]*len(tester)

        for i in range(1, len(dic['labels'])):
            for j in range(len(dic['labels'][i].split(divider))):
                if tester[j] == dic['labels'][i].split(divider)[j] and hold[j]\
                   == 0:
                    hold[j] = 1
                if tester[j] != dic['labels'][i].split(divider)[j] and hold[j]\
                   == 1:
                    hold[j] = 0

        for i in range(len(hold)):
            if hold[len(hold)-1-i] == 1:
                for j in range(len(dic['labels'])):
                    temp = []
                    for k in range(len(dic['labels'][j].split(divider))):
                        if k != len(hold) - 1 - i:
                            temp.append(dic['labels'][j].split(divider)[k])
                    dic['labels'][j] = string.join(temp, divider)

        tester = dic['labels'][0].split(divider)

        # From the back
        for i in dic['labels']:
            if len(i.split(divider)) > len(tester):
                tester = i.split(divider)
        hold = [0]*len(tester)

        for i in range(1, len(dic['labels'])):
            temp = len(dic['labels'][i].split(divider)) - 1 - j
            temp_labels = dic['labels'][i].split(divider)
            for j in range(temp):
                if tester[temp] == temp_labels[temp] and hold[temp] == 0:
                    hold[temp] = 1
                if tester[temp] != temp_labels[temp] and hold[temp] == 1:
                    hold[temp] = 0

        for i in range(len(hold)):
            if hold[len(hold)-1-i] == 1:
                for j in range(len(dic['labels'])):
                    temp = []
                    for k in range(len(dic['labels'][j].split(divider))):
                        if k != len(hold)-1-i:
                            temp.append(dic['labels'][j].split(divider)[k])
                    dic['labels'][j] = string.join(temp, divider)


def givehelp(a):
    """This command prints out some help"""

    print """This is a function which trys to inteligently create plots from \
text files. This program is 'inteligent' in that it will try various \
assumptions about the format of the data in the files and the form the output \
should be given in. So, in many cases it can produce reasonable plots even if \
no information is provided by the user other than the filenames\n"""
    if a == 0:
        print "for more help call this program with the '-help' flag"
    if a == 1:
        print """This program takes a number of flags:
        -i: Input. The input files can be listed first, or they can be listed \
following the '-i' flag.\n
        -o: Output. The output files will be given the same names as the \
input files unless otherwise specified. The output files can be specifiec \
by listing them after the '-o' flag
        -f: Format: the format of the data in the input files can be \
specified with '-f'. Each format flag should start with either 'c' or 'r', \
specifying wether the data should be read as columns or row. The following \
characters each represent a row or column. They can be: 'x', 'y', '_', '*', \
or a numeral (<10). 'x' specifies the x values, 'y' specifies 'y' values'. \
Rows or columens marked with '_' will be skipped. 'y's or '_'s can be \
proceeded by a numeral, and the 'y' or '_' will be read that many times. \
Formats will only be used if their dimensions exactly fit the data found in \
the file, unless the format string is ended with a '*', then the format will \
be used of any data found in the file which has dimensions greater than or \
equal to that stated in the format flag.
        -mp: Multiplot Pile. This flag should be followed by the number of \
y's which the user wants to have plotted in the same window. It should be \
noted that if one block of text contains multiple y columns or rows, the \
'-mp' flag will cause them to be treated individually
        -mt: Multiplot Tile. This flag should be followed by the number of \
tiles desired for each plot printed to file
        -t: Type. The '-t' flag can be used to change the output type. The \
following are acceptable: bmp, emf, eps, gif, jpeg, jpg, pdf, png, ps, raw, \
rgba, svg, svgz, tif, tiff
        -c: Color. The '-c' flag can be used to set the color. Multiple \
colors can be specified and they will be iterated over. The color options \
are: b, g, r, c, m, y, k
        -s: Point Style: The '-s' flag can be used to specify the point \
style. Multiple styles can be specified and they will be iterated over. The \
point style options are:-, --, -., :, ., , , o, v, ^, <, >, 1, 2, 3, 4, s, p, \
*, h, H, +, x, D, d, |, _ . To plot with hollow points, append the style with \
'!'. Note that it may be necessary to put a style in quotes because the \
command line my try to interpret it.
        -cs: Color/Style, or Custom Style: The '-cs' flag can be used to \
directly specify the point color and style to be used. All of the colors and \
styles listed previously will work. The flags must be a valid color followed \
(without a space) by a valid point style. Ex: blue, big diamond, hollow -'bD!'
        -xl, -yl: Set X and y labels. SHould be followed by a string, \
which can be in quotes
        -logx, -logy: set X and/or Y axes to be log scales
        -xr, -yr: Set scale of X and Y ranges, should be followed with two \
numbers sepearated by a colon. Ex: -xr 1:5
        -layout: Used to specify the tiled output layout. Write input as <# \
rows>:<# columns>
        -legend: This will turn on keys in the plots. On each plot things \
will be named using a unique combination of column heading, column number, \
and filename
        -bands: This will plot all y error bars as y error bands
        -fontsize: This sets the size of the font used for axis labels and \
titles. The default it 20.
        -grid : This turns on background grids
        -systematic: This sets the size of the systematic error. It is a \
percent and is added to the y error bars.
        -sys_err: This turns on the plotting of systematic errors.
        -markersize: changes the default marker size. Default 5
        -yscaled: Scale all of the y values by a constant number
        -xscaled: Scale all of the x values by a constant number
        -alpha: Sets the 'opaque-ness' of shaded objects (like error bars). \
Number [0, 1], default 0.25
        -norm: Normalizes all plots

        Example:
            I have a large number of files and I would like them to be \
lpotted with 9 plots tiled per output. I would like them to be eps files, and \
I have a thing for green circles. In each file the data is in columns 6 wide, \
but I only want the first and fourth columns plotted. The first column is x, \
the other will be y. I would type:
            # python plot.py * -t eps -mt 9 -c b -s o -f x3_y*"""

    exit(1)


if __name__ == '__main__':
    """A Python program that takes a file or list of filesand creates plots of
    the data."""
    global dic  # All global values are being dumped in here
    dic = globe.dic
    main()
