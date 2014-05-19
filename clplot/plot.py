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
import pickle


def plot_tiles(tiles, numbered=0, **kwargs):
    dic = globe.dic
    for i, t in enumerate(tiles):
        if not dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0], dic['layout'][1]),
                             (((i - 1) - (i - 1) %
                               dic['layout'][1]) / dic['layout'][1],
                              ((i - 1) % dic['layout'][1])))
        if dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0], dic['layout'][1]),
                             ((i - 1) % dic['layout'][1]),
                             (((i - 1) - (i - 1) %
                              dic['layout'][1]) / dic['layout'][1]))
        plot(t[0], '', Print=False)
    outputname = tiles[-1][1] + "_tiled"
    if numbered != 0:
        outputname = outputname + '_' + str(numbered)
    outputname = outputname + "." + dic['TYPE']
    plt.tight_layout()  # Experimental, and may cause problems
    plt.savefig(outputname)
    if dic['Verbose'] > 0:
        print"printed to", outputname
    # if dic['EmbedData']:
    #     EmbedData(outputname, data)
    #check = subprocess.call(['open', outputname])
    plt.clf()


def plot(data, outputfile, numbered=0, Print=True, **kwargs):
    """This function takes a list z of lists and trys to plot them. the first
    list is always x, and the folowing are always y's"""

    # data format:
    # [[f_id, b_id], filename, output, x_label, y_label,
    #  x, y, x_err, y_err, x_sys_err, y_sys_err]

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

    size = [dic['default_marker_size']] * len(points)
    for i in range(len(points)):
        if len(points[i].split(';')) == 2:
            points[i] = points[i].split(';')[0]
            size[i] = float(points[i].split(';')[1])

    plottingerrors = True

    if dic['x_range']:
        plt.xlim(dic['x_range'])
    if dic['y_range']:
        plt.ylim(dic['y_range'])
    x_label = '/'.join(sorted(set([d[3] for d in data if d[3]])))
    plt.xlabel(x_label, fontsize=dic['fontsize'])
    if dic['y_label']:
        plt.ylabel(dic['y_label'], fontsize=dic['fontsize'])
    if dic['x_log']:
        plt.xscale('log', nonposx='clip')
    if dic['y_log']:
        plt.yscale('log', nonposy='clip')

    plt.tick_params(axis='both', which='major', labelsize=dic['fontsize']*0.75)
    plt.tick_params(axis='both', which='minor', labelsize=dic['fontsize']*0.75)

    if dic['legend']:
        parse_legend(data)

    if dic['norm']:
        for d in data:
            X = np.array(d[5]).astype(float)
            Y = np.array(d[6]).astype(float)
            width = np.mean(X[1:] - X[:-1])
            Y = Y / np.sum(Y * width)
            d[6] = Y.tolist()

    for k, d in enumerate(data):
        X, Y, X_err, Y_err, X_sys_err, Y_sys_err = d[5:11]
        marker = points[k % len(points)]
        msize = size[k % len(points)]
        ecolor = points[k % len(points)][0]
        fcolor = points[k % len(points)][0]
        if marker[-1] == '!':
            fcolor = 'white'
            marker = marker[:-1]
        X = [float(x) * dic['xscaled'] for x in X]
        Y = [float(x) * dic['yscaled'] for x in Y]
        X_err = [float(x) * dic['xscaled'] for x in X_err]
        Y_err = [float(x) * dic['yscaled'] for x in Y_err]
        if plottingerrors and not dic['errorbands']:
            plt.errorbar(X, Y,
                         xerr=X_err,
                         yerr=Y_err,
                         fmt=marker, label=d[4],
                         mec=ecolor, mfc=fcolor, ms=msize)
        if plottingerrors and dic['errorbands']:
            if all([y == 0 for y in Y_err]):
                plt.errorbar(X, Y,
                             xerr=[0] * len(X),
                             yerr=[0] * len(Y),
                             fmt=marker, label=d[4],
                             mec=ecolor, mfc=fcolor, ms=msize)
            else:
                plt.errorbar(X, Y,
                             xerr=[0] * len(X),
                             yerr=[0] * len(Y),
                             fmt=marker, label=d[4],
                             mec=ecolor, mfc=fcolor, ms=msize)
                plt.fill_between(np.array(X),
                                 np.array(Y) + np.array(Y_err),
                                 np.array(Y) - np.array(Y_err),
                                 facecolor=ecolor, alpha=dic['alpha'],
                                 interpolate=True, linewidth=0)
        if dic['plot_sys_err']:
            plt.fill_between(np.array(X),
                             np.array(Y) + np.array(Y_sys_err),
                             np.array(Y) - np.array(Y_sys_err),
                             facecolor=ecolor, alpha=dic['alpha'],
                             interpolate=True, linewidth=0)
        if not plottingerrors:
            plt.plot(X, Y, points[k % len(points)])

    plt.grid(dic['grid'])

    if dic['legend']:
        plt.legend()

    if dic['interactive']:
        if dic['keep_live']:
            plt.ion()
            plt.show(block=False)
        else:
            plt.show()
        return

    outputname = outputfile

    if numbered != 0:
        outputname = outputname + "_" + str(numbered)
    if dic['MULTIP']:
        outputname = outputname + "_mp"

    outputname = outputname + "." + dic['TYPE']

    if Print:
        plt.tight_layout()  # Experimental, and may cause problems
        plt.savefig(outputname)
        if dic['Verbose'] > 0:
            print"printed to", outputname
        if dic['EmbedData']:
            EmbedData(outputname, data)
        #check = subprocess.call(['open', outputname])
        plt.clf()


def parse_legend(data):
    # dic = globe.dic
    # delimiters = ['/', '-', '.', '/', '-', '.']
    delimiters = ['/', '-']
    labels = [x[4] for x in data]

    for divider in delimiters:
        tester = labels[0].split(divider)

        # From the front
        for i in labels:
            if len(i.split(divider)) > len(tester):
                tester = i.split(divider)
        hold = [0]*len(tester)

        for i in range(1, len(labels)):
            for j in range(len(labels[i].split(divider))):
                if tester[j] == labels[i].split(divider)[j] and hold[j]\
                   == 0:
                    hold[j] = 1
                if tester[j] != labels[i].split(divider)[j] and hold[j]\
                   == 1:
                    hold[j] = 0

        for i in range(len(hold)):
            if hold[len(hold)-1-i] == 1:
                for j in range(len(labels)):
                    temp = []
                    for k in range(len(labels[j].split(divider))):
                        if k != len(hold) - 1 - i:
                            temp.append(labels[j].split(divider)[k])
                    labels[j] = string.join(temp, divider)

        tester = labels[0].split(divider)

        # From the back
        for i in labels:
            if len(i.split(divider)) > len(tester):
                tester = i.split(divider)
        hold = [0]*len(tester)

        for i in range(1, len(labels)):
            temp = len(labels[i].split(divider)) - 1 - j
            temp_labels = labels[i].split(divider)
            for j in range(temp):
                if tester[temp] == temp_labels[temp] and hold[temp] == 0:
                    hold[temp] = 1
                if tester[temp] != temp_labels[temp] and hold[temp] == 1:
                    hold[temp] = 0

        for i in range(len(hold)):
            if hold[len(hold)-1-i] == 1:
                for j in range(len(labels)):
                    temp = []
                    for k in range(len(labels[j].split(divider))):
                        if k != len(hold)-1-i:
                            temp.append(labels[j].split(divider)[k])
                    labels[j] = string.join(temp, divider)


def EmbedData(outputname, data):
    dic = globe.dic
    StringToEmbed = "Creation time: " + time.ctime() + '\n'
    StringToEmbed += "Current directory: " + os.path.abspath('.') + '\n'
    StringToEmbed += "Creation command: " + ' '.join(sys.argv) + '\n'
    StringToEmbed += "Plotted values:" + '\n'
    for i, d in enumerate(data):
        X, Y, X_err, Y_err, X_sys_err, Y_sys_err = d[5:11]
        StringToEmbed += 'Plot %d\n' % i
        StringToEmbed += 'x ' + ' '.join(map(str, X)) + '\n'
        StringToEmbed += 'x_err ' + ' '.join(map(str, X_err)) + '\n'
        StringToEmbed += 'x_sys_err ' + ' '.join(map(str, X_err)) + '\n'
        StringToEmbed += 'y ' + ' '.join(map(str, Y)) + '\n'
        StringToEmbed += 'y_err ' + ' '.join(map(str, Y_err)) + '\n'
        StringToEmbed += 'y_sys_err ' + ' '.join(map(str, Y_sys_err)) + '\n'
        StringToEmbed += 'PickleDump:'
        StringToEmbed += pickle.dumps(data)
    if dic['TYPE'] == 'jpg':
        with open(outputname, 'a') as f:
            f.write(StringToEmbed)
    elif dic['TYPE'] == 'pdf':
        if dic['Verbose'] > 0:
            print "Warning!!! Embedding data in pdfs is not reliable storage!"
            print "Many PDF viewers will strip data which is not rendered!"
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


def reload_plot(filename):
    if not os.path.isfile(filename):
        print filename, 'does not exist'
        return None
    with open(filename, 'r') as f:
        data = f.read()
    if len(data.split('PickleDump:')) > 1:
        data = data.split('PickleDump:')[-1]
        data = pickle.loads(data)
        return data[0]
    return None


if __name__ == '__main__':
    print "This code is part of CLP"
