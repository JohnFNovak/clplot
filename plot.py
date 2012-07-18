#!/usr/bin/python -tt
#KN: While OK, this isn't normal python convention. Normally, comments at the beginning of a python script say what kind of python script it is,
#or commands to the terminal on how to execute, i.e. #bin/bash/python for a python script, #bin/bash/pypi for a PyPi script, etc. Move your
#copyright/info to a README.

# A universal plotting script
#
# John Novak
# June 4, 2012


#KN: This isn't the place to put this. Docstrings go inside functions.
"""A Python program that takes a file or list of files
and creates plots of the data.
"""

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
import os
import time
import string


#Poor Python style. Variable definitions can go into the if __name__ == "__main__" part, the rest should be
#more specific functions.

# Define a main() function
def main():
        #KN: Python tabs are 4 spaces, not 2 (http://www.python.org/dev/peps/pep-0008/)
        #KN: PEP-8 is the official python style guide. Read it, use it, love it.
    # Read in the command line parameters. NB: sys.argv[0] should be 'plot.py'
    files = []
    #KN: Its usually simpler to just declare one global dictionary, and then fill in the various config settings as entries in the dict
    global formats
    formats = []
    outputs = []
    case = 0 # 0 is reading files, 1 is outputs, 2 is formats
    global TYPE
    TYPE="eps" # the default output is in eps format
    global MULTIT
    global MULTIP
    global layout
    global columnsfirst
    MULTIT = None
    MULTIP = None
    global Ucolor
    global Ustyle
    Ucolor = [] # user specified color
    Ustyle = [] # user specified point styles
    global Messy
    Messy = False # This is a global flag the notes if there is text mixed with the data or other messyness
    global remnants
    remnants = [] # This is used if multiplot pile is called and a plot has to wait for the next file to be opened
    global remnanterrors
    remnanterrors = []
    global LefttoPlot
    global x_range
    global y_range
    global x_label
    global y_label
    global x_log
    global y_log

    x_log = y_log = False
    x_range = y_range = x_label = y_label = None

    LefttoPlot = False
    columnsfirst = False
    layout = None

    if len(sys.argv)==1:
        givehelp(0)

        
    for i in range(1,len(sys.argv)):
            #KN: Its way simpler to just iterate over the items. Just do "for flag in sys.argv" and replace sys.argv[i] with flag.
            #Also, performance tweak: Check if the flag has a dash in it first, otherwise its a filename, i.e. "if '-' in flag: " 
        if "-f" == sys.argv[i]:
            # format flag
            case = 2
        elif "-i" == sys.argv[i]:
            # input file flag
            case = 0
        elif "-o" == sys.argv[i]:
            # output file flag
            case = 1
        elif "-t" == sys.argv[i]:
            # output type flag
            case = 3
        elif "-mp" == sys.argv[i]:
            # multiplot pile flag
            case = 4
        elif "-mt" == sys.argv[i]:
            # multiplot tile flag
            case = 5
        elif "-h" == sys.argv[i][:2]:
            givehelp(1)
        elif "-c" == sys.argv[i]:
            case = 6
        elif "-s" == sys.argv[i]:
            case = 7
        elif "-xr" == sys.argv[i]:
            case = 8
        elif "-yr" == sys.argv[i]:
            case = 9
        elif "-xl" == sys.argv[i]:
            case = 10
        elif "-yl" == sys.argv[i]:
            case = 11
        elif "-logx" == sys.argv[i]:
            x_log = True
        elif "-logy" == sys.argv[i]:
            y_log = True
        elif '-layout' == sys.argv[i]:
            case = 12
        elif '-columnsfirst' == sys.argv[i]:
            columnsfirst = True
        #elif "-" == sys.argv[i][:1]:
        #    case = -1
        #    print "flag",sys.argv[i],"not recognized"
        else:
            # if there is not a flag, and we are reading filenames or formats
            if case == 0:
                files.append(sys.argv[i])
            if case == 1:
                outputs.append(sys.argv[i])
            if case == 2:
                formats.append(sys.argv[i])
            if case == 3:
                TYPE = sys.argv[i]
            if case == 4:
                MULTIP=sys.argv[i] # number of plots per plot
            if case == 5:
                MULTIT = sys.argv[i] # number of plots per plot
                #if not layout:
                #    layout = plot_arragnement()
                #if layout and (layout[0]*layout[1] < int(MULTIT)):
                #    print "The layout that you specified was too small"
                #    layout = plot_arragnement()
            if case == 6:
                Ucolor.append(sys.argv[i])
            if case == 7:
                Ustyle.append(sys.argv[i])
            if case == 8:
                x_range = map(float,sys.argv[i].split(":"))
            if case == 9:
                y_range = map(float,sys.argv[i].split(":"))
            if case == 10:
                x_label = sys.argv[i]
            if case == 11:
                y_label = sys.argv[i]
            if case == 12:
                layout = tuple(map(int,sys.argv[i].split(":")))
                #if MULTIT and (layout[0]*layout[1] < int(MULTIT)):
                #    print "The layout that you specified was too small"
                #    layout = plot_arragnement()
            if case == -1:
                print "ignoring",sys.argv[i]

    if MULTIT and layout:
        if (layout[0]*layout[1] < int(MULTIT)):
            print "The layout that you specified was too small"
            layout = plot_arragnement()
        else:
            print "We are using the layout you specified:",layout[0],"by",layout[1]
    if MULTIT and not layout:
        layout = plot_arragnement()
    
    if outputs and (len(outputs)!=len(files)) and not (MULTIT or MULTIP):
        print "If you are going to specify output names, you must specify one output file per input file."

    global currentfile
    global numbered
    global Numbering
    global multicounttile
    global multicountpile

    Numbering = None

    multicounttile = 0
    multicountpile = 0

    for filename in files:
        print "plotting",filename
        currentfile=filename
        numbered = 0;
        
        #Use a context manager for this, python handles opening and closing files way more efficiently that way
        #with open(filename, 'r') as datafile:
        #     do stuff
        #http://effbot.org/zone/python-with-statement.htm

        # Now read data file
        data=read_data(filename)

        # Make decisions about what is in the file
        if len(data) > 0:
            struct=detect_blocks(data)
            #print struct
            #for i in range(len(data)):
            #    print data[i]
            
            #KN: This can be done far more efficiently using a filter() function. Either specify a one liner using a lambda function or
            #write a function that returns True or False
            struct,data=remove_empties(struct,data)
            #print struct
            #for i in range(len(data)):
            #    print data[i]

            # Plot the stuff
            #KN: Not needed. Make sure the struct is a list, and just have the for loop, followed by Numbering = len(struct) > 1
            if len(struct)>1:
                # make multiple plots, each with the name of the input file followed by a _#
                for i in range(len(struct)):
                    Numbering = True
                    x=readdat(struct,i,data)
                    smart_plot(np.array(x))
            else:
                # just make one plot, with the same name as the input file
                x=readdat(struct,0,data)
                smart_plot(np.array(x))

    if remnants:
            #KN: Where is this imported?
        plot(remnants,remnanterrors)

    if LefttoPlot:
        outputname = string.split(currentfile,".")[0]
        if numbered != 0:
            outputname = outputname+"_"+str(numbered)
        if MULTIT:
            outputname = outputname+"_tiled"
        if multicountpile != 0:
            outputname = outputname+"_"+str(multicountpile+1)
        if MULTIP:
            outputname = outputname+"_multip"
        if TYPE[0]==".":
            outputname=outputname+TYPE
        else:
            outputname=outputname+"."+TYPE
        plt.savefig(outputname)
        print"printed to",outputname


def detect_blocks(dataarray):
    """This function runs over an array of data pulled from a file and detects the structure so that the proper plotting method can be deduced
    the structure is returned as a list. Each entry is one block of the data in the form of (width of block, height of block)
    This will detect contiguous rectangular blocks of data with the same formats of text vs numbers"""
    global Messy
    
    width=[]
    height=[]
    block=0
    structure=[]
    previous=[] 

    width.append(len(dataarray[0]))
    height.append(1)
    mixed = False
    for i in range(len(dataarray[0])):
        if check_type(dataarray[0][i])=='str':
            previous.append(check_type(dataarray[0][i]))
            if i != 0:
                mixed = True
                Messy = True
        else:
            previous.append(check_type(dataarray[0][i]))
    if mixed:
        print "you seem to have text interspersed with your data"
        print "Does this look familiar?:",' '.join(dataarray[0])

    for i in range(1,len(dataarray)):
        mixed = False
        if(len(dataarray[i])==width[block]):
            good = True
            for x in range(len(dataarray[i])):
                if check_type(dataarray[i][x]) != previous[x]:
                    good = False
            if good:
                height[block]=height[block]+1;
            else:
                block=block+1;
                height.append(1);
                width.append(len(dataarray[i]))
                previous=[]
                for x in range(len(dataarray[i])):
                    if check_type(dataarray[i][x])=='str':
                        previous.append(check_type(dataarray[i][x]))
                        if x != 0:
                            mixed = True
                            Messy = True
                    else:
                        previous.append(check_type(dataarray[i][x]))
            if mixed:
                print "you seem to have text interspersed with your data"
                print "Does this look familiar?:",' '.join(dataarray[i])
        else:
            block=block+1;
            height.append(1);
            width.append(len(dataarray[i]))
            previous=[]
            for x in range(len(dataarray[i])):
                if check_type(dataarray[i][x])=='str':
                    previous.append(check_type(dataarray[i][x]))
                    if x != 0:
                        mixed = True
                        Messy = True
                else:
                    previous.append(check_type(dataarray[i][x]))
            if mixed:
                print "you seem to have text interspersed with your data"
                print "Does this look familiar?:",' '.join(dataarray[i])

    for i in range(block+1):
        #print "block",i,"is",width[i],"by",height[i]
        structure.append((width[i],height[i]));

    return structure

def smart_plot(X):
    """This function takes a rectangular arry of data and plots it first looks at the dimensions of the data, the it 'decides' the best way to plot it. Hence, 'smart plot'"""
    global numbered
    global Numbering
    global LefttoPlot

    Form = None

    z=[]
    errs=[]

    width = len(list(X[0,:]))
    height = len(list(X[:,0]))

    if len(formats)>0:
        for entry in formats:
            #print entry,len(entry),width,height
            if entry[0] == "c" and (len(entry)-1 == width or (len(entry)-1 < width and entry[-1]=="*")) and not Form:
                print "Using specified format:",entry
                Form=entry
            elif entry[0] == "r" and (len(entry)-1 == height or (len(entry)-1 < height and entry[-1]=="*")) and not Form:
                print "Using specified format:",entry
                Form=entry

    if Form:
        # Use the specified form
        mults = 0
        if Form[0] == "c":
            needx=True
            for j in range(1,len(Form)):
                if Form[j] == "x":
                    x = list(X[:,j-1])
                    needx=False
                    break
            if needx:
                print "No x specified in format"
                x = range(height)
            count = 0
            for j in range(len(Form)-1):
                if check_type(Form[j+1+mults]) == 'num':
                    if int(Form[j+1+mults]) == 1:
                        print "You are a moron, there should be no 1's in your format flag, stupid"
                    for k in range(1,int(Form[j+1+mults])):
                        if Form[j+2+mults] == "y":
                            z.append(x)
                            z.append(list(X[:,count]))
                            errs.append([0]*len(x))
                            errs.append([0]*len(list(X[count,:])))
                        #if Form[j+2+mults] == "x":
                        #    errs.append(0)
                        elif Form[j+2+mults] == "e":
                            if Form[j+1+mults] == "y": 
                                errs[-1]=list(X[count,:])
                            if Form[j+1+mults] == "x": 
                                errs[-2]=list(X[count,:])
                        count = count + 1
                    mults = mults + 1
                elif Form[j+1+mults] == "y":
                    z.append(x)
                    z.append(list(X[:,count]))
                    errs.append([0]*len(x))
                    errs.append([0]*len(list(X[:,count])))
                #elif Form[j+1+mults] == "x":
                #    errs.append(0)
                elif Form[j+1+mults] == "e":
                    if Form[j+mults] == "y": 
                        errs[-1]=list(X[:,count])
                    if Form[j+mults] == "x": 
                        errs[-2]=list(X[:,count])
                count = count + 1
                if j+mults+2 == len(Form):
                    break
        if Form[0] == "r":
            needx=True
            for j in range(1,len(Form)):
                if Form[j] == "x":
                    x = list(X[j-1,:])
                    needx=False
                    break
            if needx:
                print "No x specified in format"
                x = range(width)
            count = 0
            for j in range(len(Form)-1):
                if check_type(Form[j+1+mults]) == 'num':
                    if int(Form[j+1+mults]) == 1:
                        print "You are a moron, there should be no 1's in your format flag, stupid"
                    for k in range(1,int(Form[j+1+mults])):
                        if Form[j+2+mults] == "y":
                            z.append(x)
                            z.append(list(X[count,:]))
                            errs.append([0]*len(x))
                            errs.append([0]*len(list(X[count,:])))
                        #if Form[j+2+mults] == "x":
                        #    errs.append(0)
                        elif Form[j+2+mults] == "e":
                            if Form[j+1+mults] == "y": 
                                errs[-1]=list(X[count,:])
                            if Form[j+1+mults] == "x": 
                                errs[-2]=list(X[count,:])
                        count = count + 1
                    mults = mults + 1
                elif Form[j+1+mults] == "y":
                    z.append(x)
                    z.append(list(X[:,count]))
                    errs.append([0]*len(x))
                    errs.append([0]*len(list(X[:,count])))
                #elif Form[j+1+mults] == "x":
                #    errs.append(0)
                elif Form[j+1+mults] == "e":
                    if Form[j+mults] == "y": 
                        errs[-1]=list(X[:,count])
                    if Form[j+mults] == "x": 
                        errs[-2]=list(X[:,count])
                count = count + 1
                if j+mults+2 == len(Form):
                    break
    elif width==2 and height!=2:
        # the good old fashioned two columns
        print "the good old fashioned two columns"
        if is_it_ordered(list(X[:,0])):
            # ordered by the first column
            z=[list(X[:,0]),list(X[:,1])]
            errs = [[0] * len(z[0])] * 2
            #errs = [[0]*len(z[0])] + errs
        elif is_it_ordered(list(X[:,1])):
            # ordered by the second column
            z[list(X[:,1]),list(X[:,0])]
            errs = [[0] * len(z[0])] * 2
            #errs = [[0]*len(z[0])] + errs
        else:
            # not ordered
            print "No deducable ordering, I'll just pick which column is x"
            z=[list(X[:,0]),list(X[:,1])]
            errs = [[0] * len(z[0])] * 2
            #errs = [[0]*len(z[0])] + errs
    elif width!=2 and height==2:
        # the good old fashioned two rows
        print "the good old fashioned two rows"
        if is_it_ordered(list(X[0,:])):
            # ordered by the first row
            z=[list(X[0,:]),list(X[1,:])]
            errs = [[0] * len(z[0])] * 2
            #errs = [[0]*len(z[0])] + errs
        elif is_it_ordered(list(X[1,:])):
            # ordered by the second row
            z=[list(X[1,:]),list(X[0,:])]
            errs = [[0] * len(z[0])] * 2
            #errs = [[0]*len(z[0])] + errs
        else:
            # not ordered
            print "No deducable ordering, I'll just pick which row is x"
            z=[list(X[0,:]),list(X[1,:])]
            errs = [[0] * len(z[0])] * 2
            #errs = [[0]*len(z[0])] + errs
    elif width < 5 and height < 5:
        # we are going to have to look around for ordered things
        needx = True
        for i in range(width):
            if is_it_ordered(list(X[:,i])):
                needx = False
                xcol = i
                break
        if not needx:
            for i in range(width):
                if i != xcol:
                    errs.append([0]*len(list(X[:,xcol])))
                    errs.append([0]*len(list(X[:,i])))
                    z.append(list(X[:,xcol]))
                    z.append(list(X[:,i]))
        if needx:
            for i in range(height):
                if is_it_ordered(list(X[i,:])):
                    needx = False
                    xrow = i
                    break
            if not needx:
                for i in range(height):
                    if i != xcol:
                        errs.append([0]*len(list(X[xcol,:])))
                        errs.append([0]*len(list(X[i,:])))
                        z.append(list(X[xrow,:]))
                        z.append(list(X[i,:]))
        if needx:
            print "I don't know what to do with this block. It's",width,"by",height,"and neither axis seems to be ordered"
    elif width < 5 and height > 7:
        # we will assume that it is in columns
        needx = True
        for i in range(width):
            if is_it_ordered(list(X[:,i])):
                needx = False
                xcol = i
                break
        if not needx:
            for i in range(width):
                if i != xcol:
                    errs.append([0]*len(list(X[:,xcol])))
                    errs.append([0]*len(list(X[:,i])))
                    z.append(list(X[:,xcol]))
                    z.append(list(X[:,i]))
    elif width > 7 and height < 5:
        # we will assume that it is in rows
        needx = True
        for i in range(height):
            if is_it_ordered(list(X[i,:])):
                needx = False
                xrow = i
                break
        if not needx:
            for i in range(height):
                if i != xrow:
                    errs.append([0]*len(list(X[xcol,:])))
                    errs.append([0]*len(list(X[i,:])))
                    z.append(list(X[xrow,:]))
                    z.append(list(X[i,:]))
    elif width > 5 and height > 5:
        # will will have to look around for oredered things
        needx = True
        for i in range(width):
            if is_it_ordered(list(X[:,i])):
                needx = False
                xcol = i
                break
        if not needx:
            for i in range(width):
                if i != xcol:
                    errs.append([0]*len(list(X[:,xcol])))
                    errs.append([0]*len(list(X[:,i])))
                    z.append(list(X[:,xcol]))
                    z.append(list(X[:,i]))
        if needx:
            for i in range(height):
                if is_it_ordered(list(X[i,:])):
                    needx = False
                    xrow = i
                    break
            if not needx:
                for i in range(height):
                    if i != xrow:
                        errs.append([0]*len(list(X[xcol,:])))
                        errs.append([0]*len(list(X[i,:])))
                        z.append(list(X[xrow,:]))
                        z.append(list(X[i,:]))
        if needx:
            print "I don't know what to do with this block. It's",width,"by",height,"and neither axis seems to be ordered"
    else:
        print "I don't know what to do with this block. It's",width,"by",height

    #print z
    #print errs

    if z:
        if MULTIP:
            global remnants
            global remnanterrors
            global multicountpile
            z = remnants + z
            errs = remnanterrors + errs
            multicountpile = 0
            #print (len(z)-len(z)%int(MULTIP))/int(MULTIP)/2
            if (len(z)-len(z)%int(MULTIP))/int(MULTIP)/2 > 1:
                multicountpile = 1
            #print (len(z)-len(z)%int(MULTIP))/int(MULTIP)
            if (len(z)-len(z)%int(MULTIP))/int(MULTIP) > 0:
                for i in range(0,(len(z)-len(z)%int(MULTIP))/int(MULTIP)/2):
                    #print z[:(int(MULTIP)*2)][0][:5]
                    #print multicountpile,'\n'
                    #print (int(MULTIP)*2),len(z)
                    plot(z[:(int(MULTIP)*2)],errs[:(int(MULTIP)*2)])
                    z = z[(int(MULTIP)*2):]
                    errs = errs[(int(MULTIP)*2):]
                    multicountpile = multicountpile + 1
            remnants = z
            remnanterrors = errs
            if remnants:
                LefttoPlot = True
        else:
            # just plot it
            plot(z,errs)
        if Numbering:
            numbered = numbered + 1


def is_it_ordered(vals):
    """This function takes a list of numbers are returns whether or not they are in order"""

    ordered = False

    if vals == sorted(vals):
        ordered = True
    if vals == sorted(vals, reverse=True):
        ordered = True

    return ordered


def remove_empties(struct,x):
    """This function runs through the data and the structure array and removes entries that are either empty or are singular"""

    linenum=len(x)-1
    structBK=struct
    count=0

    for i in range(len(structBK)):
        j=-i-1+count # do this backward
        if structBK[j][0] > 1 and structBK[j][1] > 1:
            # the entry is good: it's more than a single column or single line
            linenum=linenum-struct[j][1]
        else:
            # the entry is worthless: it's a single line
            del struct[len(structBK)+j]
            del x[linenum]
            linenum=linenum-1
            count=count+1
        if i+count==len(structBK):
            break

    return struct,x


def readdat(struct,block,data):
    x=[]
    linenum=0

    for i in range(len(struct)):
        if i == block:
            # this is the block you want
            #print range(struct[i][1])
            #print data
            for j in range(struct[i][1]):
                k=j+linenum
                #print k
                x.append(data[k])
            break
        else:
            # count how many lines down you have to look
            linenum=linenum+struct[i][1]
    
    #for i in range(len(x)):
    #    print i,x[i]

    return x


def plot(z,errs):
    """This function takes a list z of lists and trys to plot them. the first list is always x, and the folowing are always y's"""

    global multicounttile
    global multicountpile
    global multifile
    global layout
    global Ucolor
    global Ustyle
    global LefttoPlot
    global x_range
    global y_range
    global x_label
    global y_label
    global x_log
    global y_log
    global columnsfirst
    points=[]

    if Ucolor:
        colors=Ucolor
    else:
        colors=['b','g','r','c','m','y','k']
    if Ustyle:
        style=Ustyle
    else:
        style=['o','.',',','v','^','<','>','-','--','-.',':','1','2','3','4','s','p','*','h','H','+','x','D','d','|','_']
    for s in style:
        for c in colors:
            points.append(str(c+s))

    if MULTIT:
        multicounttile = multicounttile + 1
        if not columnsfirst:
            plt.subplot2grid((layout[0],layout[1]),(((multicounttile-1)-(multicounttile-1)%layout[1])/layout[1],((multicounttile-1)%layout[1])))
        if columnsfirst:
            plt.subplot2grid((layout[0],layout[1]),((multicounttile-1)%layout[1])),(((multicounttile-1)-(multicounttile-1)%layout[1])/layout[1])
        plt.title(str(multicounttile))
        LefttoPlot = True

    plottingerrors = True
    #for k in errs:
    #    if k != 0:
    #        plottingerrors = True

    arg = []

    #print z
    #print errs

    for k in range(0,len(z),2):
        z[k]=map(float,z[k])
        z[k+1]=map(float,z[k+1])
        if plottingerrors:
            if errs[k] == 0:
                errs[k]=[0]*len(z[k])
            else:
                errs[k]=map(float,errs[k])
            if errs[k+1] == 0:
                plt.errorbar(z[k],z[k+1],xerr=errs[k],yerr=[0]*len(z[k+1]),fmt=points[((k+1)/2)%len(points)])
            if errs[k+1] != 0:
                errs[k+1]=map(float,errs[k+1])
                #print (z[k],z[k+1],errs[k/2],points[(k/2)%len(points)])
                plt.errorbar(z[k],z[k+1],xerr=errs[k],yerr=errs[k+1],fmt=points[((k+1)/2)%len(points)])
        if not plottingerrors:
            arg.append(z[k]) # x vector
            arg.append(z[k+1])
            arg.append(points[(k/2)%len(points)])

    if not plottingerrors:
        plt.plot(*arg)

    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    if x_log:
        plt.xscale('log')
    if y_log:
        plt.yscale('log')

    outputname = string.split(currentfile,".")[0]

    if numbered != 0:
        outputname = outputname+"_"+str(numbered)
    if MULTIT:
        outputname = outputname+"_tiled"
    if multicountpile != 0:
        outputname = outputname+"_"+str(multicountpile)
    if MULTIP:
        outputname = outputname+"_multip"
    if TYPE[0]==".":
        outputname=outputname+TYPE
    else:
        outputname=outputname+"."+TYPE

    if not MULTIT or (MULTIT and multicounttile == int(MULTIT)):
        plt.savefig(outputname)
        print"printed to",outputname
        plt.clf()
        LefttoPlot = False

    if MULTIT and multicounttile == int(MULTIT):
            multicounttile = 0


def plot_arragnement():
    """This function looks at MULTIT and decides how to structure the multiplot it returns a 2 tuple which is the root for the first 2 argument of the subplot command"""

    found = False

    if math.sqrt(float(MULTIT))%1 == 0:
        # Or multiplot can be square
        form=(int(math.sqrt(float(MULTIT))),int(math.sqrt(float(MULTIT))))
        found = True
    elif int(MULTIT) == 3:
        form=(1,3)
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(MULTIT):
            if float(MULTIT) == float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)
    if not found and math.sqrt(float(MULTIT)+1)%1 == 0:
        form=(int(math.sqrt(float(MULTIT)+1)),int(math.sqrt(float(MULTIT)+1)))
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(MULTIT)+1:
            if float(MULTIT)+1 == float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)
    if not found and math.sqrt(float(MULTIT)+2)%1 == 0:
        form=(int(math.sqrt(float(MULTIT)+2)),int(math.sqrt(float(MULTIT)+2)))
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(MULTIT)+2:
            if float(MULTIT)+2 == float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(MULTIT):
            if float(MULTIT) <= float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)

    print " I have decided that the multiplots will be",form[0],"by",form[1]

    return form


def check_type(x):
    #KN: While this is a nice job, you just recreated python's type() function
    #http://stackoverflow.com/questions/2225038/python-determine-the-type-of-an-object
    # This function returns a string. It returns "str" if x is a string, and "num" if x is a number

    try:
        float(x)
    except ValueError:
        verdict="str"
    else:
        verdict="num"

    return verdict


def skip(iterator, n):
    '''Advance the iterator n-steps ahead. If n is none, consume entirely.'''
    collections.deque(itertools.islice(iterator, n), maxlen=0)


def read_data(filename):   
    data=[]
    datafile=open(filename,"r");

    test = datafile.readline()
    while test[0] == "#" and len(test) > 1: # Not a comment or empty
        test = datafile.readline()
    delimiter = ""
    if len(test.split(" "))>1:
        delimiter = " "
    elif len(test.split(","))>1:
        delimiter = ","
    elif len(test.split(";"))>1:
        delimiter = ";"
    elif len(test.split("."))>1:
        delimiter = "."
    else:
        print "Um, we can't figure out what you are using for data seperation"
    datafile.seek(0)
    for line in datafile:
        data.append(tuple(line.split(delimiter)))

    data = remove_formating(data)
    return data


def remove_formating(data):
    """This function removes thigns that will cause problems like endlines"""
    cleaned=[]
    for i in data:
        temp=[]
        for j in i:
            if (j != '\n') and (j != ''):
                temp.append(j)
        cleaned.append(temp)

    return cleaned

def givehelp(a):
    # This command prints out some help
    #KN: Use triple quotes for this, it generates verbatim strings
    print "\nThis is a function which trys to inteligently create plots from text files."
    print "This program is 'inteligent' in that it will try various assumptions about the format of the data in the files"
    print "and the form the output should be given in. So, in many cases it can produce reasonable plots even if no information"
    print "is provided by the user other than the filenames\n"
    if a==0:
        print "for more help call this program with the '-help' flag"
    if a==1:
        print "This program takes a number of flags:"
        print "-i: Input. The input files can be listed first, or they can be listed following the '-i' flag.\n"
        print "-o: Output. The output files will be given the same names as the input files unless otherwise specified"
        print "        The output files can be specifiec by listing them after the '-o' flag"
        print "-f: Format: the format of the data in the input files can be specified with '-f'. Each format flag should start"
        print "        with either 'c' or 'r', specifying wether the data should be read as columns or row. The following characters"
        print "        each represent a row or column. They can be: 'x','y','_','*', or a numeral (<10). 'x' specifies the x values, 'y' "
        print "        specifies 'y' values'. Rows or columens marked with '_' will be skipped. 'y's or '_'s can be proceeded by a"
        print "        numeral, and the 'y' or '_' will be read that many times. Formats will only be used if their dimensions exactly fit"
        print "        the data found in the file, unless the format string is ended with a '*', then the format will be used of any data"
        print "        found in the file which has dimensions greater than or equal to that stated in the format flag."
        print "-mp: Multiplot Pile. This flag should be followed by the number of y's which the user wants to have plotted"
        print "        in the same window. It should be noted that if one block of text contains multiple y columns or rows,"
        print "        the '-mp' flag will cause them to be treated individually"
        print "-mt: Multiplot Tile. This flag should be followed by the number of tiles desired for each plot printed to file"
        print "-t: Type. The '-t' flag can be used to change the output type."
        print "        The following are acceptable: bmp, emf, eps, gif, jpeg, jpg, pdf, png, ps, raw, rgba, svg, svgz, tif, tiff"
        print "-c: Color. The '-c' flag can be used to set the color. Multiple colors can be specified and they will be iterated"
        print "        over. The color options are: b,g,r,c,m,y,k"
        print "-s: Point Style: The '-s' flag can be used to specify the point style. Multiple styles can be specified and they"
        print "        will be iterated over. The point style options are:-,--,-.,:,.,,,o,v,^,<,>,1,2,3,4,s,p,*,h,H,+,x,D,d,|,_\n"
        print "-xl,-yl: Set X and y labels. SHould be followed by a string, which can be in quotes"
        print "-logx,-logy: set X and/or Y axes to be log scales"
        print "-xr,-yr: Set scale of X and Y ranges, should be followed with two numbers sepearated by a colon. Ex: -xr 1:5"
        print "-layout: Used to specify the tiled output layout. Write input as <# rows>:<# columns>"
        print "Example:"
        print "        I have a large number of files and I would like them to be plotted with 9 plots tiled per output. I would like them to "
        print "        be eps files, and I have a thing for green circles. In each file the data is in columns 6 wide, but I only want the first"
        print "        and fourth columns plotted. The first column is x, the other will be y. I would type:"
        print "        # python plot.py * -t eps -mt 9 -c b -s o -f x3_y*"

    exit(1)


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
