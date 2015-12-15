'''
Created on Dec 11, 2015

@author: Benjamin Jakubowski
'''
'''
This module checks that the SCHMA data is available, and that it is stored in a data sub-directory
of the parent directory. It then checks that other necessary directories exist, and if not,
it creates them (so they're available for getting/cleaning/saving data)
'''

import sys
if __name__ == "__main__":
    print "Not to be called directly- exiting program"
    sys.exit()
    
import os

def check_filesystem():
    if os.path.exists('../data/SCHMA/schma19962013.csv'):
        if not os.path.isdir('../data/raw_school_expenditures_by_year'):
            os.mkdir('../data/raw_school_expenditures_by_year')
        if not os.path.isdir('../data/clean_expenditure_data_by_year'):
            os.mkdir('../data/clean_expenditure_data_by_year')
        if not os.path.isdir('../data/merged_data'):
            os.mkdir('../data/merged_data')
    else:
        error_msg =  '''At a minimum, to use this program you must have the 1996-2013 SCHMA data
at the filepath ../data/SCHMA/schma19962013.csv. This dataset is produced by the
the Research Alliance for New York City Schools at New York University, and to 
request it you should visit http://steinhardt.nyu.edu/research_alliance/research/schma
        '''
        raise IOError(error_msg)
    return