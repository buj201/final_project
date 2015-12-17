'''
Created on Dec 10, 2015

@author: Benjamin Jakubowski
'''

'''
This module gets and clean the school demographics and accountability snapshot, 2006-2012.
First, we read in the data from NYC Open Data. Then we:
    - Clean the data.
    - Impute school types (elementary, middle school, and/or high school)
    - Plot the distributions of several features in the snapshot.
'''
import sys
if __name__ == "__main__":
    print "Not to be called directly- exiting program"
    sys.exit()
    
    
import numpy as np
import pandas as pd
from scipy import stats
import re

def get_and_clean_demo_and_account():
    query = 'https://data.cityofnewyork.us/api/views/ihfw-zy9j/rows.csv?accessType=DOWNLOAD'
    demo_and_account = pd.read_csv(query)
    
    ## Clean all the numeric features in demo_and_account dataframe using find_bad_vals helper function.
    for feature in demo_and_account.drop(['Name','DBN','schoolyear'],axis=1).columns:
        demo_and_account.loc[(demo_and_account[feature].isin(find_bad_vals(feature, demo_and_account).keys())),feature] = np.NaN
        demo_and_account[feature] =  demo_and_account[feature].astype(float)
    
    ## Drop the first two characters (district code) from the DBN
    ## (so DBN can be used as a merge key with our other datasets),
    ## and drop all but the last four characters from school year
    ## (so it can also be used as a merge key).
    
    demo_and_account.loc[:,'DBN'] = demo_and_account['DBN'].map(lambda x: str(x)[2:])
    demo_and_account.loc[:,'schoolyear'] = demo_and_account['schoolyear'].map(lambda x: str(x)[-4:])
    
    ## Drop the '_num' features, which are redundant (given the '_per' features).
    demo_and_account.drop(['ell_num','sped_num','ctt_num','selfcontained_num','asian_num','black_num','hispanic_num','white_num','male_num','female_num'], axis=1, inplace=True)
    
    ## Fill the missing grade-level enrollment values:
    for feature in ['prek','k','grade1','grade2','grade3','grade4','grade5','grade6','grade7','grade8','grade9','grade10','grade11','grade12']:
        demo_and_account[feature].fillna(0,inplace=True)
        
    ## Use mean imputation to fill missing ell_percent values:
    demo_and_account = fill_missed_ell(demo_and_account)
    
    ## construct povert rank measure:
    demo_and_account = construct_poverty_rank_measure(demo_and_account)
    
    ## impute school type
    demo_and_account = impute_school_type(demo_and_account)
    
    ##Finally write to a csv file:
    demo_and_account.to_csv('../data/clean_demo_account.csv')

    
def find_bad_vals(feature, dataframe):
    '''
    A helper function that takes an input feature and returns dictionary
    with keys = non-numeric entries in demo_and_account[feature],
    vals = number of occurences of these bad values in the dataframe.
    '''
    bad_vals = {}
    for val in dataframe[feature].astype(str):
        finder = re.match('[0-9]+\.?[0-9]*', val)
        if finder == None:
            if val in bad_vals:
                bad_vals[val] += 1
            else:
                bad_vals[val] = 1
    return bad_vals


def fill_missed_ell(dataframe):
    '''
    Use mean imputation to fill the missing ell_percent values
    '''
    missing_ell = dataframe[dataframe.ell_percent.isnull()].groupby('DBN')
    avg_ell = {}
    for group in missing_ell.groups:
        avg_ell[group] = dataframe[(dataframe.DBN == group)]['ell_percent'].mean()
    dataframe.loc[dataframe['ell_percent'].isnull(),'ell_percent'] = dataframe.loc[dataframe['ell_percent'].isnull(), 'DBN'].map(lambda x: avg_ell[x])
    ## Drop school's with no mean available (only 3 cases- see exploratory ipynb)
    dataframe = dataframe.loc[dataframe['ell_percent'].notnull(),:]
    return dataframe


def construct_poverty_rank_measure(dataframe):
    '''
    fl_percent is only available for academic years (AYs) between
    2005-2006 and 2008-2009, while frl_percent is available for
    academic years between 2009-2010 and 2011-2012. This function constructs
    a measure of poverty that is comparable across years:
    poverty_level- that ranks a school's poverty level as a percentile
    using the available metric for each year.
    '''
    grouped = dataframe.groupby('schoolyear')
    
    for year in range(2006,2010):
        data = dataframe.loc[grouped.groups[str(year)],'fl_percent']
        dataframe.loc[grouped.groups[str(year)],'poverty_level'] = [stats.percentileofscore(data, a, 'weak') for a in data]
        
    for year in range(2010,2013):
        data = dataframe.loc[grouped.groups[str(year)],'frl_percent']
        dataframe.loc[grouped.groups[str(year)],'poverty_level'] = [stats.percentileofscore(data, a, 'weak') for a in data]
    return dataframe
    
def impute_school_type(dataframe):
    '''
    Impute whether a school is an elementary, middle, and/or high school.
    Heuristically define cutoffs as:
        - Elementary if >30% of students are in grades pre-k through 5
        - Middle if >15% of students are in grades 6-8
        - High if >30% of students in grades 9-12.
    Note this does not partition schools, but it is reasonable in that
    no school is considered an elementary and high, but not middle.
    After imputation, drop grade level enrollment totals.
    '''

    dataframe['elementary_school'] = ((dataframe['prek']+dataframe['k']+dataframe['grade1']+dataframe['grade2']+dataframe['grade3']+dataframe['grade4']+dataframe['grade5'])/dataframe['total_enrollment']).map(lambda x: 0 if x<0.3 else 1)
    dataframe['middle_school'] = ((dataframe['grade6']+dataframe['grade7']+dataframe['grade8'])/dataframe['total_enrollment']).map(lambda x: 0 if x<0.15 else 1)
    dataframe['high_school'] = ((dataframe['grade9']+dataframe['grade10']+dataframe['grade11']+dataframe['grade12'])/dataframe['total_enrollment']).map(lambda x: 0 if x<0.3 else 1)
    dataframe.drop(['prek', 'k', 'grade1', 'grade2', 'grade3', 'grade4', 'grade5', 'grade6', 'grade7', 'grade8', 'grade9', 'grade10', 'grade11', 'grade12'], axis=1, inplace=True)
    return dataframe