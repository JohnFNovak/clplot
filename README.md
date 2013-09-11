#CLP - Command Line Plotting

##A command line plotting utlity written in python

###John Novak

john (period) franc (period) novak (at) gmail (dot) com <br />
This project was born: June 6, 2012 <br />
Last Updated: Check the Repo 

####What it is:<br />
  an inteligent command line plotting utility. You give it a text file (or multiple text file) and it gives you plots. It can take a decent handfull of plotting flags giving the user the ability to make relatively complicated and customized plots quickly.

###Note to the discerning:<br />
This is not the most elegant piece of code that was ever written. This was one of the first python projects I ever took on, before I had ever even heard of 'pep8'. It grew like a wet thing in a dark corner. "Rewrite plot code" has been on my todo list for 6 months, but I haven't done it yet. Why? Two reasons: I'm trying to finish my docotrate, so this isn't a top priority, and frankly, it works. I crack it open all the time and add things that I need (like error bands, axes scaling, hollow points, etc) and I think "this needs to be gutted". But I use it literaly hundreds of times each day, and I don't want to break it. The suffering it would cause me if I broke a little something and didn't notice for even a few hours would be beyond reason. So once the university accepts my thesis, then I'll attack this. Well, maybe beer first, then I'll attack this.

####requires:<br />
python<br />
numpy<br />
matplotlib<br />

####To use:<br />
  python main.py

  for more information call<br />
    python main.py -help

####Contents of this file:<br />
main.py - the heart of the program. <br />
plot.py - sub-module handles the actual plotting. <br />
structure.py - sub-module which handles the automatic structure determination. <br />
helpers.py - sub-module which is collection of helper functions. <br />
data\_handler.py - sub-module which handles file interactions. <br />
globe.py - sub-module which holds shared globals. <br />
various .txt files - testing files
