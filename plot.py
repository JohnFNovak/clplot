# A universal plotting script
#
# John Novak
# June 4, 2012


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
import itertools
import collections


# Define a main() function
def main():
  # Read in the command line parameters. NB: sys.argv[0] should be 'plot.py'
  files = []
  global formats
  formats = []
  outputs = []
  case = 0 # 0 is reading files, 1 is outputs, 2 is formats
  global TYPE
  TYPE="png" # the default output is in png format
  global MULTIT
  global MULTIP
  global layout
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
  global LefttoPlot

  LefttoPlot = False

  if len(sys.argv)==1:
    givehelp(0)
  for i in range(1,len(sys.argv)):
    if "-f" == sys.argv[i][:2]:
      # format flag
      case = 2
    elif "-i" == sys.argv[i][:2]:
      # input file flag
      case = 0
    elif "-o" == sys.argv[i][:2]:
      # output file flag
      case = 1
    elif "-t" == sys.argv[i][:2]:
      # output type flag
      case = 3
    elif "-mp" == sys.argv[i][:3]:
      # multiplot pile flag
      case = 4
    elif "-mt" == sys.argv[i][:3]:
      # multiplot tile flag
      case = 5
    elif "-help" == sys.argv[i][:5] or "-h" == sys.argv[i][:2]:
      givehelp(1)
    elif "-color" == sys.argv[i][:6] or "-c" == sys.argv[i][:2]:
      case = 6
    elif "-s" == sys.argv[i][:2]:
      case = 7
    #elif "-" == sys.argv[i][:1]:
    #  case = -1
    #  print "flag",sys.argv[i],"not recognized"
    else:
      # if there is not a flag, and we are reading filenames or formats
      if case == 0:
        files.append(sys.argv[i])
      if case == 1:
        outputs.append(sys.argv[i])
      if case == 2:
        formats.append(sys.argv[i])
      if case == 3:
        TYPE=sys.argv[i]
      if case == 4:
        MULTIP=sys.argv[i] # number of plots per plot
      if case == 5:
        MULTIT=sys.argv[i] # number of plots per plot
        layout=plot_arragnement()
      if case == 6:
        Ucolor.append(sys.argv[i])
      if case == 7:
        Ustyle.append(sys.argv[i])
      if case == -1:
        print "ignoring",sys.argv[i]
  
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
    data=[]
    datafile=open(filename,"r");

    # Now read data file
    for line in datafile:
      data.append(tuple(line.split()))

    # Make decisions about what is in the file
    struct=detect_blocks(data)
    #print struct
    #for i in range(len(data)):
    #  print data[i]

    struct,data=remove_empties(struct,data)
    #print struct
    #for i in range(len(data)):
      #print data[i]

    # Plot the stuff
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
    plot(remnants)

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
  # This function runs over an array of data pulled from a file and detects
  # the structure so that the proper plotting method can be deduced
  #
  # the structure is returned as a list. Each entry is one block of the 
  # data in the form of (width of block, height of block)
  #
  # This will detect contiguous rectangular blocks of data with the same 
  # formats of text vs numbers
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
    if check_type(dataarray[0][i])=="str":
      previous.append("str")
      if i != 0:
        mixed = True
        Messy = True
    else:
      previous.append("num")
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
          if check_type(dataarray[i][x])=="str":
            previous.append("str")
            if x != 0:
              mixed = True
              Messy = True
          else:
            previous.append("num")
      if mixed:
        print "you seem to have text interspersed with your data"
        print "Does this look familiar?:",' '.join(dataarray[i])
    else:
      block=block+1;
      height.append(1);
      width.append(len(dataarray[i]))
      previous=[]
      for x in range(len(dataarray[i])):
        if check_type(dataarray[i][x])=="str":
          previous.append("str")
          if x != 0:
            mixed = True
            Messy = True
        else:
          previous.append("num")
      if mixed:
        print "you seem to have text interspersed with your data"
        print "Does this look familiar?:",' '.join(dataarray[i])

  for i in range(block+1):
    #print "block",i,"is",width[i],"by",height[i]
    structure.append((width[i],height[i]));

  return structure

def smart_plot(X):
  # This function takes a rectangular arry of data and plots it
  # it first looks at the dimensions of the data, the it 
  # 'decides' the best way to plot it. Hence, 'smart plot'
  global numbered
  global Numbering
  global LefttoPlot

  Form = None

  z=[]

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
        if check_type(Form[j+1+mults]) == "num":
          if int(Form[j+1+mults]) == 1:
            print "You are a moron, there should be no 1's in your format flag, stupid"
          for k in range(1,int(Form[j+1+mults])):
            if Form[j+2+mults] == "y":
              z.append(x)
              z.append(list(X[:,count]))
            elif Form[j+2+mults] == "e":
              print "errors are being ignored for now until we can learn to plot them"
            count = count + 1
          mults = mults + 1
        elif Form[j+1+mults] == "y":
          z.append(x)
          z.append(list(X[:,count]))
        elif Form[j+1+mults] == "e":
          print "errors are being ignored for now until we can learn to plot them"
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
        if check_type(Form[j+1+mults]) == "num":
          if int(Form[j+1+mults]) == 1:
            print "You are a moron, there should be no 1's in your format flag, stupid"
          for k in range(1,int(Form[j+1+mults])):
            if Form[j+2+mults] == "y":
              z.append(x)
              z.append(list(X[count,:]))
            elif Form[j+2+mults] == "e":
              print "errors are being ignored for now until we can learn to plot them"
            count = count + 1
          mults = mults + 1
        elif Form[j+1+mults] == "y":
          z.append(x)
          z.append(list(X[count,:]))
        elif Form[j+1+mults] == "e":
          print "errors are being ignored for now until we can learn to plot them"
        count = count + 1
        if j+mults+2 == len(Form):
          break
  elif width==2 and height!=2:
    # the good old fashioned two columns
    print "the good old fashioned two columns"
    if is_it_ordered(list(X[:,0])):
      # ordered by the first column
      z=[list(X[:,0]),list(X[:,1])]
    elif is_it_ordered(list(X[:,1])):
      # ordered by the second column
      z[list(X[:,1]),list(X[:,0])]
    else:
      # not ordered
      print "No deducable ordering, I'll just pick which column is x"
      z=[list(X[:,0]),list(X[:,1])]
  elif width!=2 and height==2:
    # the good old fashioned two rows
    print "the good old fashioned two rows"
    if is_it_ordered(list(X[0,:])):
      # ordered by the first row
      z=[list(X[0,:]),list(X[1,:])]
    elif is_it_ordered(list(X[1,:])):
      # ordered by the second row
      z=[list(X[1,:]),list(X[0,:])]
    else:
      # not ordered
      print "No deducable ordering, I'll just pick which row is x"
      z=[list(X[0,:]),list(X[1,:])]
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
          z.append(list(X[xrow,:]))
          z.append(list(X[i,:]))
  elif width > 5 and height > 5 and not (width > 12 and height > 12) :
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
            z.append(list(X[xrow,:]))
            z.append(list(X[i,:]))
    if needx:
      print "I don't know what to do with this block. It's",width,"by",height,"and neither axis seems to be ordered"
  else:
    print "I don't know what to do with this block. It's",width,"by",height

  if z:
    if MULTIP:
      global remnants
      global multicountpile
      z = remnants + z
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
          plot(z[:(int(MULTIP)*2)])
          z = z[(int(MULTIP)*2):]
          multicountpile = multicountpile + 1
      remnants = z
      if remnants:
        LefttoPlot = True
    else:
      # just plot it
      plot(z)
    if Numbering:
      numbered = numbered + 1


def is_it_ordered(vals):
  # This function takes a list of numbers are returns whether
  # or not they are in order

  ordered = False

  if vals == sorted(vals):
    ordered = True
  if vals == sorted(vals, reverse=True):
    ordered = True

  return ordered


def remove_empties(struct,x):
  # This function runs through the data and the structure array and
  # removes entries that are either empty or are singular

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
  #  print i,x[i]

  return x


def plot(z):
  # This function takes a list z of lists and trys to plot them.
  # the first list is always x, and the folowing are always y's

  global multicounttile
  global multicountpile
  global multifile
  global layout
  global Ucolor
  global Ustyle
  global LefttoPlot
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
    plt.subplot2grid((layout[0],layout[1]),(((multicounttile-1)-(multicounttile-1)%layout[1])/layout[1],((multicounttile-1)%layout[1])))
    plt.title(str(multicounttile))
    LefttoPlot = True

  arg=[]

  for k in range(0,len(z),2):
    arg.append(z[k]) # x vector
    arg.append(z[k+1]) # y vector
    arg.append(points[(k/2)%len(points)]) # we loop over the point styles

  plt.plot(*arg);
  plt.hold()

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
  # THis function looks at MULTIT and decides how to structure the multiplot
  # it returns a 2 tuple which is the root for the first 2 argument of the subplot command

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


def givehelp(a):
  # This command prints out some help
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
    print "    The output files can be specifiec by listing them after the '-o' flag"
    print "-f: Format: the format of the data in the input files can be specified with '-f'. Each format flag should start"
    print "    with either 'c' or 'r', specifying wether the data should be read as columns or row. The following characters"
    print "    each represent a row or column. They can be: 'x','y','_','*', or a numeral (<10). 'x' specifies the x values, 'y' "
    print "    specifies 'y' values'. Rows or columens marked with '_' will be skipped. 'y's or '_'s can be proceeded by a"
    print "    numeral, and the 'y' or '_' will be read that many times. Formats will only be used if their dimensions exactly fit"
    print "    the data found in the file, unless the format string is ended with a '*', then the format will be used of any data"
    print "    found in the file which has dimensions greater than or equal to that stated in the format flag."
    print "-mp: Multiplot Pile. This flag should be followed by the number of y's which the user wants to have plotted"
    print "    in the same window. It should be noted that if one block of text contains multiple y columns or rows,"
    print "    the '-mp' flag will cause them to be treated individually"
    print "-mt: Multiplot Tile. This flag should be followed by the number of tiles desired for each plot printed to file"
    print "-t: Type. The '-t' flag can be used to change the output type."
    print "    The following are acceptable: bmp, emf, eps, gif, jpeg, jpg, pdf, png, ps, raw, rgba, svg, svgz, tif, tiff"
    print "-c: Color. The '-c' flag can be used to set the color. Multiple colors can be specified and they will be iterated"
    print "    over. The color options are: b,g,r,c,m,y,k"
    print "-s: Point Style: The '-s' flag can be used to specify the point style. Multiple styles can be specified and they"
    print "    will be iterated over. The point style options are:-,--,-.,:,.,,,o,v,^,<,>,1,2,3,4,s,p,*,h,H,+,x,D,d,|,_\n"
    print "Example:"
    print "    I have a large number of files and I would like them to be plotted with 9 plots tiled per output. I would like them to "
    print "    be eps files, and I have a thing for green circles. In each file the data is in columns 6 wide, but I only want the first"
    print "    and fourth columns plotted. The first column is x, the other will be y. I would type:"
    print "    # python plot.py * -t eps -mt 9 -c b -s o -f x3_y*"

  exit(1)


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()
