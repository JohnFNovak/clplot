#clplot - Command Line Plotting

##A command line plotting utility written in python

###John Novak

john (period) franc (period) novak (at) gmail (dot) com <br />
This project was born: June 6, 2012 <br />
Last Updated: Check the Repo 

####What it is:<br />
  an intelligent command line plotting utility. You give it a text file (or multiple text files) and it gives you plots. It can take a decent handful of plotting flags giving the user the ability to make relatively complicated and customized plots quickly.

###Note to the discerning:<br />
Sep 11, 2013:
>This is not the most elegant piece of code that was ever written. This was one of the first python projects I ever took on, before I had ever even heard of 'pep8'. It grew like a wet thing in a dark corner. "Rewrite plot code" has been on my to-do list for 6 months, but I haven't done it yet. Why? Two reasons: I'm trying to finish my doctorate, so this isn't a top priority, and frankly, it works. I crack it open all the time and add things that I need (like error bands, axes scaling, hollow points, etc) and I think "this needs to be gutted". Once the university accepts my thesis, then I'll attack this. Well, maybe beer first, then I'll attack this.<br />

May 9, 2014: The time has come to get this code up to snuff. I have returned, christened with my PhD.


####requires:<br />
python<br />
numpy<br />
matplotlib<br />

####To use:<br />
  python clplot.py <something to plot>

  for more information call<br />
    python clplot.py -help

####Contents of this file:<br />
clplot/clplot.py - the heart of the program. <br />
clplot/plot.py - sub-module handles the actual plotting. <br />
clplot/structure.py - sub-module which handles the automatic structure determination. <br />
clplot/helpers.py - sub-module which is collection of helper functions. <br />
clplot/data\_handler.py - sub-module which handles file interactions. <br />
clplot/globe.py - sub-module which holds shared globals. <br />
clplot/test/various .txt files - testing files
