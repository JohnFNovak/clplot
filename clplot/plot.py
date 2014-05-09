#!/usr/bin/env python

# A universal command line plotting script
#
# John Novak
# June 4, 2012 - July 19, 2012

# this sub-file holds the functions relating to generating the output

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
        if dic['EmbedData']:
            EmbedData(outputname, z, errs)
        #check = subprocess.call(['open', outputname])
        plt.clf()
        dic['LefttoPlot'] = False

    if dic['MULTIT'] and dic['multicounttile'] == int(dic['MULTIT']):
            dic['multicounttile'] = 0


def read_flags():
    dic = globe.dic
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


def EmbedData(outputname, z, errs):
    StringToEmbed = "Creation time: " + time.ctime() + '\n'
    StringToEmbed += "Current directory: " + os.path.abspath('.') + '\n'
    StringToEmbed += "Creation command: " + ' '.join(sys.argv) + '\n'
    StringToEmbed += "Plotted values:" + '\n'
    for k in range(0, len(z), 2):
        StringToEmbed += 'x ' + ' '.join(map(str, z[k])) + '\n'
        StringToEmbed += 'x err ' + ' '.join(map(str, errs[k])) + '\n'
        StringToEmbed += 'y ' + ' '.join(map(str, z[k + 1])) + '\n'
        StringToEmbed += 'y err ' + ' '.join(map(str, errs[k + 1])) + '\n'
    with open(outputname, 'a') as f:
        if dic['TYPE'] == '.jpg':
            f.write(StringToEmbed)


if __name__ == '__main__':
    print "This code is part of CLP"
