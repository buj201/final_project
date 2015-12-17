'''
Created on Dec 10, 2015

@author: Benjamin Jakubowski
'''
'''
In this module, we will clean data from the School-Level Master File. This dataset is produced by
the Research Alliance for New York City Schools at NYU. They describe it as follows:
    The School-Level Master File (SCHMA) is a dataset developed by the Research Alliance for New
    York City Schools at New York University. To create the file, we compiled publicly available
    data from the New York City Department of Education (DOE) and the U.S. Department of Education.
    The result is a consistent, accessible document that can be used to investigate characteristics
    of individual New York City schools or groups of schools and how they have changed over time.
We will use the SCHMA to obtain each school's latitude and longitude (so we can create spatial plots).
'''
import sys
if __name__ == "__main__":
    print "Not to be called directly- exiting program"
    sys.exit()
    
    
import pandas as pd

def clean_SCHMA():
    '''
    Read and clean the SCHMA data. Save cleaned SCHMA data to csv file. Note that
    in an exploratory ipython notebook, the max and min of the latitude and longitudes
    was shown to be in the permissible range (such that these feaures don't need additional
    cleaning.
    '''
    
    raw_SCHMA = pd.read_csv('../data/SCHMA/schma19962013.csv', usecols=['YEAR', 'BNLONG','LCGGEOX','LCGGEOY'], low_memory=False)
    
    ## Drop all records with YEAR not between 2006 and 2012.
    proc_SCHMA = raw_SCHMA.loc[(2006 <= raw_SCHMA.YEAR)]
    proc_SCHMA = proc_SCHMA.loc[(raw_SCHMA.YEAR <= 2012)]
    
    ## Drop missing values- need BNLONG and Year to merge, and lat/long to plot. Imputation also
    ## not permissible, since schools can move between buildings while retaining code.
    proc_SCHMA.dropna(inplace=True)
    
    ##Save to csv file
    proc_SCHMA.to_csv('../data/clean_SCHMA.csv')