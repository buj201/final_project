'''
Created on Dec 10, 2015

@author: benjaminjakubowski
'''
import unittest
import pandas as pd
from check_webscraper_coverage import check_webscraper_coverage, retry_if_URL_error_not_HTTP_error
from urllib2 import HTTPError, URLError

class Test(unittest.TestCase):

    def test_clean_demo_and_account_not_NaN(self):
        demo_and_account = pd.read_csv('../data/clean_demo_account.csv', index_col=0)
        ## Drop two columns systematically missing data across years:
        demo_and_account = demo_and_account.drop(['fl_percent', 'frl_percent'], axis=1)
        self.assertEqual(demo_and_account.isnull().any(axis=1).sum(), 0)
       
    def test_clean_expenditure_data_not_NaN(self):
        all_years_data = {}
        for year in range(2006,2013):
            all_years_data[year] = pd.read_csv('../data/clean_expenditure_data_by_year/clean_year_{}.csv'.format(str(year)), index_col=0)
        ## Drop two columns systematically missing data across years:
            self.assertEqual(all_years_data[year].isnull().any(axis=1).sum(), 0) 
    
    def test_webscraper_coverage(self):
        missed_schools_by_year = check_webscraper_coverage()
        none_missed = dict(zip(range(2006,2013),[0,0,0,0,0,0,0]))
        self.assertDictEqual(missed_schools_by_year, none_missed)
        
    def test_shape_clean_SCHMA(self):
        SCHMA = pd.read_csv('../data/clean_SCHMA.csv', index_col=0)
        self.assertEqual(SCHMA.shape[1], 4)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()