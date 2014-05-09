#!/usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak

# This sub-module handles file reading stuff

# written for Python 2.6. Requires Scipy,  Numpy,  and Matplotlib

import string
import globe
from helpers import *


def detect_blocks(dataarray):
    """This function runs over an array of data pulled from a file and \
detects the structure so that the proper plotting method can be deduced the \
structure is returned as a list. Each entry is one block of the data in the \
form of (width of block,  height of block) This will detect contiguous \
rectangular blocks of data with the same formats of text vs numbers"""
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
                height[block] = height[block]+1
            else:
                block = block+1
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
            if mixed and len(dataarray) != i+1:
                if len(dataarray[i]) == len(dataarray[i+1]):
                    print "we are going to use", string.join(dataarray[i]),
                    print "as labels"
                    dic['columnlabel'].append(dataarray[i])
            else:
                dic['columnlabel'].append(range(len(dataarray[i])))
        else:
            block = block+1
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
            if mixed and len(dataarray) != i+1:
                if len(dataarray[i]) == len(dataarray[i+1]):
                    print "we are going to use", string.join(dataarray[i]),
                    print "as labels"
                    dic['columnlabel'].append(dataarray[i])
            else:
                dic['columnlabel'].append(range(len(dataarray[i])))

    for i in range(block+1):
        #print "block", i, "is", width[i], "by", height[i]
        structure.append((width[i], height[i]))

    return structure


def readdat(struct, block, data):
    x = []
    linenum = 0

    for i in range(len(struct)):
        if i == block:
            # this is the block you want
            for j in range(struct[i][1]):
                k = j+linenum
                x.append(data[k])
            break
        else:
            # count how many lines down you have to look
            linenum = linenum+struct[i][1]
    return x


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
        print "Um,  we can't figure out what you are using for data seperation"

    datafile.seek(0)
    for line in datafile:
        data.append(tuple(line.split(delimiter)))
    datafile.close()

    data = remove_formating(data)
    return data

if __name__ == '__main__':
    print "This code is part of CLP"
