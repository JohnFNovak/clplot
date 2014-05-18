#! /usr/bin/env python

# Part of CLP
# A universal command line plotting script
#
# John Novak

# This sub-file just holds a global dictionary

# written for Python 2.6. Requires Scipy, Numpy, and Matplotlib

dic = {'formats': [],
       'outputs': [],
       'TYPE': 'pdf',
       'MULTIT': None,
       'MULTIP': None,
       'layout': None,
       'columnsfirst': False,
       'Ucolor': [],
       'Ustyle': [],
       'x_range': None,
       'y_range': None,
       'x_label': None,
       'y_label': None,
       'x_log': False,
       'y_log': False,
       'numbered': None,
       'files': [],
       'replots': [],
       'legend': False,
       'colorstyle': [],
       'errorbands': False,
       'fontsize': 20,
       'grid': False,
       'sys_err_default': 0,
       'default_marker_size': 5,
       'plot_sys_err': False,
       'yscaled': 1,
       'xscaled': 1,
       'alpha': 0.25,
       'norm': False,
       'EmbedData': True,
       'Verbose': 0,
       'GroupBy': 'files',
       'interactive': False,
       'keep_live': False,
       'LoadFromSavePrompt': True,
       'SavePrompt': True,
       'DefaultSave': 'default_save.plots'}


if __name__ == '__main__':
    print "This code is part of CLP"
