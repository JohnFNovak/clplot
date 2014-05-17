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
from helpers import read_flags, interact, choose_from, check_type, choose_multiple
from plot import plot, plot_tiles
from data_handler import make_blocks, read_data
import sys
import os


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
    data = structure(data)

    return data


def clplot(data):
    dic = globe.dic

    # data format:
    # [[f_id, b_id, c_id], filename, output, x_label, y_label,
    #  x, y, x_err, y_err, x_sys_err, y_sys_err]

    if not dic['MULTIP']:
        # multiplot flag not give, group plots by file, then block
        l = lambda x: '-'.join(map(str, x))
        groups = [[d for d in data if l(d[0][:2]) == f]
                  for f in set([l(x[0][:2]) for x in data])]
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
    files = dic['files']
    blocks = list(set([x[1] + '_' + str(x[0][1]) for x in data]))
    mode = choose_from('Pick a mode: from (s)ratch or (a)utomatic',
                       ['s', 'a'],
                       default='s')
    plots = [[]]
    if mode == 's':
        default = 'a'
    elif mode == 'a':
        default = 'g'
    while command:
        print '(%s) =====================#' % (mode)
        if mode == 's':
            # print [p for p in plots]
            print ['%d: %s cols by %d rows' % (i + 1, len(p), len(p[0][6]))
                   for i, p in enumerate(plots) if p and p[0]]
            # print [['-'.join(map(str, [d[1]] + d[0])), len(d[6])]
            #        for plot in plots for d in plot]
        command = choose_from('?',
                              ['!', 'g', 'G', 'f', 'a', 'd', 's'],
                              default=default)
        history.append(command)
        if command == '!':
            interact(**{'dic': dic, 'data': data, 'plots': plots})
        elif command == 'g':
            if mode == 'a':
                clplot(data)
            elif mode == 's':
                for p in plots:
                    c = choose_from('Plot %d: %s cols by %d rows ?' % (i + 1, len(p), len(p[0][6])),
                                    ['y', 'n'],
                                    default='y')
                    if c == 'y':
                        clplot(p)
        elif command == 'G':
            dic['interactive'] = False
            if mode == 'a':
                clplot(data)
            elif mode == 's':
                for p in plots:
                    c = choose_from('Plot %d: %s cols by %d rows ?' % (i + 1, len(p), len(p[0][6])),
                                    ['y', 'n'],
                                    default='y')
                    if c == 'y':
                        clplot(p)
            sys.exit(1)
        elif command == 'f':
            new_file = raw_input('file to load: ').strip()
            if os.path.isfile(new_file):
                files.append(new_file)
            data += structure(init(files=[new_file]))
            blocks = list(set([x[1] + '_' + str(x[0][1]) for x in data]))
        elif mode == 's' and command == 'a':
            print 'adding data to plot'
            print 'select file:'
            for i, f in enumerate(files):
                n_b = len(set([' '.join(map(str, x[0][:2]))
                               for x in data if x[1] == f]))
                print '%d- file: %s [# blocks = %d]' % (i + 1, f, n_b)
            choice = int(choose_from("selection",
                                     map(str,
                                         range(1, 1 + len(files))),
                                     default='1')) - 1
            blocks = list(set([' '.join([x[1], 'block:', str(x[0][1] + 1)]) for
                               x in data if x[1] == files[int(choice)]]))
            blocks.sort(key=lambda x: x.split(' ')[-1])
            print '-------------'
            print 'select block:'
            for i, b in enumerate(blocks):
                n_c = len(set([' '.join(map(str, x[0])) for x in data if
                               ' '.join([x[1], 'block:', str(x[0][1] + 1)]) == b]))
                n_r = len([x for x in data if ' '.join([x[1], 'block:', str(x[0][1] + 1)]) == b][0][6])
                print '%d- file: %s [# cols = %d, # rows = %d]' % (i + 1, b, n_c, n_r)
            choice = int(choose_from("selection",
                                     map(str,
                                         range(1, 1 + len(blocks))),
                                     default='1')) - 1
            cols = [d for d in data
                    if ' '.join([d[1], 'block:', str(d[0][1] + 1)]) ==
                    blocks[choice]]
            print '-------------'
            print 'select columns:'
            for i, d in enumerate(cols):
                print '%d- file: %s block: %d col: %d [len %d title: %s]' % (i + 1, d[1], d[0][0] + 1, d[0][1] + 1, len(d[6]), d[4])
            choices = choose_multiple("selections",
                                      range(1, 1 + len(cols)),
                                      default='1')
            print '-------------'
            if choices == map(str, range(1, 1 + len(cols))):
                print 'adding all columns as plot'
                plots.append(cols)
                choices = []
            for choice in choices:
                print choice
                good = False
                if check_type(choice) == 'num':
                    size = len(cols[int(choice) - 1][6])
                    choice = int(choice) - 1
                elif not plots[0]:
                    print 'starting new plot'
                    plots[0].append(cols[choice])
                    good = True
                elif len([p for p in plots if p and len(p[0]) > 6
                          and len(p[0][6]) == size]) > 1:
                    # print size, [len(p[0][6]) for p in plots]
                    print 'multiple plots of an appropriate dimension have been',
                    print 'found'
                    opts = [p for p in plots if p[6] == size]
                    for i, o in enumerate(opts):
                        print i, ':', o
                    c = choose_from("select one ('n' for new)",
                                    map(str, range(1, 1 + len(opts))) + ['n'],
                                    default='1')
                    if check_type(c) == 'num':
                        plots[plots.index(opts[int(c) - 1])].append(cols[choice])
                elif len([p for p in plots if p and len(p[0]) > 6
                          and len(p[0][6]) == size]) == 1:
                    # print size, [len(p[0][6]) for p in plots]
                    print 'only one plot has been found with the appropriate',
                    print 'dimension.'
                    new = choose_from('start new plot? (y/n)',
                                      ['y', 'n'],
                                      default='n')
                    if new == 'n':
                        plots[plots.index([p for p in plots if p
                                           and len(p[0]) > 6
                                           and len(p[0][6]) == size][0]
                                          )].append(cols[int(choice)])
                        good = True
                else:
                    print 'no plot of appropriate dimension has been found.'
                if not good:
                    print 'starting new plot'
                    plots.append([cols[int(choice)]])
            blocks = list(set([x[1] + '_' + str(x[0][1]) for x in data]))
        elif command == 'd' and mode == 's':
            if len(plots) > 1:
                print 'plots:'
                for i, p in enumerate(plots):
                    print p
                    # print '%d- %d: %s cols by %d rows ?' % (i + 1, len(p), len(p[0][6]))
                choice = int(choose_from("selection",
                                         map(str,
                                             range(1, 1 + len(plots))),
                                         default='1')) - 1
            else:
                choice = 0
            print 'columns:'
            for i, d in enumerate(plots[choice]):
                print '%d- file: %s block: %d col: %d [len %d title: %s]' % (i + 1, d[1], d[0][0] + 1, d[0][1] + 1, len(d[6]), d[4])
            choice2 = int(choose_from("selection",
                                      map(str,
                                          range(1, 1 + len(plots[choice]))),
                                      default='1')) - 1
            c = choose_from('delete?', ['y', 'n'], default='n')
            if c == 'y':
                del(plots[choice][choice2])
        elif command == 's':
            dic['Ustyle'] = [raw_input('style: ')] + dic['Ustyle']


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
