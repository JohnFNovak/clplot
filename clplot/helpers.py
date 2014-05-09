#!/usr/bin/env python

# A universal command line plotting script
#
# John Novak

# This sub-file contains helper functions

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import collections
import itertools
import string


def is_it_ordered(vals):
    """This function takes a list of numbers are returns whether or not they are in order"""

    ordered = False

    if vals == sorted(vals):
        ordered = True
    if vals == sorted(vals, reverse=True):
        ordered = True

    return ordered


def remove_empties(struct, x):
    """This function runs through the data and the structure array and removes entries that are either empty or are singular"""

    linenum = len(x)-1
    structBK = struct
    count = 0
    blocks = len(structBK)

    for i in range(blocks):
        j = -i - 1 + count  # do this backward
        if structBK[j][0] > 1 and structBK[j][1] > 1:
            # the entry is good: it's more than a single column or single line
            linenum = linenum - struct[j][1]
        else:
            # the entry is worthless: it's a single line
            del struct[len(structBK) + j]
            del x[linenum]
            linenum = linenum - 1
            count = count + 1

    return struct, x


def check_type(x):
    """This function returns a string. It returns "str" if x is a string, and "num" if x is a number"""
    try:
        float(x)
    except ValueError:
        verdict = "str"
    else:
        verdict = "num"

    return verdict


def skip(iterator, n):
    '''Advance the iterator n-steps ahead. If n is none, consume entirely.'''
    collections.deque(itertools.islice(iterator, n), maxlen=0)


def remove_formating(data):
    """This function removes thigns that will cause problems like endlines"""
    cleaned = []
    for i in data:
        temp = []
        for j in i:
            temp2 = []
            for k in j:
                if (k != '\n') and (k != '') and (k != '\r'):
                    temp2.append(k)
            if(len(temp2) > 0):
                temp.append(string.join(temp2, ''))
        cleaned.append(temp)

    return cleaned


def givehelp(a):
    """This command prints out some help"""

    print """This is a function which trys to inteligently create plots from text files. This program is 'inteligent' in that it will try various assumptions about the format of the data in the files and the form the output should be given in. So, in many cases it can produce reasonable plots even if no information is provided by the user other than the filenames\n"""
    if a == 0:
        print "for more help call this program with the '-help' flag"
    if a == 1:
        print """This program takes a number of flags:
        -i: Input. The input files can be listed first, or they can be listed following the '-i' flag.
        -o: Output. The output files will be given the same names as the input files unless otherwise specified. The output files can be specifiec by listing them after the '-o' flag
        -f: Format: the format of the data in the input files can be specified with '-f'. Each format flag should start with either 'c' or 'r', specifying wether the data should be read as columns or row. The following characters each represent a row or column. They can be: 'x', 'y', '_', '*', or a numeral (<10). 'x' specifies the x values, 'y' specifies 'y' values'. Rows or columens marked with '_' will be skipped. 'y's or '_'s can be proceeded by a numeral, and the 'y' or '_' will be read that many times. Formats will only be used if their dimensions exactly fit the data found in the file, unless the format string is ended with a '*', then the format will be used of any data found in the file which has dimensions greater than or equal to that stated in the format flag.
        -mp: Multiplot Pile. This flag should be followed by the number of y's which the user wants to have plotted in the same window. It should be noted that if one block of text contains multiple y columns or rows, the '-mp' flag will cause them to be treated individually
        -mt: Multiplot Tile. This flag should be followed by the number of tiles desired for each plot printed to file
        -t: Type. The '-t' flag can be used to change the output type. The following are acceptable: bmp, emf, eps, gif, jpeg, jpg, pdf, png, ps, raw, rgba, svg, svgz, tif, tiff
        -c: Color. The '-c' flag can be used to set the color. Multiple colors can be specified and they will be iterated over. The color options are: b, g, r, c, m, y, k
        -s: Point Style: The '-s' flag can be used to specify the point style. Multiple styles can be specified and they will be iterated over. The point style options are:-, --, -., :, ., , , o, v, ^, <, >, 1, 2, 3, 4, s, p, *, h, H, +, x, D, d, |, _ . To plot with hollow points, append the style with '!'. Note that it may be necessary to put a style in quotes because the command line my try to interpret it.
        -cs: Color/Style, or Custom Style: The '-cs' flag can be used to directly specify the point color and style to be used. All of the colors and styles listed previously will work. The flags must be a valid color followed (without a space) by a valid point style. Ex: blue, big diamond, hollow -'bD!'
        -xl, -yl: Set X and y labels. SHould be followed by a string, which can be in quotes
        -logx, -logy: set X and/or Y axes to be log scales
        -xr, -yr: Set scale of X and Y ranges, should be followed with two numbers sepearated by a colon. Ex: -xr 1:5
        -layout: Used to specify the tiled output layout. Write input as <# rows>:<# columns>
        -legend: This will turn on keys in the plots. On each plot things will be named using a unique combination of column heading, column number, and filename
        -bands: This will plot all y error bars as y error bands
        -fontsize: This sets the size of the font used for axis labels and titles. The default it 20.
        -grid : This turns on background grids
        -systematic: This sets the size of the systematic error. It is a percent and is added to the y error bars.
        -sys_err: This turns on the plotting of systematic errors.
        -markersize: changes the default marker size. Default 5
        -yscaled: Scale all of the y values by a constant number
        -xscaled: Scale all of the x values by a constant number
        -alpha: Sets the 'opaque-ness' of shaded objects (like error bars). Number [0, 1], default 0.25
        -norm: Normalizes all plots

        Example:
            I have a large number of files and I would like them to be plotted with 9 plots tiled per output. I would like them to be eps files, and I have a thing for green circles. In each file the data is in columns 6 wide, but I only want the first and fourth columns plotted. The first column is x, the other will be y. I would type:
            # python plot.py * -t eps -mt 9 -c b -s o -f x3_y*"""

    exit(1)


if __name__ == '__main__':
    print "This code is part of CLP"
