'''
Created on Dec 10, 2015

@author: Benjamin Jakubowski
'''
'''
This module reads in the scraped school expenditure data.
It then cleans this data and saves each year as a cleaned csv file.
'''
import sys
if __name__ == "__main__":
    print "Not to be called directly- exiting program"
    sys.exit()
    
    
import pandas as pd

def clean_scraped_data():
    '''Cleans the data scraped from NYC schol expenditure reports and saves cleaned data.'''
    all_years_data = {}
    for year in range(2006,2013):
        all_years_data[year] = pd.read_csv('../data/raw_school_expenditures_by_year/year_{}.csv'.format(str(year)), index_col=0)
    
    ## need todrop _No_type_required, which is a duplicated feature in the 2006-2008 datasets.
    for year in [2006, 2007, 2008]:
        all_years_data[year] = all_years_data[year].drop('_No_type_required', axis=1)

    ## Next we:
    ##    - Fill in missing values with 0. This is justified under the assumption that if a row is missing from the
    ##      expenditure report, it is because the school did not have any expenditures under that category.
    ##    - Drop features with zero variance (which are non-informative)
    ##    - Convert Title_1 from a text feature to a dummy variable, with 'Yes' = 1 and 'No' = 0.
    ##    - Save to a csv file
    
    for year in all_years_data:
        all_years_data[year].fillna(0.0,inplace=True)
        mask = list((all_years_data[year].std() == 0.0).loc[(all_years_data[year].std() == 0.0)==True].index)
        all_years_data[year].drop(mask, axis=1, inplace=True)
        all_years_data[year]['Title_1'] = all_years_data[year]['Title_1'].map({'Yes':1.0, 'No':0.0})
        path = '../data/clean_expenditure_data_by_year/clean_year_{}.csv'.format(str(year))
        all_years_data[year].to_csv(path)