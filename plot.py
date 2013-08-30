#!/usr/bin/python

# A universal command line plotting script
#
# John Novak
# June 4, 2012 - July 19, 2012

# Run with: python plot.py
# or just: ./plot.py (after making it executable, obviously)

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
import os
import time
import string

def main():
    global dic

    read_flags()

    if dic['MULTIT'] and dic['layout']:
        if (dic['layout'][0]*dic['layout'][1] < int(dic['MULTIT'])):
            print "The layout that you specified was too small"
            dic['layout'] = plot_arragnement()
        else:
            print "We are using the layout you specified:",dic['layout'][0],"by",dic['layout'][1]
    if dic['MULTIT'] and not dic['layout']:
        dic['layout'] = plot_arragnement()
    
    if dic['outputs'] and (len(dic['outputs'])!=len(dic['files'])) and not (dic['MULTIT'] or dic['MULTIP']):
        print "If you are going to specify output names, you must specify one output file per input file."

    for filename in dic['files']:
        print "plotting",filename
        dic['currentfile'] = filename
        dic['sys_err'] = dic['sys_err_default']
        if len(filename.split('#')) == 2:
            dic['sys_err'] = float(filename.split('#')[1])
            filename = filename.split('#')[0]
        if dic['outputs']:
            dic['currentoutput'] = dic['outputs'].pop(0)
        dic['numbered'] = 0;
        
        # Now read data file
        data=read_data(filename)

        # Make decisions about what is in the file
        if len(data) > 0:
            struct=detect_blocks(data)
            
            #KN: This can be done far more efficiently using a filter() function. Either specify a one liner using a lambda function or
            #write a function that returns True or False
            struct,data=remove_empties(struct,data)

            # Plot the stuff
            #KN: Not needed. Make sure the struct is a list, and just have the for loop, followed by Numbering = len(struct) > 1
            if len(struct)>1:
                # make multiple plots, each with the name of the input file followed by a _#
                for i in range(len(struct)):
                    dic['currentstruct']=i
                    dic['Numbering'] = True
                    x=readdat(struct,i,data)
                    smart_plot(np.array(x))
            else:
                # just make one plot, with the same name as the input file
                x=readdat(struct,0,data)
                smart_plot(np.array(x))

    if dic['remnants']:
        plot(dic['remnants'],dic['remnanterrors'])

    if dic['LefttoPlot']:
        outputname = string.split(dic['currentfile'],".")[0]
        if dic['numbered'] != 0:
            outputname = outputname+"_"+str(dic['numbered'])
        if dic['MULTIT']:
            outputname = outputname+"_tiled"
        if dic['multicountpile'] != 0:
            outputname = outputname+"_"+str(dic['multicountpile']+1)
        if dic['MULTIP']:
            outputname = outputname+"_multip"
        if dic['TYPE'][0]==".":
            outputname=outputname+dic['TYPE']
        else:
            outputname=outputname+"."+dic['TYPE']
        plt.savefig(outputname)
        print"printed to",outputname

def detect_blocks(dataarray):
    """This function runs over an array of data pulled from a file and detects the structure so that the proper plotting method can be deduced the structure is returned as a list. Each entry is one block of the data in the form of (width of block, height of block) This will detect contiguous rectangular blocks of data with the same formats of text vs numbers"""
    global dic
    
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
                dic['Messy'] = True
        else:
            previous.append(check_type(dataarray[0][i]))
    if mixed:
        print "you seem to have text interspersed with your data"
        print "Does this look familiar?:",' '.join(dataarray[0])
    if mixed and len(dataarray[0]) == len(dataarray[1]):
        print "we are going to use",string.join(dataarray[0]),"as labels"
        dic['columnlabel'].append(dataarray[0])
    else: 
        dic['columnlabel'].append(range(len(dataarray[0])))

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
                            dic['Messy'] = True
                    else:
                        previous.append(check_type(dataarray[i][x]))
            if mixed:
                print "you seem to have text interspersed with your data"
                print "Does this look familiar?:",' '.join(dataarray[i])
            if mixed and len(dataarray) != i+1:
                if len(dataarray[i]) == len(dataarray[i+1]):
                    print "we are going to use",string.join(dataarray[i]),"as labels"
                    dic['columnlabel'].append(dataarray[i])
            else: 
                dic['columnlabel'].append(range(len(dataarray[i])))
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
                        dic['Messy'] = True
                else:
                    previous.append(check_type(dataarray[i][x]))
            if mixed:
                print "you seem to have text interspersed with your data"
                print "Does this look familiar?:",' '.join(dataarray[i])
            if mixed and len(dataarray) != i+1:
                if len(dataarray[i]) == len(dataarray[i+1]):
                    print "we are going to use",string.join(dataarray[i]),"as labels"
                    dic['columnlabel'].append(dataarray[i])
            else: 
                dic['columnlabel'].append(range(len(dataarray[i])))

    for i in range(block+1):
        #print "block",i,"is",width[i],"by",height[i]
        structure.append((width[i],height[i]));

    return structure

def smart_plot(X):
    """This function takes a rectangular array of data and plots it first looks at the dimensions of the data, the it 'decides' the best way to plot it. Hence, 'smart plot'"""
    global dic

    Form = None

    z=[]
    errs=[]

    width = len(list(X[0,:]))
    height = len(list(X[:,0]))

    # Check if a prespecified format will work
    if len(dic['formats'])>0:
        for entry in dic['formats']:
            #print entry,len(entry),width,height
            if entry[0] == "c" and (len(entry)-1 == width or (len(entry)-1 < width and entry[-1]=="*")) and not Form:
                print "Using specified format:",entry
                Form=entry
            elif entry[0] == "r" and (len(entry)-1 == height or (len(entry)-1 < height and entry[-1]=="*")) and not Form:
                print "Using specified format:",entry
                Form=entry

    if Form: # If a form was specified, then use it
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
                            dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][j+mults]))
                            errs.append([0]*len(x))
                            errs.append([0]*len(list(X[count,:])))
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
                    dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][j+mults]))
                    errs.append([0]*len(x))
                    errs.append([0]*len(list(X[:,count])))
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
                            dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][j+mults]))
                            errs.append([0]*len(x))
                            errs.append([0]*len(list(X[count,:])))
                        elif Form[j+2+mults] == "e":
                            if Form[j+1+mults] == "y": 
                                errs[-1]=list(X[count,:])
                            if Form[j+1+mults] == "x": 
                                errs[-2]=list(X[count,:])
                        count = count + 1
                    mults = mults + 1
                elif Form[j+1+mults] == "y":
                    z.append(x)
                    z.append(list(X[count,:]))
                    dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][j+mults]))
                    errs.append([0]*len(x))
                    errs.append([0]*len(list(X[count,:])))
                elif Form[j+1+mults] == "e":
                    if Form[j+mults] == "y": 
                        errs[-1]=list(X[count,:])
                    if Form[j+mults] == "x": 
                        errs[-2]=list(X[count,:])
                count = count + 1
                if j+mults+2 == len(Form):
                    break
    elif width==2 and height!=2:
        # the good old fashioned two columns
        print "the good old fashioned two columns"
        if is_it_ordered(list(X[:,0])):
            # ordered by the first column
            z=[list(X[:,0]),list(X[:,1])]
            dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
            errs = [[0] * len(z[0])] * 2
        elif is_it_ordered(list(X[:,1])):
            # ordered by the second column
            z[list(X[:,1]),list(X[:,0])]
            dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
            errs = [[0] * len(z[0])] * 2
        else:
            # not ordered
            print "No deducable ordering, I'll just pick which column is x"
            z=[list(X[:,0]),list(X[:,1])]
            dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
            errs = [[0] * len(z[0])] * 2
    elif width!=2 and height==2:
        # the good old fashioned two rows
        print "the good old fashioned two rows"
        if is_it_ordered(list(X[0,:])):
            # ordered by the first row
            z=[list(X[0,:]),list(X[1,:])]
            dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
            errs = [[0] * len(z[0])] * 2
        elif is_it_ordered(list(X[1,:])):
            # ordered by the second row
            z=[list(X[1,:]),list(X[0,:])]
            dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
            errs = [[0] * len(z[0])] * 2
        else:
            # not ordered
            print "No deducable ordering, I'll just pick which row is x"
            z=[list(X[0,:]),list(X[1,:])]
            errs = [[0] * len(z[0])] * 2
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
                    dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
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
                        dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
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
                    dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
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
                    dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
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
                    dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
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
                        dic['labels'].append(dic['currentfile']+"/"+str(dic['columnlabel'][dic['currentstruct']][int(len(z)/2)]))
        if needx:
            print "I don't know what to do with this block. It's",width,"by",height,"and neither axis seems to be ordered"
    else:
        print "I don't know what to do with this block. It's",width,"by",height

    if z:
        new_err = []
        new_z = []
        for k in range(len(z)/2):
            new_err.append([[],[]])
            new_err.append([[],[]])
            for l in range(len(z[2*k+1])):
                new_err[2*k][0].append(errs[2*k][l])
                new_err[2*k][1].append(errs[2*k][l])
                new_err[2*k+1][0].append(float(errs[2*k+1][l]))
                new_err[2*k+1][1].append(dic['sys_err']*float(z[2*k+1][l]))
        errs = new_err
        if dic['MULTIP']:
            z = dic['remnants'] + z
            errs = dic['remnanterrors'] + errs
            dic['multicountpile'] = 0
            if (len(z)-len(z)%int(dic['MULTIP']))/int(dic['MULTIP'])/2 > 1:
                dic['multicountpile'] = 1
            if (len(z)-len(z)%int(dic['MULTIP']))/int(dic['MULTIP']) > 0:
                for i in range(0,(len(z)-len(z)%int(dic['MULTIP']))/int(dic['MULTIP'])/2):
                    plot(z[:(int(dic['MULTIP'])*2)],errs[:(int(dic['MULTIP'])*2)])
                    z = z[(int(dic['MULTIP'])*2):]
                    errs = errs[(int(dic['MULTIP'])*2):]
                    dic['multicountpile'] = dic['multicountpile'] + 1
            dic['remnants'] = z
            dic['remnanterrors'] = errs
            if dic['remnants']:
                dic['LefttoPlot'] = True
        else:
            # just plot it
            plot(z,errs)
        if dic['Numbering']:
            dic['numbered'] = dic['numbered'] + 1

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
    blocks=len(structBK)

    for i in range(blocks):
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

    return struct,x

def readdat(struct,block,data):
    x=[]
    linenum=0

    for i in range(len(struct)):
        if i == block:
            # this is the block you want
            for j in range(struct[i][1]):
                k=j+linenum
                x.append(data[k])
            break
        else:
            # count how many lines down you have to look
            linenum=linenum+struct[i][1]
    
    return x

def plot(z,errs):
    """This function takes a list z of lists and trys to plot them. the first list is always x, and the folowing are always y's"""

    #print z
    #print errs

    global dic
    points=dic['colorstyle']

    if dic['Ucolor']:
        colors=dic['Ucolor']
    else:
        colors=['b','g','r','c','m','y','k']
    if dic['Ustyle']:
        style=dic['Ustyle']
    else:
        style=['o','v','^','<','>','1','2','3','4','-','--','-.',':','s','p','*','h','H','+','x','D','d','|','_','.',',']
    for s in style:
        for c in colors:
            points.append(str(c+s))

    size = [dic['default_marker_size']]*len(points)
    for i in range(len(points)):
        if len(points[i].split(';')) == 2:
            points[i] = points[i].split(';')[0]
            size[i] = float(points[i].split(';')[1])

    if dic['MULTIT']:
        dic['multicounttile'] = dic['multicounttile'] + 1
        if not dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0],dic['layout'][1]),(((dic['multicounttile']-1)-(dic['multicounttile']-1)%dic['layout'][1])/dic['layout'][1],((dic['multicounttile']-1)%dic['layout'][1])))
        if dic['columnsfirst']:
            plt.subplot2grid((dic['layout'][0],dic['layout'][1]),((dic['multicounttile']-1)%dic['layout'][1])),(((dic['multicounttile']-1)-(dic['multicounttile']-1)%dic['layout'][1])/dic['layout'][1])
        plt.title(str(dic['multicounttile']))
        dic['LefttoPlot'] = True

    plottingerrors = True
    #for k in errs:
    #    if k != 0:
    #        plottingerrors = True

    arg = []

    if dic['x_range']:
        plt.xlim(dic['x_range'])
    if dic['y_range']:
        plt.ylim(dic['y_range'])
    if dic['x_label']:
        plt.xlabel(dic['x_label'], fontsize = dic['fontsize'])
    if dic['y_label']:
        plt.ylabel(dic['y_label'], fontsize = dic['fontsize'])
    if dic['x_log']:
        plt.xscale('log', nonposx='clip')
    if dic['y_log']:
        plt.yscale('log', nonposy='clip')

    plt.tick_params(axis='both', which='major', labelsize=dic['fontsize']*0.75)
    plt.tick_params(axis='both', which='minor', labelsize=dic['fontsize']*0.75)

    if dic['legend'] and len(dic['labels']) > 1:
        parse_legend();

    for k in range(0,len(z),2):
        marker = points[((k+1)/2)%len(points)]
        msize  = size[((k+1)/2)%len(points)]
        ecolor = points[((k+1)/2)%len(points)][0]
        fcolor = points[((k+1)/2)%len(points)][0]
        if marker[-1] == '!':
            fcolor = 'white'
            marker = marker[:-1]
        z[k]=map(lambda x: float(x) * dic['xscaled'],z[k])
        z[k+1]=map(lambda x: float(x) * dic['yscaled'],z[k+1])
        #z[k+1]=map(float,z[k+1])
        if plottingerrors and not dic['errorbands']:
            if errs[k][0] == 0:
                errs[k][0]=[0]*len(z[k])
            else:
                errs[k][0]=map(lambda x: float(x) * dic['xscaled'],errs[k][0])
            if errs[k+1][0] == 0:
                plt.errorbar(z[k],z[k+1],xerr=errs[k][0],yerr=[0]*len(z[k+1]),fmt=marker,label=dic['labels'][(k+1)/2],mec=ecolor,mfc=fcolor,ms=msize)
            if errs[k+1][0] != 0:
                errs[k+1][0]=map(lambda x: float(x) * dic['yscaled'],errs[k+1][0])
                plt.errorbar(z[k],z[k+1],xerr=errs[k][0],yerr=errs[k+1][0],fmt=marker,label=dic['labels'][(k+1)/2],mec=ecolor,mfc=fcolor,ms=msize)
        if plottingerrors and dic['errorbands']:
            if errs[k][0] == 0:
                errs[k][0]=[0]*len(z[k])
            else:
                errs[k][0]=map(lambda x: float(x) * dic['xscaled'],errs[k][0])
            if errs[k+1][0] == 0:
                plt.errorbar(z[k],z[k+1],xerr=[0]*len(errs[k][0]),yerr=[0]*len(z[k+1]),fmt=marker,label=dic['labels'][(k+1)/2],mec=ecolor,mfc=fcolor,ms=msize)
            if errs[k+1][0] != 0:
                errs[k+1][0]=map(lambda x: float(x) * dic['yscaled'],errs[k+1][0])
                plt.errorbar(z[k],z[k+1],xerr=[0]*len(errs[k][0]),yerr=[0]*len(errs[k+1][0]),fmt=marker,label=dic['labels'][(k+1)/2],mec=ecolor,mfc=fcolor,ms=msize)
                plt.fill_between(np.array(z[k]),np.array(z[k+1])+np.array(errs[k+1][0]),np.array(z[k+1])-np.array(errs[k+1][0]),facecolor=ecolor,alpha=dic['alpha'],interpolate=True,linewidth=0)
        if dic['plot_sys_err']:
            plt.fill_between(np.array(z[k]),np.array(z[k+1])+np.array(errs[k+1][1]),np.array(z[k+1])-np.array(errs[k+1][1]),facecolor=ecolor,alpha=dic['alpha'],interpolate=True,linewidth=0)
        if not plottingerrors:
            arg.append(z[k]) # x vector
            arg.append(z[k+1])
            arg.append(points[(k/2)%len(points)])

    if not plottingerrors:
        plt.plot(*arg)

    plt.grid(True)

    if dic['legend']:
        plt.legend()
        dic['labels']=[]

    if dic['currentoutput']:
        outputname = dic['currentoutput']
    else:
        outputname = string.split(dic['currentfile'],".")[0]

    if dic['numbered'] != 0:
        outputname = outputname+"_"+str(dic['numbered'])
    if dic['MULTIT']:
        outputname = outputname+"_tiled"
    if dic['multicountpile'] != 0:
        outputname = outputname+"_"+str(dic['multicountpile'])
    if dic['MULTIP']:
        outputname = outputname+"_multip"
    if dic['TYPE'][0]==".":
        outputname=outputname+dic['TYPE']
    else:
        outputname=outputname+"."+dic['TYPE']

    if not dic['MULTIT'] or (dic['MULTIT'] and dic['multicounttile'] == int(dic['MULTIT'])):
        plt.savefig(outputname)
        print"printed to",outputname
        plt.clf()
        dic['LefttoPlot'] = False

    if dic['MULTIT'] and dic['multicounttile'] == int(dic['MULTIT']):
            dic['multicounttile'] = 0

def plot_arragnement():
    """This function looks at dic['MULTIT'] and decides how to structure the multiplot it returns a 2 tuple which is the root for the first 2 argument of the subplot command"""

    found = False

    if math.sqrt(float(dic['MULTIT']))%1 == 0:
        # Or multiplot can be square
        form=(int(math.sqrt(float(dic['MULTIT']))),int(math.sqrt(float(dic['MULTIT']))))
        found = True
    elif int(dic['MULTIT']) == 3:
        form=(1,3)
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(dic['MULTIT']):
            if float(dic['MULTIT']) == float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)
    if not found and math.sqrt(float(dic['MULTIT'])+1)%1 == 0:
        form=(int(math.sqrt(float(dic['MULTIT'])+1)),int(math.sqrt(float(dic['MULTIT'])+1)))
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(dic['MULTIT'])+1:
            if float(dic['MULTIT'])+1 == float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)
    if not found and math.sqrt(float(dic['MULTIT'])+2)%1 == 0:
        form=(int(math.sqrt(float(dic['MULTIT'])+2)),int(math.sqrt(float(dic['MULTIT'])+2)))
        found = True
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(dic['MULTIT'])+2:
            if float(dic['MULTIT'])+2 == float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)
    if not found:
        looking = True
        a = 1
        while looking and a*(a+1) <= int(dic['MULTIT']):
            if float(dic['MULTIT']) <= float(a*(a+1)):
                looking = False
                found = True
            else:
                a = a+1
        if found:
            form = (a,a+1)

    print " I have decided that the multiplots will be",form[0],"by",form[1]

    return form

def check_type(x):
    """This function returns a string. It returns "str" if x is a string, and "num" if x is a number"""

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
    delimiter = " "
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
    datafile.close()

    data = remove_formating(data)
    return data

def remove_formating(data):
    """This function removes thigns that will cause problems like endlines"""
    cleaned=[]
    for i in data:
        temp=[]
        for j in i:
            temp2=[]
            for k in j:
                if (k != '\n') and (k != '') and (k!='\r'):
                    temp2.append(k)
            if(len(temp2)>0):
                temp.append(string.join(temp2,''))
        cleaned.append(temp)

    return cleaned

def read_flags():
    global dic
    case = 0 # 0 is reading files, 1 is outputs, 2 is formats, etc

    if len(sys.argv)==1:
        givehelp(0)

    for flag in sys.argv[1:]:
            #performance tweak: Check if the flag has a dash in it first, otherwise its a filename, i.e. "if '-' in flag: " 
        if "-f" == flag:
            # format flag
            case = 2
        elif "-i" == flag:
            # input file flag
            case = 0
        elif "-o" == flag:
            # output file flag
            case = 1
        elif "-t" == flag:
            # output type flag
            case = 3
        elif "-mp" == flag:
            # multiplot pile flag
            case = 4
        elif "-mt" == flag:
            # multiplot tile flag
            case = 5
        elif "-h" == flag[:2]:
            givehelp(1)
        elif "-c" == flag:
            case = 6
        elif "-s" == flag:
            case = 7
        elif "-xr" == flag:
            case = 8
        elif "-yr" == flag:
            case = 9
        elif "-xl" == flag:
            case = 10
        elif "-yl" == flag:
            case = 11
        elif "-logx" == flag:
            dic['x_log'] = True
            if dic['x_range']:
                if dic['x_range'][0] <= 0:
                    dic['x_range'] = None
        elif "-logy" == flag:
            dic['y_log'] = True
            if dic['y_range']:
                if dic['y_range'][0] <= 0:
                    dic['y_range'] = None
        elif '-layout' == flag:
            case = 12
        elif '-cs' == flag:
            case = 13
        elif '-fontsize' == flag:
            case = 14
        elif '-systematic' == flag:
            case = 15
        elif '-xscaled' == flag:
            case = 16
        elif '-yscaled' == flag:
            case = 17
        elif '-markersize' == flag:
            case = 18
        elif '-alpha' == flag:
            case = 19
        elif '-columnsfirst' == flag:
            dic['columnsfirst'] = True
        elif "-legend" == flag:
            dic['legend'] = True
        elif '-bands' == flag:
            dic['errorbands'] = True
        elif '-grid' == flag:
            dic['grid'] = True
        elif '-sys_err' == flag:
            dic['plot_sys_err'] = True
        elif "-" == flag[0] and case != 7 and case != 8 and case != 9:
            case = -1
            print "flag",flag,"not recognized"
        else:
            # if there is not a flag, and we are reading filenames or formats
            if case == 0:
                dic['files'].append(flag)
            if case == 1:
                dic['outputs'].append(flag)
            if case == 2:
                dic['formats'].append(flag)
            if case == 3:
                dic['TYPE'] = flag
            if case == 4:
                dic['MULTIP']=flag # number of plots per plot
            if case == 5:
                dic['MULTIT'] = flag # number of plots per plot
            if case == 6:
                dic['Ucolor'].append(flag)
            if case == 7:
                dic['Ustyle'].append(flag)
            if case == 8:
                dic['x_range'] = map(float,flag.split(":"))
            if case == 9:
                dic['y_range'] = map(float,flag.split(":"))
            if case == 10:
                dic['x_label'] = flag
            if case == 11:
                dic['y_label'] = flag
            if case == 12:
                dic['layout'] = tuple(map(int,flag.split(":")))
            if case == -1:
                print "ignoring",flag

def parse_legend():
    global dic
    delimiters = ['/','-','.','/','-','.']

    for divider in delimiters:
        tester=dic['labels'][0].split(divider)

        #From the front
        for i in dic['labels']:
            if len(i.split(divider)) > len(tester):
                tester=i.split(divider)
        hold=[0]*len(tester)

        for i in range(1,len(dic['labels'])):
            for j in range(len(dic['labels'][i].split(divider))):
                if tester[j] == dic['labels'][i].split(divider)[j] and hold[j] == 0:
                    hold[j]=1
                if tester[j] != dic['labels'][i].split(divider)[j] and hold[j] == 1:
                    hold[j]=0

        for i in range(len(hold)):
            if hold[len(hold)-1-i] == 1:
                for j in range(len(dic['labels'])):
                    temp=[]
                    for k in range(len(dic['labels'][j].split(divider))):
                        if k != len(hold)-1-i:
                            temp.append(dic['labels'][j].split(divider)[k])
                    dic['labels'][j]=string.join(temp,divider)

        tester=dic['labels'][0].split(divider)

        #From the back
        for i in dic['labels']:
            if len(i.split(divider)) > len(tester):
                tester=i.split(divider)
        hold=[0]*len(tester)

        for i in range(1,len(dic['labels'])):
            for j in range(len(dic['labels'][i].split(divider))):
                if tester[len(dic['labels'][i].split(divider))-1-j] == dic['labels'][i].split(divider)[len(dic['labels'][i].split(divider))-1-j] and hold[len(dic['labels'][i].split(divider))-1-j] == 0:
                    hold[len(dic['labels'][i].split(divider))-1-j]=1
                if tester[len(dic['labels'][i].split(divider))-1-j] != dic['labels'][i].split(divider)[len(dic['labels'][i].split(divider))-1-j] and hold[len(dic['labels'][i].split(divider))-1-j] == 1:
                    hold[len(dic['labels'][i].split(divider))-1-j]=0

        for i in range(len(hold)):
            if hold[len(hold)-1-i] == 1:
                for j in range(len(dic['labels'])):
                    temp=[]
                    for k in range(len(dic['labels'][j].split(divider))):
                        if k != len(hold)-1-i:
                            temp.append(dic['labels'][j].split(divider)[k])
                    dic['labels'][j]=string.join(temp,divider)

def givehelp(a):
    """This command prints out some help"""

    print """This is a function which trys to inteligently create plots from text files. This program is 'inteligent' in that it will try various assumptions about the format of the data in the files and the form the output should be given in. So, in many cases it can produce reasonable plots even if no information is provided by the user other than the filenames\n"""
    if a==0:
        print "for more help call this program with the '-help' flag"
    if a==1:
        print """This program takes a number of flags:
        -i: Input. The input files can be listed first, or they can be listed following the '-i' flag.\n
        -o: Output. The output files will be given the same names as the input files unless otherwise specified. The output files can be specifiec by listing them after the '-o' flag
        -f: Format: the format of the data in the input files can be specified with '-f'. Each format flag should start with either 'c' or 'r', specifying wether the data should be read as columns or row. The following characters each represent a row or column. They can be: 'x','y','_','*', or a numeral (<10). 'x' specifies the x values, 'y' specifies 'y' values'. Rows or columens marked with '_' will be skipped. 'y's or '_'s can be proceeded by a numeral, and the 'y' or '_' will be read that many times. Formats will only be used if their dimensions exactly fit the data found in the file, unless the format string is ended with a '*', then the format will be used of any data found in the file which has dimensions greater than or equal to that stated in the format flag.
        -mp: Multiplot Pile. This flag should be followed by the number of y's which the user wants to have plotted in the same window. It should be noted that if one block of text contains multiple y columns or rows, the '-mp' flag will cause them to be treated individually
        -mt: Multiplot Tile. This flag should be followed by the number of tiles desired for each plot printed to file
        -t: Type. The '-t' flag can be used to change the output type. The following are acceptable: bmp, emf, eps, gif, jpeg, jpg, pdf, png, ps, raw, rgba, svg, svgz, tif, tiff
        -c: Color. The '-c' flag can be used to set the color. Multiple colors can be specified and they will be iterated over. The color options are: b,g,r,c,m,y,k
        -s: Point Style: The '-s' flag can be used to specify the point style. Multiple styles can be specified and they will be iterated over. The point style options are:-,--,-.,:,.,,,o,v,^,<,>,1,2,3,4,s,p,*,h,H,+,x,D,d,|,_
        -xl,-yl: Set X and y labels. SHould be followed by a string, which can be in quotes
        -logx,-logy: set X and/or Y axes to be log scales
        -xr,-yr: Set scale of X and Y ranges, should be followed with two numbers sepearated by a colon. Ex: -xr 1:5
        -layout: Used to specify the tiled output layout. Write input as <# rows>:<# columns>
        -legend: This will turn on keys in the plots. On each plot things will be named using a unique combination of column heading, column number, and filename
        
        Example:
            I have a large number of files and I would like them to be plotted with 9 plots tiled per output. I would like them to be eps files, and I have a thing for green circles. In each file the data is in columns 6 wide, but I only want the first and fourth columns plotted. The first column is x, the other will be y. I would type:
            # python plot.py * -t eps -mt 9 -c b -s o -f x3_y*"""

    exit(1)


if __name__ == '__main__':
    """A Python program that takes a file or list of filesand creates plots of the data."""
    global dic # All global values are being dumped in here
    dic = { 'formats':[],'outputs':[],'TYPE':'pdf','MULTIT':None,'MULTIP':None,'layout':None,'columnsfirst':False,'Ucolor':[],'Ustyle':[],'Messy':False,'remnants':[],'remnanterrors':[],'LefttoPlot':False,'x_range':None,'y_range':None,'x_label':None,'y_label':None,'x_log':False,'y_log':False,'currentfile':None,'numbered':None,'Numbering':None,'multicounttile':0,'multicountpile':0,'currentoutput':None,'files':[],'legend':False,'labels':[],'columnlabel':[],'currentstruct':0,'colorstyle':[],'errorbands':False, 'fontsize':20, 'grid':False,'sys_err_default':0,'default_marker_size':5,'sys_err':0,'plot_sys_err':False, 'yscaled':1, 'xscaled':1, 'alpha':0.25}
    main()
