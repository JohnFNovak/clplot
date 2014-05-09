#! / usr / bin / env python

# Part of CLP
# A universal command line plotting script
#
# John Novak

# This sub-file does some of the automatic structure determination

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import math
import globe
from helpers import *
from plot import *


def unstruct_plot(X):
    """This function takes a rectangular array of data and plots it first \
    looks at the dimensions of the data, the it 'decides' the best way to \
    plot it. Hence, 'smart plot'"""
    dic = globe.dic

    Form = None

    z = []
    errs = []

    width = len(list(X[0, :]))
    height = len(list(X[:, 0]))

    # Check if a prespecified format will work
    if len(dic['formats']) > 0:
        for entry in dic['formats']:
            #print entry, len(entry), width, height
            if entry[0] == "c" and (len(entry)-1 == width or (len(entry)-1 <
                                    width and entry[-1] == "*")) and not Form:
                print "Using specified format:", entry
                Form = entry
            elif entry[0] == "r" and (len(entry)-1 == height or (len(entry)-1 <
                                      height and entry[-1] == "*")) and not Form:
                print "Using specified format:", entry
                Form = entry

    if Form:  # If a form was specified, then use it
        mults = 0
        if Form[0] == "c":
            needx = True
            for j in range(1, len(Form)):
                if Form[j] == "x":
                    x = list(X[:, j-1])
                    needx = False
                    break
            if needx:
                print "No x specified in format"
                x = range(height)
            count = 0
            for j in range(len(Form)-1):
                if check_type(Form[j + 1 + mults]) == 'num':
                    if int(Form[j + 1 + mults]) == 1:
                        print "You are a moron, there should be no 1's in",
                        print "your format flag, stupid"
                    for k in range(1, int(Form[j + 1 + mults])):
                        if Form[j + 2 + mults] == "y":
                            z.append(x)
                            z.append(list(X[:, count]))
                            dic['labels'].append(dic['currentfile'] + " / " +
                                                 str(dic['columnlabel']
                                                     [dic['currentstruct']]
                                                     [j + mults]))
                            errs.append([0]*len(x))
                            errs.append([0]*len(list(X[count, :])))
                        elif Form[j + 2 + mults] == "e":
                            if Form[j + 1 + mults] == "y":
                                errs[-1] = list(X[count, :])
                            if Form[j + 1 + mults] == "x":
                                errs[-2] = list(X[count, :])
                        count = count + 1
                    mults = mults + 1
                elif Form[j + 1 + mults] == "y":
                    z.append(x)
                    z.append(list(X[:, count]))
                    dic['labels'].append(dic['currentfile'] + " / " +
                                         str(dic['columnlabel']
                                             [dic['currentstruct']]
                                             [j + mults]))
                    errs.append([0]*len(x))
                    errs.append([0]*len(list(X[:, count])))
                elif Form[j + 1 + mults] == "e":
                    if Form[j + mults] == "y":
                        errs[-1] = list(X[:, count])
                    if Form[j + mults] == "x":
                        errs[-2] = list(X[:, count])
                count = count + 1
                if j + mults + 2 == len(Form):
                    break
        if Form[0] == "r":
            needx = True
            for j in range(1, len(Form)):
                if Form[j] == "x":
                    x = list(X[j-1, :])
                    needx = False
                    break
            if needx:
                print "No x specified in format"
                x = range(width)
            count = 0
            for j in range(len(Form)-1):
                if check_type(Form[j + 1 + mults]) == 'num':
                    if int(Form[j + 1 + mults]) == 1:
                        print "You are a moron, there should be no 1's in",
                        print "your format flag, stupid"
                    for k in range(1, int(Form[j + 1 + mults])):
                        if Form[j + 2 + mults] == "y":
                            z.append(x)
                            z.append(list(X[count, :]))
                            dic['labels'].append(dic['currentfile'] + " / " +
                                                 str(dic['columnlabel']
                                                     [dic['currentstruct']]
                                                     [j + mults]))
                            errs.append([0]*len(x))
                            errs.append([0]*len(list(X[count, :])))
                        elif Form[j + 2 + mults] == "e":
                            if Form[j + 1 + mults] == "y":
                                errs[-1] = list(X[count, :])
                            if Form[j + 1 + mults] == "x":
                                errs[-2] = list(X[count, :])
                        count = count + 1
                    mults = mults + 1
                elif Form[j + 1 + mults] == "y":
                    z.append(x)
                    z.append(list(X[count, :]))
                    dic['labels'].append(dic['currentfile'] + " / " +
                                         str(dic['columnlabel']
                                             [dic['currentstruct']]
                                             [j + mults]))
                    errs.append([0]*len(x))
                    errs.append([0]*len(list(X[count, :])))
                elif Form[j + 1 + mults] == "e":
                    if Form[j + mults] == "y":
                        errs[-1] = list(X[count, :])
                    if Form[j + mults] == "x":
                        errs[-2] = list(X[count, :])
                count = count + 1
                if j + mults + 2 == len(Form):
                    break
    elif width == 2 and height != 2:
        # the good old fashioned two columns
        print "the good old fashioned two columns"
        if is_it_ordered(list(X[:, 0])):
            # ordered by the first column
            z = [list(X[:, 0]), list(X[:, 1])]
            dic['labels'].append(dic['currentfile'] + " / " +
                                 str(dic['columnlabel']
                                     [dic['currentstruct']][int(len(z) / 2)]))
            errs = [[0] * len(z[0])] * 2
        elif is_it_ordered(list(X[:, 1])):
            # ordered by the second column
            z[list(X[:, 1]), list(X[:, 0])]
            dic['labels'].append(dic['currentfile'] + " / " +
                                 str(dic['columnlabel']
                                     [dic['currentstruct']][int(len(z) / 2)]))
            errs = [[0] * len(z[0])] * 2
        else:
            # not ordered
            print "No deducable ordering, I'll just pick which column is x"
            z = [list(X[:, 0]), list(X[:, 1])]
            dic['labels'].append(dic['currentfile'] + " / " +
                                 str(dic['columnlabel']
                                     [dic['currentstruct']][int(len(z) / 2)]))
            errs = [[0] * len(z[0])] * 2
    elif width != 2 and height == 2:
        # the good old fashioned two rows
        print "the good old fashioned two rows"
        if is_it_ordered(list(X[0, :])):
            # ordered by the first row
            z = [list(X[0, :]), list(X[1, :])]
            dic['labels'].append(dic['currentfile'] + " / " +
                                 str(dic['columnlabel']
                                     [dic['currentstruct']][int(len(z) / 2)]))
            errs = [[0] * len(z[0])] * 2
        elif is_it_ordered(list(X[1, :])):
            # ordered by the second row
            z = [list(X[1, :]), list(X[0, :])]
            dic['labels'].append(dic['currentfile'] + " / " +
                                 str(dic['columnlabel']
                                     [dic['currentstruct']][int(len(z) / 2)]))
            errs = [[0] * len(z[0])] * 2
        else:
            # not ordered
            print "No deducable ordering, I'll just pick which row is x"
            z = [list(X[0, :]), list(X[1, :])]
            errs = [[0] * len(z[0])] * 2
    elif width < 5 and height < 5:
        # we are going to have to look around for ordered things
        needx = True
        for i in range(width):
            if is_it_ordered(list(X[:, i])):
                needx = False
                xcol = i
                break
        if not needx:
            for i in range(width):
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
            for i in range(height):
                if is_it_ordered(list(X[i, :])):
                    needx = False
                    xrow = i
                    break
            if not needx:
                for i in range(height):
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
            print "I don't know what to do with this block. It's", width, "by",
            print height, "and neither axis seems to be ordered"
    elif width < 5 and height > 7:
        # we will assume that it is in columns
        needx = True
        for i in range(width):
            if is_it_ordered(list(X[:, i])):
                needx = False
                xcol = i
                break
        if not needx:
            for i in range(width):
                if i != xcol:
                    errs.append([0]*len(list(X[:, xcol])))
                    errs.append([0]*len(list(X[:, i])))
                    z.append(list(X[:, xcol]))
                    z.append(list(X[:, i]))
                    dic['labels'].append(dic['currentfile'] + " / " +
                                         str(dic['columnlabel']
                                             [dic['currentstruct']]
                                             [int(len(z) / 2)]))
    elif width > 7 and height < 5:
        # we will assume that it is in rows
        needx = True
        for i in range(height):
            if is_it_ordered(list(X[i, :])):
                needx = False
                xrow = i
                break
        if not needx:
            for i in range(height):
                if i != xrow:
                    errs.append([0]*len(list(X[xcol, :])))
                    errs.append([0]*len(list(X[i, :])))
                    z.append(list(X[xrow, :]))
                    z.append(list(X[i, :]))
                    dic['labels'].append(dic['currentfile'] + " / " +
                                         str(dic['columnlabel']
                                             [dic['currentstruct']]
                                             [int(len(z) / 2)]))
    elif width > 5 and height > 5:
        # will will have to look around for oredered things
        needx = True
        for i in range(width):
            if is_it_ordered(list(X[:, i])):
                needx = False
                xcol = i
                break
        if not needx:
            for i in range(width):
                if i != xcol:
                    errs.append([0]*len(list(X[:, xcol])))
                    errs.append([0]*len(list(X[:, i])))
                    z.append(list(X[:, xcol]))
                    z.append(list(X[:, i]))
                    dic['labels'].append(dic['currentfile'] + " / " + str(dic['columnlabel'][dic['currentstruct']][int(len(z) / 2)]))
        if needx:
            for i in range(height):
                if is_it_ordered(list(X[i, :])):
                    needx = False
                    xrow = i
                    break
            if not needx:
                for i in range(height):
                    if i != xrow:
                        errs.append([0]*len(list(X[xcol, :])))
                        errs.append([0]*len(list(X[i, :])))
                        z.append(list(X[xrow, :]))
                        z.append(list(X[i, :]))
                        dic['labels'].append(dic['currentfile'] + " / " + str(dic['columnlabel'][dic['currentstruct']][int(len(z) / 2)]))
        if needx:
            print "I don't know what to do with this block. It's", width, "by",
            print height, "and neither axis seems to be ordered"
    else:
        print "I don't know what to do with this block. It's", width, "by",
        print height

    if z:
        new_err = []
        for k in range(len(z) / 2):
            new_err.append([[], []])
            new_err.append([[], []])
            for l in range(len(z[2*k + 1])):
                new_err[2*k][0].append(errs[2*k][l])
                new_err[2*k][1].append(errs[2*k][l])
                new_err[2*k + 1][0].append(float(errs[2*k + 1][l]))
                new_err[2*k + 1][1].append(dic['sys_err']*float(z[2*k + 1][l]))
        errs = new_err
        if dic['MULTIP']:
            z = dic['remnants'] + z
            errs = dic['remnanterrors'] + errs
            dic['multicountpile'] = 0
            if (len(z)-len(z) % int(dic['MULTIP'])) / int(dic['MULTIP']) / 2 > 1:
                dic['multicountpile'] = 1
            if (len(z)-len(z) % int(dic['MULTIP'])) / int(dic['MULTIP']) > 0:
                for i in range(0, (len(z)-len(z) % int(dic['MULTIP'])) / int(dic['MULTIP']) / 2):
                    plot(z[:(int(dic['MULTIP']) * 2)], errs[:(int(dic['MULTIP']) * 2)])
                    z = z[(int(dic['MULTIP']) * 2):]
                    errs = errs[(int(dic['MULTIP']) * 2):]
                    dic['multicountpile'] = dic['multicountpile'] + 1
            dic['remnants'] = z
            dic['remnanterrors'] = errs
            if dic['remnants']:
                dic['LefttoPlot'] = True
        else:
            # just plot it
            plot(z, errs)
        if dic['Numbering']:
            dic['numbered'] = dic['numbered'] + 1


def plot_arragnement():
    """This function looks at dic['MULTIT'] and decides how to structure the \
    multiplot it returns a 2 tuple which is the root for the first 2 argument \
    of the subplot command"""

    found = False

    if math.sqrt(float(dic['MULTIT'])) % 1 == 0:
        # Or multiplot can be square
        form = (int(math.sqrt(float(dic['MULTIT']))),
                int(math.sqrt(float(dic['MULTIT']))))
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
    if not found and math.sqrt(float(dic['MULTIT']) + 1) % 1 == 0:
        form = (int(math.sqrt(float(dic['MULTIT']) + 1)),
                int(math.sqrt(float(dic['MULTIT']) + 1)))
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
    if not found and math.sqrt(float(dic['MULTIT']) + 2) % 1 == 0:
        form = (int(math.sqrt(float(dic['MULTIT']) + 2)),
                int(math.sqrt(float(dic['MULTIT']) + 2)))
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

    print " I have decided that the multiplots will be", form[0], "by", form[1]

    return form


if __name__ == '__main__':
    print "This code is part of CPL"
