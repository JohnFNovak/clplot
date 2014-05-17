#! /usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak

# This sub-file does some of the automatic structure determination

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import numpy as np
import globe
from helpers import check_type, is_it_ordered


def structure(data):
    """This function takes a rectangular array of data and plots it. First
    looks at the dimensions of the data, the it 'decides' the best way to plot
    it.'"""
    dic = globe.dic

    new = []

    for d in data:
        Form = None
        w = d[3]['dims'][0]
        h = d[3]['dims'][1]
        block = np.array(d[3]['data'])

        # Check if a prespecified format will work
        if dic['formats']:
            if d[3]['Format']:
                if dic['Verbose'] > 1:
                    print 'data handler decided appropriat format was',
                    print d[3]['Format']
                formats = [x for x in dic['formats'] if x[0] == d[3]['Format']]
            else:
                formats = dic['formats']
            for f in formats:
                l = len(f) - 1
                if dic['Verbose'] > 2:
                    print 'checking', f, l, w, h
                wild = '*' in f
                if f[0] == "c" and (l == w or (l < w and wild)):
                    if dic['Verbose'] > 0:
                        print "Using specified format:", f
                    Form = f
                    break
                elif f[0] == "r" and (l == h or (l < h and wild)):
                    if dic['Verbose'] > 0:
                        print "Using specified format:", f
                    Form = f
        if not Form:
            if w == 2 and h > 2:
                # the good old fashioned two columns
                if dic['Verbose'] > 0:
                    print "the good old fashioned two columns"
                Form = 'cxy'
            elif w > 2 and h == 2:
                # the good old fashioned two rows
                if dic['Verbose'] > 0:
                    print "the good old fashioned two rows"
                Form = 'rxy'
            elif h > (w * 3):
                Form = 'cx' + ('y' * (w - 1))
            elif w > (h * 3):
                Form = 'rx' + ('y' * (h - 1))
            else:
                rows = [is_it_ordered(block[:, x].tolist()) for x in range(w)]
                cols = [is_it_ordered(block[x, :].tolist()) for x in range(h)]
                if cols.count(1) > rows.count(1):
                    Form = 'rx' + ('y' * (h - 1))
                elif rows.count(1) > cols.count(1):
                    Form = 'cx' + ('y' * (w - 1))
                else:
                    print "I have no idea what's going on"
                    Form = 'cx' + ('y' * (w - 1))

        if Form:
            if Form[0] == 'r':
                block = block.T
            needx = True
            mults = 0
            for j, c in enumerate(Form[1:]):
                if check_type(c) == 'num':
                    mults += (int(c) - 1)
                if c == "x":
                    if dic['x_label']:
                        d[3]['x_label'] = dic['x_label']
                    elif d[3]['labels']:
                        d[3]['x_label'] = d[3]['labels'][j + mults]
                    x = block[:, j + mults].tolist()
                    needx = False
                    break
            if needx:
                print "No x specified in format"
                x = range(h)
            count = 0
            for j in range(len(Form) - 1):
                if check_type(Form[j + 1 + mults]) == 'num':
                    for k in range(1, int(Form[j + 1 + mults])):
                        if Form[j + 2 + mults] == "y":
                            new.append([d[0] + [j + mults], d[1], d[2],
                                        d[3]['x_label']])
                            if d[3]['labels']:
                                new[-1].append(d[3]['labels'][j + mults])
                            else:
                                new[-1].append('_'.join(map(str, [d[2],
                                               'block', d[0][1], 'col',
                                               j + mults])))
                            new[-1] = new[-1] + [x, block[:, count].tolist()]
                            new[-1].append([0]*len(x))  # x err
                            new[-1].append([0]*len(x))  # y err
                            new[-1].append([0]*len(x))  # x sys err
                            new[-1].append([d[-1]]*len(x))  # y sys err
                        elif Form[j + 2 + mults] == "e":
                            if Form[j + 1 + mults] == "y":
                                new[-1][-3] = block[:, count].tolist()
                            if Form[j + 1 + mults] == "x":
                                new[-1][-4] = block[:, count].tolist()
                        elif Form[j + 2 + mults] == "s":
                            # % systematic error
                            if Form[j + 1 + mults] == "y":
                                new[-1][-1] = (new[-1][-5] *
                                               block[:, count]).tolist()
                            if Form[j + 1 + mults] == "x":
                                new[-1][-2] = (new[-1][-6] *
                                               block[:, count]).tolist()
                        elif Form[j + 2 + mults] == "S":
                            # abs systematic error
                            if Form[j + 1 + mults] == "y":
                                new[-1][-1] = block[:, count].tolist()
                            if Form[j + 1 + mults] == "x":
                                new[-1][-2] = block[:, count].tolist()
                        count = count + 1
                    mults = mults + 1
                elif Form[j + 1 + mults] == "y":
                    new.append([d[0] + [j + 1 + mults], d[1], d[2],
                                d[3]['x_label']])
                    if d[3]['labels']:
                        new[-1].append(d[3]['labels'][j + mults])
                    else:
                        new[-1].append('_'.join(map(str, [d[2],
                                       'block', d[0][1], 'col',
                                       j + mults])))
                    new[-1] = new[-1] + [x, block[:, count].tolist()]
                    new[-1].append([0]*len(x))  # x err
                    new[-1].append([0]*len(x))  # y err
                    new[-1].append([0]*len(x))  # x sys err
                    new[-1].append([d[-1]]*len(x))  # y sys err
                elif Form[j + 1 + mults] == "x":
                    x = block[:, count].tolist()
                elif Form[j + 1 + mults] == "e":
                    if Form[j + 1 + mults] == "y":
                        new[-1][-3] = block[:, count].tolist()
                    if Form[j + 1 + mults] == "x":
                        new[-1][-4] = block[:, count].tolist()
                elif Form[j + 1 + mults] == "s":
                    # % systematic error
                    if Form[j + 1 + mults] == "y":
                        new[-1][-1] = (new[-1][-5] *
                                       block[:, count]).tolist()
                    if Form[j + 1 + mults] == "x":
                        new[-1][-2] = (new[-1][-6] *
                                       block[:, count]).tolist()
                elif Form[j + 1 + mults] == "S":
                    # abs systematic error
                    if Form[j + 1 + mults] == "y":
                        new[-1][-1] = block[:, count].tolist()
                    if Form[j + 1 + mults] == "x":
                        new[-1][-2] = block[:, count].tolist()
                count = count + 1
                if j + mults + 2 == len(Form):
                    break

    return new


if __name__ == '__main__':
    print "This code is part of CPL"
