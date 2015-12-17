'''
Created on Dec 10, 2015

@author: benjaminjakubowski
'''
import unittest
import pandas as pd
from check_data_and_ipython_call import *
from school_dashboard import school_dashboard

class Test(unittest.TestCase):

    def test_ipython_call_check(self):
         ## try_call_function will return false when unittest called
        self.assertTrue(not try_call_function(lambda x: 'arbitrary test function'))
        
    def test_data_check(self):
        ## Note we want to be sure data is available- if this test fails print msg.
        self.assertTrue(data_available(),'Data not available- re-run main.py in get_clean_data.')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()