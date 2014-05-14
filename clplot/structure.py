#! /usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak

# This sub-file does some of the automatic structure determination

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import numpy as np
import math as m
import globe
from helpers import check_type, is_it_ordered
from plot import plot


def structure(data):
    """This function takes a rectangular array of data and plots it. First
    looks at the dimensions of the data, the it 'decides' the best way to plot
    it.'"""
    dic = globe.dic

    Form = None

    new = []

    for d in data:
        w = d[3]['dims'][0]
        h = d[3]['dims'][1]
        block = np.array(d[3]['data'])
        if (h, w) != block.shape:
            print "Internal error, the dimensions given from make_blocks don't",
            print "match the dims on the data"
            print h, w, block.shape
            print 'using the dims on the data'
            h, w = block.shape

        # Check if a prespecified format will work
        if dic['formats']:
            if d[3]['Format']:
                formats = [x for x in dic['formats'] if x[0] == d[3]['Format']]
            else:
                formats = dic['formats']
            for f in formats:
                l = len(f) - 1
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

        elif w == 2 and h > 2:
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
            Form = 'c' + ('y' * w)
        elif w > (h * 3):
            Form = 'r' + ('y' * h)
        else:
            rows = [is_it_ordered(block[:, x].list()) for x in range(w)]
            cols = [is_it_ordered(block[x, :].list()) for x in range(h)]
            if cols.count(1) > rows.count(1):
                Form = 'r' + ('y' * h)
            if rows.count(1) > cols.count(1):
                Form = 'c' + ('y' * w)

        elif w < 5 and h < 5:
            # we are going to have to look around for ordered things
            needx = True
            for i in range(w):
                if is_it_ordered(list(X[:, i])):
                    needx = False
                    xcol = i
                    break
            if not needx:
                for i in range(w):
                    if i != xcol:
                        errs.append([0]*len(list(X[:, xcol])))
                        errs.append([0]*len(list(X[:, i])))
                        z.append(list(X[:, xcol]))
                        z.append(list(X[:, i]))
                        dic['labels'].append(dic['currentfile'] + " / " +
                                             str(dic['columnlabel']
                                                 [dic['currentstruct']]
                                                 [int(len(z) / 2)]))
            if needx:
                for i in range(h):
                    if is_it_ordered(list(X[i, :])):
                        needx = False
                        xrow = i
                        break
                if not needx:
                    for i in range(h):
                        if i != xcol:
                            errs.append([0]*len(list(X[xcol, :])))
                            errs.append([0]*len(list(X[i, :])))
                            z.append(list(X[xrow, :]))
                            z.append(list(X[i, :]))
                            dic['labels'].append(dic['currentfile'] + " / " +
                                                 str(dic['columnlabel']
                                                     [dic['currentstruct']]
                                                     [int(len(z) / 2)]))
            if needx:
                print "I don't know what to do with this block. It's", w, "by",
                print h, "and neither axis seems to be ordered"
        elif w < 5 and h > 7:
            # we will assume that it is in columns
            needx = True
            for i in range(w):
                if is_it_ordered(list(X[:, i])):
                    needx = False
                    xcol = i
                    break
            if not needx:
                for i in range(w):
                    if i != xcol:
                        errs.append([0]*len(list(X[:, xcol])))
                        errs.append([0]*len(list(X[:, i])))
                        z.append(list(X[:, xcol]))
                        z.append(list(X[:, i]))
                        dic['labels'].append(dic['currentfile'] + " / " +
                                             str(dic['columnlabel']
                                                 [dic['currentstruct']]
                                                 [int(len(z) / 2)]))
        elif w > 7 and h < 5:
            # we will assume that it is in rows
            needx = True
            for i in range(h):
                if is_it_ordered(list(X[i, :])):
                    needx = False
                    xrow = i
                    break
            if not needx:
                for i in range(h):
                    if i != xrow:
                        errs.append([0]*len(list(X[xcol, :])))
                        errs.append([0]*len(list(X[i, :])))
                        z.append(list(X[xrow, :]))
                        z.append(list(X[i, :]))
                        dic['labels'].append(dic['currentfile'] + " / " +
                                             str(dic['columnlabel']
                                                 [dic['currentstruct']]
                                                 [int(len(z) / 2)]))
        elif w > 5 and h > 5:
            # will will have to look around for oredered things
            needx = True
            for i in range(w):
                if is_it_ordered(list(X[:, i])):
                    needx = False
                    xcol = i
                    break
            if not needx:
                for i in range(w):
                    if i != xcol:
                        errs.append([0]*len(list(X[:, xcol])))
                        errs.append([0]*len(list(X[:, i])))
                        z.append(list(X[:, xcol]))
                        z.append(list(X[:, i]))
                        dic['labels'].append(dic['currentfile'] + " / " + str(dic['columnlabel'][dic['currentstruct']][int(len(z) / 2)]))
            if needx:
                for i in range(h):
                    if is_it_ordered(list(X[i, :])):
                        needx = False
                        xrow = i
                        break
                if not needx:
                    for i in range(h):
                        if i != xrow:
                            errs.append([0]*len(list(X[xcol, :])))
                            errs.append([0]*len(list(X[i, :])))
                            z.append(list(X[xrow, :]))
                            z.append(list(X[i, :]))
                            dic['labels'].append(dic['currentfile'] + " / " + str(dic['columnlabel'][dic['currentstruct']][int(len(z) / 2)]))
            if needx:
                print "I don't know what to do with this block. It's", w, "by",
                print h, "and neither axis seems to be ordered"
        else:
            print "I don't know what to do with this block. It's", w, "by",
            print h

        if Form:  # If a form was specified, then use it
            mults = 0
            if Form[0] == 'r':
                block = block.T
            needx = True
            for j, c in enumerate(Form[1:]):
                if c == "x":
                    x = block[:, j + 1].tolist()
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
                            new.append([d[1], d[2]])
                            if d[3]['labels']:
                                new[-1].append(d[3]['labels'])
                            else:
                                new[-1].append('_'.join(map(str, [d[1],
                                               'block', d[0][1], 'col',
                                               j + mults])))
                            new[-1] = new[-1] + [x, block[:, count].tolist()]
                            new[-1].append([0]*len(x))
                            new[-1].append([0]*len(x))
                        elif Form[j + 2 + mults] == "e":
                            if Form[j + 1 + mults] == "y":
                                new[-1][-1] = block[:, count].tolist()
                            if Form[j + 1 + mults] == "x":
                                new[-1][-2] = block[:, count].tolist()
                        count = count + 1
                    mults = mults + 1
                elif Form[j + 2 + mults] == "y":
                    new.append([d[1], d[2]])
                    if d[3]['labels']:
                        new[-1].append(d[3]['labels'])
                    else:
                        new[-1].append('_'.join(map(str, [d[1],
                                       'block', d[0][1], 'col',
                                       j + mults])))
                    new[-1] = new[-1] + [x, block[:, count].tolist()]
                    new[-1].append([0]*len(x))
                    new[-1].append([0]*len(x))
                elif Form[j + 2 + mults] == "x":
                    x = block[:, count].tolist()
                elif Form[j + 2 + mults] == "e":
                    if Form[j + 1 + mults] == "y":
                        new[-1][-1] = block[:, count].tolist()
                    if Form[j + 1 + mults] == "x":
                        new[-1][-2] = block[:, count].tolist()
                count = count + 1
                if j + mults + 2 == len(Form):
                    break

    return new


def plot_arragnement():
    """This function looks at dic['MULTIT'] and decides how to structure the
    multiplot it returns a 2 tuple which is the root for the first 2 argument
    of the subplot command"""

    dic = globe.dic
    found = False

    if m.sqrt(float(dic['MULTIT'])) % 1 == 0:
        # Or multiplot can be square
        form = (int(m.sqrt(float(dic['MULTIT']))),
                int(m.sqrt(float(dic['MULTIT']))))
        found = True
    elif int(dic['MULTIT']) == 3:
        form = (1, 3)
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a * (a + 1) <= int(dic['MULTIT']):
            if float(dic['MULTIT']) == float(a * (a + 1)):
                looking = False
                found = True
            else:
                a = a + 1
        if found:
            form = (a, a + 1)
    if not found and m.sqrt(float(dic['MULTIT']) + 1) % 1 == 0:
        form = (int(m.sqrt(float(dic['MULTIT']) + 1)),
                int(m.sqrt(float(dic['MULTIT']) + 1)))
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a * (a + 1) <= int(dic['MULTIT']) + 1:
            if float(dic['MULTIT']) + 1 == float(a * (a + 1)):
                looking = False
                found = True
            else:
                a = a + 1
        if found:
            form = (a, a + 1)
    if not found and m.sqrt(float(dic['MULTIT']) + 2) % 1 == 0:
        form = (int(m.sqrt(float(dic['MULTIT']) + 2)),
                int(m.sqrt(float(dic['MULTIT']) + 2)))
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a * (a + 1) <= int(dic['MULTIT']) + 2:
            if float(dic['MULTIT']) + 2 == float(a * (a + 1)):
                looking = False
                found = True
            else:
                a = a + 1
        if found:
            form = (a, a + 1)
    if not found:
        looking = True
        a = 1
        while looking and a * (a + 1) <= int(dic['MULTIT']):
            if float(dic['MULTIT']) <= float(a * (a + 1)):
                looking = False
                found = True
            else:
                a = a + 1
        if found:
            form = (a, a + 1)

    if dic['Verbose'] > 0:
        print " I have decided that the multiplots will be", form[0], "by", form[1]

    return form


if __name__ == '__main__':
    print "This code is part of CPL"
