#!/usr/bin/env python

# A universal command line plotting script
#
# John Novak

# This sub-module contains helper functions

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import collections
import itertools
import string


def is_it_ordered(vals):
    """This function takes a list of numbers are returns whether or not they are in order"""

    ordered = False

    if vals == sorted(vals):
        ordered = True
    if vals == sorted(vals, reverse=True):
        ordered = True

    return ordered


def remove_empties(struct, x):
    """This function runs through the data and the structure array and removes entries that are either empty or are singular"""

    linenum = len(x)-1
    structBK = struct
    count = 0
    blocks = len(structBK)

    for i in range(blocks):
        j = -i - 1 + count  # do this backward
        if structBK[j][0] > 1 and structBK[j][1] > 1:
            # the entry is good: it's more than a single column or single line
            linenum = linenum - struct[j][1]
        else:
            # the entry is worthless: it's a single line
            del struct[len(structBK) + j]
            del x[linenum]
            linenum = linenum - 1
            count = count + 1

    return struct, x


def check_type(x):
    """This function returns a string. It returns "str" if x is a string, and "num" if x is a number"""
    try:
        float(x)
    except ValueError:
        verdict = "str"
    else:
        verdict = "num"

    return verdict


def skip(iterator, n):
    '''Advance the iterator n-steps ahead. If n is none, consume entirely.'''
    collections.deque(itertools.islice(iterator, n), maxlen=0)


def remove_formating(data):
    """This function removes thigns that will cause problems like endlines"""
    cleaned = []
    for i in data:
        temp = []
        for j in i:
            temp2 = []
            for k in j:
                if (k != '\n') and (k != '') and (k != '\r'):
                    temp2.append(k)
            if(len(temp2) > 0):
                temp.append(string.join(temp2, ''))
        cleaned.append(temp)

    return cleaned


if __name__ == '__main__':
    print "This code is part of CLP"
