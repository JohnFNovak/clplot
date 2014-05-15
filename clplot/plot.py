#! /usr/bin/env python

# Part of CLP
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


def plot(z, errs, Force=False):
    """This function takes a list z of lists and trys to plot them. the first
    list is always x, and the folowing are always y's"""

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
        dic['mct'] = dic['mct'] + 1
        if not dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0], dic['layout'][1]),
                             (((dic['mct'] - 1) - (dic['mct'] - 1) %
                               dic['layout'][1]) / dic['layout'][1],
                              ((dic['mct'] - 1) % dic['layout'][1])))
        if dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0], dic['layout'][1]),
                             ((dic['mct'] - 1) % dic['layout'][1]),
                             (((dic['mct'] - 1) - (dic['mct'] - 1) %
                              dic['layout'][1]) / dic['layout'][1]))

    plottingerrors = True

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
        z[k] = [float(x) * dic['xscaled'] for x in z[k]]
        z[k + 1] = [float(x) * dic['yscaled']for x in z[k + 1]]
        if plottingerrors and not dic['errorbands']:
            if errs[k][0] == 0:
                errs[k][0] = [0] * len(z[k])
            else:
                errs[k][0] = [float(x) * dic['xscaled'] for x in errs[k][0]]
            if errs[k + 1][0] == 0:
                plt.errorbar(z[k], z[k + 1],
                             xerr=errs[k][0],
                             yerr=[0] * len(z[k + 1]),
                             fmt=marker, label=dic['labels'][(k + 1) / 2],
                             mec=ecolor, mfc=fcolor, ms=msize)
            if errs[k + 1][0] != 0:
                errs[k + 1][0] = [float(x) * dic['yscaled']
                                  for x in errs[k + 1][0]]
                plt.errorbar(z[k], z[k + 1],
                             xerr=errs[k][0],
                             yerr=errs[k + 1][0],
                             fmt=marker, label=dic['labels'][(k + 1) / 2],
                             mec=ecolor, mfc=fcolor, ms=msize)
        if plottingerrors and dic['errorbands']:
            if errs[k][0] == 0:
                errs[k][0] = [0] * len(z[k])
            else:
                errs[k][0] = [float(x) * dic['xscaled'] for x in errs[k][0]]
            if errs[k + 1][0] == 0:
                plt.errorbar(z[k], z[k + 1],
                             xerr=[0] * len(errs[k][0]),
                             yerr=[0] * len(z[k + 1]),
                             fmt=marker, label=dic['labels'][(k + 1) / 2],
                             mec=ecolor, mfc=fcolor, ms=msize)
            if errs[k + 1][0] != 0:
                errs[k + 1][0] = [float(x) * dic['yscaled']
                                  for x in errs[k + 1][0]]
                plt.errorbar(z[k], z[k + 1],
                             xerr=[0] * len(errs[k][0]),
                             yerr=[0] * len(errs[k + 1][0]),
                             fmt=marker, label=dic['labels'][(k + 1) / 2],
                             mec=ecolor, mfc=fcolor, ms=msize)
                plt.fill_between(np.array(z[k]),
                                 np.array(z[k + 1]) + np.array(errs[k + 1][0]),
                                 np.array(z[k + 1]) - np.array(errs[k + 1][0]),
                                 facecolor=ecolor, alpha=dic['alpha'],
                                 interpolate=True, linewidth=0)
        if dic['plot_sys_err']:
            plt.fill_between(np.array(z[k]),
                             np.array(z[k + 1]) + np.array(errs[k + 1][1]),
                             np.array(z[k + 1]) - np.array(errs[k + 1][1]),
                             facecolor=ecolor, alpha=dic['alpha'],
                             interpolate=True, linewidth=0)
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
    if dic['mcp'] != 0:
        if Force:
            outputname = outputname + "_" + str(dic['mcp'] + 1)
        else:
            outputname = outputname + "_" + str(dic['mcp'])
    if dic['MULTIP']:
        outputname = outputname + "_multip"
    if dic['TYPE'][0] == ".":
        outputname = outputname + dic['TYPE']
    else:
        outputname = outputname + "." + dic['TYPE']

    if not dic['MULTIT'] or (dic['MULTIT'] and dic['mct'] ==
                             int(dic['MULTIT'])) or Force:
        plt.tight_layout()  # Experimental, and may cause problems
        plt.savefig(outputname)
        if dic['Verbose'] > 0:
            print"printed to", outputname
        if dic['EmbedData']:
            EmbedData(outputname, z, errs)
        #check = subprocess.call(['open', outputname])
        plt.clf()

    if dic['MULTIT'] and dic['mct'] == int(dic['MULTIT']):
            dic['mct'] = 0


def parse_legend():
    dic = globe.dic
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
    dic = globe.dic
    StringToEmbed = "Creation time: " + time.ctime() + '\n'
    StringToEmbed += "Current directory: " + os.path.abspath('.') + '\n'
    StringToEmbed += "Creation command: " + ' '.join(sys.argv) + '\n'
    StringToEmbed += "Plotted values:" + '\n'
    for k in range(0, len(z), 2):
        StringToEmbed += 'x ' + ' '.join(map(str, z[k])) + '\n'
        StringToEmbed += 'x err ' + ' '.join(map(str, errs[k])) + '\n'
        StringToEmbed += 'y ' + ' '.join(map(str, z[k + 1])) + '\n'
        StringToEmbed += 'y err ' + ' '.join(map(str, errs[k + 1])) + '\n'
    if dic['TYPE'] == 'jpg':
        with open(outputname, 'a') as f:
            f.write(StringToEmbed)
    elif dic['TYPE'] == 'pdf':
        if dic['Verbose'] > 0:
            print "Warning!!! Embedding data in pdfs is not reliable storage!"
            print "Many PDF viewers will strip data which is not viewed!"
        with open(outputname, 'r') as f:
            filetext = f.read().split('\n')
        obj_count = 0
        for line in filetext:
            if ' obj' in line:
                obj_count = max(int(line.split()[0]), obj_count)
            if 'xref' in line:
                break
        StringToEmbed = '%d 0 obj\n<</Novak\'s_EmbedData >>\nstream\n' % (
                        obj_count + 1) + StringToEmbed + 'endstream\nendobj'
        with open(outputname, 'w') as f:
            f.write('\n'.join(filetext[:2] + [StringToEmbed] + filetext[2:]))


if __name__ == '__main__':
    print "This code is part of CLP"
