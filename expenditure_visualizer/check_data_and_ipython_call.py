'''
Created on Dec 14, 2015

@author: Benjamin Jakubowski
'''
'''
This module includes two functions that check system conditions necessary to run the expenditure visualizer,
specifically:
    - Availability of data
    - Visualization modules called from ipython notebook.
'''

import os
    
def run_from_ipython(): ### Note code below from Tom Dunham, StackOverflow, 03/21/11
    '''
    Check if function called from ipython environment, not from terminal or python shell.
    '''
    try:
        __IPYTHON__
        return True
    except NameError:
        return False
    
def data_available():
    '''
    Check if the necessary data available
    '''
    for year in range(2006,2013): 
        if not os.path.exists('../data/merged_data/expenditure_demo_account_year_{}.csv'.format(str(year))):
            return False
    if not os.path.exists('../data/SCHMA/schma19962013.csv'):
        return False
    else:
        return True

def try_call_function(function):
    '''
    Calls function 'function' if data_available and run)_from_ipython. Otherwise prints informative
    message and exits.
    '''
    if run_from_ipython() and data_available():
        function()
    else:
        if not run_from_ipython():
            print 'This program must be called from within an ipython interactive notebook.'
        elif not data_available():
            print 'The necessary data is not available- please run main.py in get_and_clean data first.'
    return