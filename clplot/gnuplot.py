#! /usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak
# June 4, 2012 - July 19, 2012

# this sub-file holds the functions relating to generating the output

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import numpy as np
import string
import globe
from helpers import EmbedData
import subprocess


class GnuPlotPipe:
    """Pipe to gnuplot to make plot calls"""
    def __init__(self):
        self.pipe = subprocess.Popen(['gnuplot', '-persist', 'w'])

    def close(self):
        self.pipe.terminate()

    def __call__(self, command):
        self.pipe.communicate(command)


class GnuPlot:
    """Class which represents a plot"""

    def __init__(self):
        self.pipe = GnuPlotPipe()
        self.string = ''
        self.labels = []

    def __call__(self, command):
        self.string += command

    def plot(self, X, Y, style, xerr=None, yerr=None, fmt=None, label=None,
             mec=None, mfc=None, ms=None):
        command = ''
        if label:
            self.labels.append(label)
        else:
            self.labels.append('')
        self.pipe(command)

    def legend(self):
        command = ''
        self.pipe(command)

    def savefig(self, filename):
        command = ''
        self.pipe(command)

    def clear(self):
        self.string = ''
        self.labels = []

    def show(self):
        self.pipe(self.string)

    def band(self):
        command = ''
        self.pipe(command)


global Plot
Plot = GnuPlot()


def plot_tiles(tiles, numbered=0, **kwargs):
    global Plot
    dic = globe.dic
    for i, t in enumerate(tiles):
        Plot('set multiplot layout %d, %d\n' % tuple(dic['layout']))
        plot(t[0], '', Print=False)
        Plot('e\n#\n')
    Plot('unset multiplot')
    outputname = tiles[-1][1] + "_tiled"
    if numbered != 0:
        outputname = outputname + '_' + str(numbered)
    outputname = outputname + "." + dic['TYPE']
    Plot.savefig(outputname)
    if dic['Verbose'] > 0:
        print"printed to", outputname
    # if dic['EmbedData']:
    #     EmbedData(outputname, data)
    #check = subprocess.call(['open', outputname])


def plot(data, outputfile, numbered=0, Print=True, **kwargs):
    global Plot
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
        plot('set xrange [' + ':'.join(map(str, dic['x_range'])) + ']')
    if dic['y_range']:
        plot('set yrange [' + ':'.join(map(str, dic['y_range'])) + ']')
    x_label = '/'.join(sorted(set([d[3] for d in data if d[3]])))
    plot('set xlabel ' + x_label)
    if dic['y_label']:
        plot('set xlabel ' + dic['y_label'])
    # if dic['x_log']:
    #     plt.xscale('log', nonposx='clip')
    # if dic['y_log']:
    #     plt.yscale('log', nonposy='clip')

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
            Plot.plot(X, Y, xerr=X_err, yerr=Y_err, fmt=marker, label=d[4],
                      mec=ecolor, mfc=fcolor, ms=msize)
        if plottingerrors and dic['errorbands']:
            if all([y == 0 for y in Y_err]):
                Plot.plot(X, Y, xerr=X_err, yerr=Y_err, fmt=marker, label=d[4],
                          mec=ecolor, mfc=fcolor, ms=msize)
            else:
                Plot.plot(X, Y, fmt=marker, label=d[4], mec=ecolor, mfc=fcolor,
                          ms=msize)
                Plot.band(np.array(X), np.array(Y_sys_err), facecolor=ecolor,
                          alpha=dic['alpha'], interpolate=True, linewidth=0)
        if dic['plot_sys_err']:
            Plot.band(np.array(X), np.array(Y_sys_err), facecolor=ecolor,
                      alpha=dic['alpha'], interpolate=True, linewidth=0)
        if not plottingerrors:
            Plot.plot(X, Y, points[k % len(points)])

    if dic['legend']:
        Plot.legend()

    # if dic['interactive']:
    #     if dic['keep_live']:
    #         plt.ion()
    #         plt.show(block=False)
    #     else:
    #         plt.show()
    #     return

    outputname = outputfile

    if numbered != 0:
        outputname = outputname + "_" + str(numbered)
    if dic['MULTIP']:
        outputname = outputname + "_mp"

    outputname = outputname + "." + dic['TYPE']

    if Print:
        # plt.tight_layout()  # Experimental, and may cause problems
        Plot.savefig(outputname)
        if dic['Verbose'] > 0:
            print"printed to", outputname
        if dic['EmbedData']:
            EmbedData(outputname, data)
        #check = subprocess.call(['open', outputname])
        Plot.clear()


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


if __name__ == '__main__':
    print "This code is part of CLP"
