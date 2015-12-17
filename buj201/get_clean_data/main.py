'''
Created on Dec 11, 2015

@author: Benjamin Jakubowski
'''
'''
The main module for get_clean_data. It:
- Checks that the SCHMA data is available locally
- Creates directories as necessary
- Reads in, cleans, and saves:
    - SCHMA data
    - Demographic accountability snapshot data
    - Expenditure data
Note this program will take several hours to run, as it is scraping data from approximately 20K HTML
pages. 
'''

if __name__ == '__main__':
    pass

import sys
from clean_SCHMA_data import clean_SCHMA
from scrape_expenditure_data import save_2006_to_2012_data
from clean_scraped_data import clean_scraped_data
from get_and_clean_school_demo_and_account import get_and_clean_demo_and_account
from merge_expenditure_and_demo_account_data import merge_demo_account_and_expenditure
from check_filesystem import check_filesystem


try:
    check_filesystem()
except IOError as msg:
    print msg
    sys.exit()
    
def main():
    print 'Getting and cleaning expenditure data'
    save_2006_to_2012_data()
    clean_scraped_data()
    print 'Cleaning SCHMA data'
    clean_SCHMA()
    print 'Getting and cleaning demographic and accountability snapshot data'
    get_and_clean_demo_and_account()
    print 'Merging demographic/accountabilty and expenditure data'
    merge_demo_account_and_expenditure()
    return

try:
    main()
except KeyboardInterrupt:
    print 'Program terminated by keyboard interrupt- restart main.py to get data.'