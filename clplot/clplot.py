#! /usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak
# June 4, 2012 - July 19, 2012

# Run with: python clplot.py
# or just: ./clplot.py (after making it executable, obviously)

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import globe
from structure import structure
from helpers import read_flags, interact
from plot import plot, plot_tiles
from data_handler import make_blocks, read_data


def init(data=[], files=globe.dic['files']):
    dic = globe.dic
    for i, filename in enumerate(files):
        if dic['Verbose'] > 0:
            print "plotting", filename
        sys_err = dic['sys_err_default']
        if len(filename.split('#')) == 2:
            sys_err = float(filename.split('#')[1].strip())
            filename = filename.split('#')[0].strip()
        if dic['outputs']:
            output = dic['outputs'].pop()
        else:
            output = '.'.join(filename.split('.')[:-1])
        dic['numbered'] = 0

        # Now read data file
        blocks = make_blocks(read_data(filename))

        if blocks:
            for j, b in enumerate(blocks):
                if dic['GroupBy'] == 'files':
                    data.append([[i, j], filename, output, b, sys_err])
                elif dic['GroupBy'] == 'blocks':
                    data.append([[j, i], filename, output, b, sys_err])

    data.sort(key=lambda x: x[0])

    return data


def clplot(data):
    dic = globe.dic

    if not data:
        return

    data = structure(data)

    # data format:
    # [[f_id, b_id], filename, output, x_label, y_label,
    #  x, y, x_err, y_err, x_sys_err, y_sys_err]

    if not dic['MULTIP']:
        # multiplot flag not give, group plots by file, then block
        l = lambda x: '-'.join(map(str, x))
        groups = [[d for d in data if l(d[0]) == f]
                  for f in set([l(x[0]) for x in data])]
    else:
        groups = [data[(i * dic['MULTIP']):((i + 1) * dic['MULTIP'])]
                  for i in range((len(data) / dic['MULTIP']) + 1)]

    plots = []
    for g in groups:
        if g:
            outputfile = '-'.join(sorted(set([d[2] for d in g])))
            plots.append([g, outputfile])

    tiles = []
    tiled_count = 0
    tile_name = ''
    for p in plots:
        e_args = {}
        if [x[1] for x in plots].count(p[1]) > 1:
            e_args['numbered'] = [x for x in plots if x[1] == p[1]].index(p)
        if dic['MULTIT']:
            tiles.append(p)
            if len(tiles) == dic['MULTIT']:
                if tile_name != p[1]:
                    tiled_count = 0
                plot_tiles(tiles, numbered=tiled_count)
                tiles = []
                tiled_count += 1
                tile_name = p[1]
        else:
            plot(*p, **e_args)

    if tiles:
        plot_tiles(tiles, numbered=tiled_count)


def interactive_plot(data):
    """Interactive Mode!"""
    dic = globe.dic

    command = True
    history = []
    while command:
        print '#=====================#'
        command = raw_input('?: ')  # or '.'
        history.append(command)
        if command == '!':
            interact()
        if command == 'g':
            clplot(data)


if __name__ == '__main__':
    """A Python program that takes a file or list of filesand creates plots of
    the data."""
    dic = globe.dic
    read_flags()
    data = init()
    if dic['interactive']:
        interactive_plot(data)
    else:
        clplot(data)
