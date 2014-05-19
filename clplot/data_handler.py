#! /usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak

# This sub-file handles file reading stuff

# written for Python 2.6. Requires Scipy,  Numpy,  and Matplotlib

import string
import globe
from helpers import check_type
import os


def make_blocks(dataarray):
    dic = globe.dic

    def block(d, d2):
        blank = {'dims': [len(d), 1], 'data': [], 'labels': None,
                 'Format': None, 'x_label': dic['x_label'],
                 'y_label': dic['y_label']}
        current = [check_type(x) for x in d]
        if 'str' in current:
            if dic['Verbose'] > -1:
                print "you seem to have text interspersed with your data"
                print "Does this look familiar?:", ' '.join(d)
        # if all([x == 'str' for x in current]):
        if current.count('str') > (len(current) / 2.):
            # more than half the enrties are strings, so we will assume it's
            # column titles
            if len(d) == len(d2):
                if dic['Verbose'] > -1:
                    print "we are going to use", string.join(d),
                    print "as labels"
                blank['labels'] = d
                blank['Format'] = 'c'
                blank['dims'][1] = 0
        elif (current[0] == 'str'
              and not any([x == 'str' for x in current[1:]])):
            # The first column in a string, and nothing else is
            blank['labels'] = [d[0]]
            blank['Format'] = 'r'
            blank['dims'][0] = len(d) - 1
            blank['data'].append(d)
        elif not any([x == 'str' for x in d]):
            blank['data'].append(d)

        return blank

    blocks = []
    for i, d in enumerate(dataarray):
        if i == 0:  # first pass
            blocks.append(block(d, dataarray[i + 1]))
            previous = [check_type(x) for x in d]
        else:
            current = [check_type(x) for x in d]
            check = (((current == previous)  # same as the previous pass
                      or (blocks[-1]['Format'] == 'c'
                          and blocks[-1]['dims'][1] == 0
                          and len(d) == blocks[-1]['dims'][0]))
                     and ((blocks[-1]['Format'] == 'r'
                           and not any([x == 'str' for x in current[1:]]))
                          or (blocks[-1]['Format'] != 'r'
                              and not any([x == 'str' for x in current]))))
            if check:
                blocks[-1]['dims'][1] += 1
                if blocks[-1]['Format'] == 'r':
                    blocks[-1]['labels'].append(d[0])
                    blocks[-1]['data'].append(d[1:])
                else:
                    blocks[-1]['data'].append(d)
            else:
                if blocks[-1]['dims'][1] <= 1:
                    # The previous block was only one line long
                    del(blocks[-1])
                if (i + 1) < len(dataarray):
                    blocks.append(block(d, dataarray[i + 1]))
            previous = current

    return blocks


def read_data(filename):
    if not os.path.isfile(filename):
        print filename, 'does not exist'
        return []
    with open(filename, "r") as datafile:
        test = datafile.readline()
        test = datafile.readline()
        while test[0] == "#" and len(test) > 1:  # Not a comment or empty
            test = datafile.readline()

    delimiters = [' ', ',', ';', '\t']
    while delimiters:
        d = delimiters.pop()
        if len([x.strip() for x in test.split(d) if x.strip()]) > 1:
            break
    if not d:
        print "Um,  we can't figure out what you are using for data seperation"
        return False

    with open(filename, "r") as datafile:
        data = datafile.read().split('\n')
    data = [line.split(d) for line in data if line.strip()]

    if len(data) < 2:
        print filename, 'does not contain sufficient data'
        print 'length of printable data is too short'
        return []

    return data


if __name__ == '__main__':
    print "This code is part of CLP"
