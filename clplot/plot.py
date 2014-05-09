#!/usr/bin/env python

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
import os
import time
import string
import globe
from structure import *
from helpers import *


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

    if dic['outputs'] and (len(dic['outputs']) != len(dic['files'])) and not (dic['MULTIT'] or dic['MULTIP']):
        print "If you are going to specify output names,",
        print "you must specify one output file per input file."

    for filename in dic['files']:
        print "plotting", filename
        dic['currentfile'] = filename
        dic['sys_err'] = dic['sys_err_default']
        if len(filename.split('#')) == 2:
            dic['sys_err'] = float(filename.split('#')[1])
            filename = filename.split('#')[0]
        if dic['outputs']:
            dic['currentoutput'] = dic['outputs'].pop(0)
        dic['numbered'] = 0

        # Now read data file
        data = read_data(filename)

        # Make decisions about what is in the file
        if len(data) > 0:
            struct = detect_blocks(data)

            # KN: This can be done far more efficiently using a filter() \
            # function. Either specify a one liner using a lambda function or
            # write a function that returns True or False
            struct, data = remove_empties(struct, data)

            # Plot the stuff
            # KN: Not needed. Make sure the struct is a list, and just have \
            # the for loop, followed by Numbering = len(struct) > 1
            if len(struct) > 1:
                # make multiple plots, each with the name of the input file \
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
            outputname = outputname + "_" + str(dic['numbered'])
        if dic['MULTIT']:
            outputname = outputname + "_tiled"
        if dic['multicountpile'] != 0:
            outputname = outputname + "_" + str(dic['multicountpile'] + 1)
        if dic['MULTIP']:
            outputname = outputname + "_multip"
        if dic['TYPE'][0] == ".":
            outputname = outputname + dic['TYPE']
        else:
            outputname = outputname + "." + dic['TYPE']
        plt.savefig(outputname)
        print"printed to", outputname


def detect_blocks(dataarray):
    """This function runs over an array of data pulled from a file and \
    detects the structure so that the proper plotting method can be deduced \
    the structure is returned as a list. Each entry is one block of the data \
    in the form of (width of block, height of block) This will detect \
    contiguous rectangular blocks of data with the same formats of text vs \
    numbers"""
    dic = globe.dic

    width = []
    height = []
    block = 0
    structure = []
    previous = []

    width.append(len(dataarray[0]))
    height.append(1)
    mixed = False
    for i in range(len(dataarray[0])):
        if check_type(dataarray[0][i]) == 'str':
            previous.append(check_type(dataarray[0][i]))
            if i != 0:
                mixed = True
                dic['Messy'] = True
        else:
            previous.append(check_type(dataarray[0][i]))
    if mixed:
        print "you seem to have text interspersed with your data"
        print "Does this look familiar?:", ' '.join(dataarray[0])
    if mixed and len(dataarray[0]) == len(dataarray[1]):
        print "we are going to use", string.join(dataarray[0]), "as labels"
        dic['columnlabel'].append(dataarray[0])
    else:
        dic['columnlabel'].append(range(len(dataarray[0])))

    for i in range(1, len(dataarray)):
        mixed = False
        if(len(dataarray[i]) == width[block]):
            good = True
            for x in range(len(dataarray[i])):
                if check_type(dataarray[i][x]) != previous[x]:
                    good = False
            if good:
                height[block] = height[block] + 1
            else:
                block = block + 1
                height.append(1)
                width.append(len(dataarray[i]))
                previous = []
                for x in range(len(dataarray[i])):
                    if check_type(dataarray[i][x]) == 'str':
                        previous.append(check_type(dataarray[i][x]))
                        if x != 0:
                            mixed = True
                            dic['Messy'] = True
                    else:
                        previous.append(check_type(dataarray[i][x]))
            if mixed:
                print "you seem to have text interspersed with your data"
                print "Does this look familiar?:", ' '.join(dataarray[i])
            if mixed and len(dataarray) != i + 1:
                if len(dataarray[i]) == len(dataarray[i + 1]):
                    print "we are going to use", string.join(dataarray[i]),
                    print "as labels"
                    dic['columnlabel'].append(dataarray[i])
            else:
                dic['columnlabel'].append(range(len(dataarray[i])))
        else:
            block = block + 1
            height.append(1)
            width.append(len(dataarray[i]))
            previous = []
            for x in range(len(dataarray[i])):
                if check_type(dataarray[i][x]) == 'str':
                    previous.append(check_type(dataarray[i][x]))
                    if x != 0:
                        mixed = True
                        dic['Messy'] = True
                else:
                    previous.append(check_type(dataarray[i][x]))
            if mixed:
                print "you seem to have text interspersed with your data"
                print "Does this look familiar?:", ' '.join(dataarray[i])
            if mixed and len(dataarray) != i + 1:
                if len(dataarray[i]) == len(dataarray[i + 1]):
                    print "we are going to use", string.join(dataarray[i]),
                    print "as labels"
                    dic['columnlabel'].append(dataarray[i])
            else:
                dic['columnlabel'].append(range(len(dataarray[i])))

    for i in range(block + 1):
        #print "block", i, "is", width[i], "by", height[i]
        structure.append((width[i], height[i]))

    return structure


def is_it_ordered(vals):
    """This function takes a list of numbers are returns whether or not they \
    are in order"""

    ordered = False

    if vals == sorted(vals):
        ordered = True
    if vals == sorted(vals, reverse=True):
        ordered = True

    return ordered


def remove_empties(struct, x):
    """This function runs through the data and the structure array and \
    removes entries that are either empty or are singular"""

    linenum = len(x)-1
    structBK = struct
    count = 0
    blocks = len(structBK)

    for i in range(blocks):
        j = -i - 1 + count  # do this backward
        if structBK[j][0] > 1 and structBK[j][1] > 1:
            # the entry is good: it's more than a single column or single line
            linenum = linenum-struct[j][1]
        else:
            # the entry is worthless: it's a single line
            del struct[len(structBK) + j]
            del x[linenum]
            linenum = linenum-1
            count = count + 1

    return struct, x


def readdat(struct, block, data):
    x = []
    linenum = 0

    for i in range(len(struct)):
        if i == block:
            # this is the block you want
            for j in range(struct[i][1]):
                k = j + linenum
                x.append(data[k])
            break
        else:
            # count how many lines down you have to look
            linenum = linenum + struct[i][1]
    return x


def plot(z, errs):
    """This function takes a list z of lists and trys to plot them. the first \
    list is always x, and the folowing are always y's"""

    #print z
    #print errs

    dic = globe.dic
    points = dic['colorstyle']

    if dic['Ucolor']:
        colors = dic['Ucolor']
    else:
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    if dic['Ustyle']:
        style = dic['Ustyle']
    else:
        style = ['o', 'v', '^', '<', ' > ', '1', '2', '3', '4', '-', '--',
                 '-.', ':', 's', 'p', '*', 'h', 'H', ' + ', 'x', 'D', 'd', '|',
                 '_', '.', ', ']
    for s in style:
        for c in colors:
            points.append(str(c + s))

    size = [dic['default_marker_size']]*len(points)
    for i in range(len(points)):
        if len(points[i].split(';')) == 2:
            points[i] = points[i].split(';')[0]
            size[i] = float(points[i].split(';')[1])

    if dic['MULTIT']:
        dic['multicounttile'] = dic['multicounttile'] + 1
        if not dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0], dic['layout'][1]), (((dic['multicounttile']-1)-(dic['multicounttile']-1)%dic['layout'][1])/dic['layout'][1], ((dic['multicounttile']-1)%dic['layout'][1])))
        if dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0], dic['layout'][1]), ((dic['multicounttile']-1)%dic['layout'][1])), (((dic['multicounttile']-1)-(dic['multicounttile']-1)%dic['layout'][1])/dic['layout'][1])
        #plt.title(str(dic['multicounttile']), fontsize = dic['fontsize'])
        dic['LefttoPlot'] = True

    plottingerrors = True
    #for k in errs:
    #    if k != 0:
    #        plottingerrors = True

    arg = []

    if dic['x_range']:
        plt.xlim(dic['x_range'])
    if dic['y_range']:
        plt.ylim(dic['y_range'])
    if dic['x_label']:
        plt.xlabel(dic['x_label'], fontsize=dic['fontsize'])
    if dic['y_label']:
        plt.ylabel(dic['y_label'], fontsize=dic['fontsize'])
    if dic['x_log']:
        plt.xscale('log', nonposx='clip')
    if dic['y_log']:
        plt.yscale('log', nonposy='clip')

    plt.tick_params(axis='both', which='major', labelsize=dic['fontsize']*0.75)
    plt.tick_params(axis='both', which='minor', labelsize=dic['fontsize']*0.75)

    if dic['legend'] and len(dic['labels']) > 1:
        parse_legend()

    if dic['norm']:
        for k in range(0, len(z), 2):
            X = np.array(z[k]).astype(float)
            Y = np.array(z[k + 1]).astype(float)
            width = np.mean(X[1:] - X[:-1])
            Y = Y / np.sum(Y * width)
            z[k + 1] = Y.tolist()

    for k in range(0, len(z), 2):
        marker = points[((k + 1) / 2) % len(points)]
        msize = size[((k + 1) / 2) % len(points)]
        ecolor = points[((k + 1) / 2) % len(points)][0]
        fcolor = points[((k + 1) / 2) % len(points)][0]
        if marker[-1] == '!':
            fcolor = 'white'
            marker = marker[:-1]
        z[k] = map(lambda x: float(x) * dic['xscaled'], z[k])
        z[k + 1] = map(lambda x: float(x) * dic['yscaled'], z[k + 1])
        #z[k + 1] = map(float, z[k + 1])
        if plottingerrors and not dic['errorbands']:
            if errs[k][0] == 0:
                errs[k][0] = [0]*len(z[k])
            else:
                errs[k][0] = map(lambda x: float(x) * dic['xscaled'], errs[k][0])
            if errs[k + 1][0] == 0:
                plt.errorbar(z[k], z[k + 1], xerr=errs[k][0], yerr=[0]*len(z[k + 1]), fmt=marker, label=dic['labels'][(k + 1)/2], mec=ecolor, mfc=fcolor, ms=msize)
            if errs[k + 1][0] != 0:
                errs[k + 1][0] = map(lambda x: float(x) * dic['yscaled'], errs[k + 1][0])
                plt.errorbar(z[k], z[k + 1], xerr=errs[k][0], yerr=errs[k + 1][0], fmt=marker, label=dic['labels'][(k + 1)/2], mec=ecolor, mfc=fcolor, ms=msize)
        if plottingerrors and dic['errorbands']:
            if errs[k][0] == 0:
                errs[k][0] = [0]*len(z[k])
            else:
                errs[k][0] = map(lambda x: float(x) * dic['xscaled'], errs[k][0])
            if errs[k + 1][0] == 0:
                plt.errorbar(z[k], z[k + 1], xerr=[0]*len(errs[k][0]), yerr=[0]*len(z[k + 1]), fmt=marker, label=dic['labels'][(k + 1)/2], mec=ecolor, mfc=fcolor, ms=msize)
            if errs[k + 1][0] != 0:
                errs[k + 1][0] = map(lambda x: float(x) * dic['yscaled'], errs[k + 1][0])
                plt.errorbar(z[k], z[k + 1], xerr=[0]*len(errs[k][0]), yerr=[0]*len(errs[k + 1][0]), fmt=marker, label=dic['labels'][(k + 1)/2], mec=ecolor, mfc=fcolor, ms=msize)
                plt.fill_between(np.array(z[k]), np.array(z[k + 1]) + np.array(errs[k + 1][0]), np.array(z[k + 1])-np.array(errs[k + 1][0]), facecolor=ecolor, alpha=dic['alpha'], interpolate=True, linewidth=0)
        if dic['plot_sys_err']:
            plt.fill_between(np.array(z[k]), np.array(z[k + 1]) + np.array(errs[k + 1][1]), np.array(z[k + 1])-np.array(errs[k + 1][1]), facecolor=ecolor, alpha=dic['alpha'], interpolate=True, linewidth=0)
        if not plottingerrors:
            arg.append(z[k])  # x vector
            arg.append(z[k + 1])
            arg.append(points[(k / 2) % len(points)])

    if not plottingerrors:
        plt.plot(*arg)

    plt.grid(dic['grid'])

    if dic['legend']:
        plt.legend()
        dic['labels'] = []

    if dic['currentoutput']:
        outputname = dic['currentoutput']
    else:
        outputname = string.split(dic['currentfile'], ".")[0]

    if dic['numbered'] != 0:
        outputname = outputname + "_" + str(dic['numbered'])
    if dic['MULTIT']:
        outputname = outputname + "_tiled"
    if dic['multicountpile'] != 0:
        outputname = outputname + "_" + str(dic['multicountpile'])
    if dic['MULTIP']:
        outputname = outputname + "_multip"
    if dic['TYPE'][0] == ".":
        outputname = outputname + dic['TYPE']
    else:
        outputname = outputname + "." + dic['TYPE']

    if not dic['MULTIT'] or (dic['MULTIT'] and dic['multicounttile'] == int(dic['MULTIT'])):
        plt.tight_layout()  # Experimental, and may cause problems
        plt.savefig(outputname)
        print"printed to", outputname
        f = open(outputname, 'a')
        f.write("Creation time: " + time.ctime() + '\n')
        f.write("Current directory: " + os.path.abspath('.') + '\n')
        f.write("Creation command: " + ' '.join(sys.argv) + '\n')
        f.write("Plotted values:" + '\n')
        for k in range(0, len(z), 2):
            f.write('x ' + ' '.join(map(str, z[k])) + '\n')
            f.write('x err ' + ' '.join(map(str, errs[k])) + '\n')
            f.write('y ' + ' '.join(map(str, z[k + 1])) + '\n')
            f.write('y err ' + ' '.join(map(str, errs[k + 1])) + '\n')
        f.close()
        #check = subprocess.call(['open', outputname])
        plt.clf()
        dic['LefttoPlot'] = False

    if dic['MULTIT'] and dic['multicounttile'] == int(dic['MULTIT']):
            dic['multicounttile'] = 0


def check_type(x):
    """This function returns a string. It returns "str" if x is a string, """\
        """and "num" if x is a number"""
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


def read_data(filename):
    data = []
    datafile = open(filename, "r")

    test = datafile.readline()
    while test[0] == "#" and len(test) > 1:  # Not a comment or empty
        test = datafile.readline()
    delimiter = " "
    if len(test.split(" ")) > 1:
        delimiter = " "
    elif len(test.split(", ")) > 1:
        delimiter = ", "
    elif len(test.split(";")) > 1:
        delimiter = ";"
    elif len(test.split(".")) > 1:
        delimiter = "."
    else:
        print "Um, we can't figure out what you are using for data seperation"

    datafile.seek(0)
    for line in datafile:
        data.append(tuple(line.split(delimiter)))
    datafile.close()

    data = remove_formating(data)
    return data


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
