'''
Created on Dec 10, 2015

@author: Benjamin Jakubowski
'''
'''
This module merges the cleaned demographic and accountability data with the cleaned school expenditure data.
The final merged dataset is saved as a csv file.
'''
import sys
if __name__ == "__main__":
    print "Not to be called directly- exiting program"
    sys.exit()
    
import pandas as pd

def merge_demo_account_and_expenditure():
    demo_and_account = pd.read_csv('../data/clean_demo_account.csv', index_col=0)
    all_years_data = {}
    for year in range(2006,2013):
    ## read in raw expenditure data
        all_years_data[year] = pd.read_csv('../data/clean_expenditure_data_by_year/clean_year_{}.csv'.format(str(year)), index_col=0)
    ## merge dataframes and save data
        all_years_data[year] = pd.merge(all_years_data[year], demo_and_account[demo_and_account['schoolyear']==year], how='inner', left_on='School', right_on='DBN')
        all_years_data[year].set_index('DBN',inplace=True)
        path = '../data/merged_data/expenditure_demo_account_year_{}.csv'.format(str(year))
        all_years_data[year].to_csv(path)