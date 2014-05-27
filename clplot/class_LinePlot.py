#! /usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak

# this sub-file holds the line plots class


class LinePlot():
    """This class represents 2d point and line plots"""
    lines = []

    def __init__(self):
        pass

    def add(self, Line):
        self.lines.append(Line)


class Line():
    """This class represents a single line in a LinePlot"""
    File_ID = -1
    Block_ID = -1
    Column_ID = -1
    filename = ''
    output = ''
    X_label = ''
    Y_label = ''
    X = []
    Y = []
    X_err = []
    Y_err = []
    X_sys_err = []
    Y_sys_err = []

    def __init__(self):
        pass

if __name__ == '__main__':
    print "This code is part of CLP"
