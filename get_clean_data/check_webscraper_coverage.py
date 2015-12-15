'''
Created on Dec 10, 2015

@author: Benjamin Jakubowski
'''
'''
This module checks the coverage of the webscraper. Specifically, it
defines a function that determines if the missed DBNs (i.e. schools
present in the Demographic and Accountability snapshot but not
in the expenditure dataset) were missed due to poor coverage by
they webscraper, or due to non-availability of data for those schools.
'''
import sys
if __name__ == "__main__":
    print "Not to be called directly- exiting program"
    sys.exit()

from urllib2 import urlopen, HTTPError, URLError
from lxml.html import parse
import pandas as pd
from retrying import retry

def get_all_DBNs():
    query = 'https://nycopendata.socrata.com/api/views/ihfw-zy9j/rows.csv?accessType=DOWNLOAD'
    Demo_and_Account = pd.read_csv(query)
    all_DBNs = Demo_and_Account[['DBN','schoolyear']]
    return all_DBNs

def check_webscraper_coverage():
    ## read in raw scraped data
    all_years_data = {}
    for year in range(2006,2013):
        all_years_data[year] = pd.read_csv('../data/raw_school_expenditures_by_year/year_{}.csv'.format(str(year)), index_col=0)
    
    ## get and process DBN's
    all_DBNs = get_all_DBNs()
    all_DBNs['schoolyear'] = all_DBNs['schoolyear'].map(lambda x: str(x)[4:])
    all_DBNs['DBN'] = all_DBNs['DBN'].map(lambda x: str(x)[2:])
    grouped = all_DBNs.groupby('schoolyear')
    
    ## determine which schools were 'missed' by the webscraper
    missed_schools = {}
    for year in range(2006,2013):
        DBN_targets = all_DBNs.loc[grouped.groups[str(year)],'DBN']
        missing = list(set(DBN_targets) - set(all_years_data[year].index))
        missed_schools[year] = missing
    
    ## count the number of these schools are found when searching expenditure
    ## report search form by DBN
    results = {}
    print 'Searching for all missed schools by year:'
    for year in missed_schools:
        results[year] = 0
        print '\n'
        print 'Year = ', year
        for school in missed_schools[year]:
            results[year] += how_many_schools_missed(year, school)
            
    return results
        

def retry_if_URL_error_not_HTTP_error(exception):
    '''Return True if we should retry (in this case when it's a URLError (i.e. network is down) and not an
    HTTPError (i.e. page doesn't exist)'''
    return (isinstance(exception, URLError) and not isinstance(exception, HTTPError))
            
##Retry decorator will retry every two seconds, for up to 10 seconds, if server side error
 
@retry(retry_on_exception=retry_if_URL_error_not_HTTP_error, wait_fixed=2000, stop_max_delay=10000)
def how_many_schools_missed(year, DBN):
    ##counter for missed schools:
    missed_school_counts = 0
    
    ##build initial query using year and DBN
    years = str(year-1) + '_' + str(year)
    query1 = ("https://www.nycenet.edu/offices/d_chanc_oper/budget/exp01/y" + years +
             "/function.asp?district=All&search=" + DBN +
             "&searchgo=Search&LCMS=**&GRANT=NO&cr1=All&cr2=All&cr3=All&cr4=All&R=1&prior=search")
    
    ##get school name by searching html page returned from query- if not found, return None.
    try:
        parsed1 = parse(urlopen(query1))
        doc=parsed1.getroot()
        options = doc.findall('.//option')
        
        print_next=False
        for option in options:
            if 'No Schools Found' in option.text_content():
                print option.text_content()
                return 0
                
            elif 'School List' in option.text_content():
                print_next=True ##Then the next option includes the school name
                missed_school_counts +=1
                continue
                
            if print_next==True: ##So print it
                print option.text_content()
                print_next=False
                
        return missed_school_counts
    
    except HTTPError as e:
        print e
        return None
    
    except URLError as y:
        print y
        return None
    
    except URLError as y:
        print y
        return None