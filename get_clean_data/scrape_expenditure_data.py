'''
Created on Dec 10, 2015

@author: Benjamin Jakubowski
'''

'''
This module scrapes online NYC school expenditure reports.

For each year from 2006-2012 (and earlier years, though earlier years
were not included due to availability of demographic and enrollment data),
NYC Department of Education has published expenditure reports for each school.
These reports are available online. The data is stored in an HTML table, withSpecifically, we're using the schools listed in the 2006-2012 Demographic and Accountability snapshot available on NYC Open Data.
each school's report on a unique webpage.

This module:
    - Reads in the list of DBN (school codes) available in the NYC
    School Demographic Accountability 2006-2012 snapshot (from NYC open data)
    - Scrapes per-pupil expenditure data for each of these schools for each year
    - Saves the data for each year as a csv file for future use.
'''
import sys
if __name__ == "__main__":
    print "Not to be called directly- exiting program"
    sys.exit()
    
from urllib2 import urlopen, HTTPError, URLError
from lxml.html import parse
import re
import pandas as pd
from retrying import retry

def hexencode(matchobj):
    '''
    Helper function hexencode converts special characters in school name
    to a hexcode, which is how they are represented in the school expenditure report URL'''
    
    encoded = '%' + matchobj.group(0).encode('hex')
    return encoded

def retry_if_URL_error_not_HTTP_error(exception):
    '''Return True if we should retry (in this case when a URLError has been raised (i.e. network connection
    problem) and not an HTTPError (i.e. page doesn't exist)'''
    return (isinstance(exception, URLError) and not isinstance(exception, HTTPError))
            
##Retry decorator will retry every two seconds, for up to 10 seconds, if URLError    
@retry(retry_on_exception=retry_if_URL_error_not_HTTP_error, wait_fixed=2000, stop_max_delay=10000)
def get_school_name_from_year_and_DBN(year, DBN):
    '''
    Takes an input year and school code (DBN). Builds a URL to search the given year's expenditure
    reports for that DBN. If a result (i.e. school name) is found, returns the URL to get that school's
    expenditure report'''
    
    #build initial query:
    
    years = str(year-1) + '_' + str(year)
    query1 = ("https://www.nycenet.edu/offices/d_chanc_oper/budget/exp01/y" + years +
             "/function.asp?district=All&search=" + DBN +
             "&searchgo=Search&LCMS=**&GRANT=NO&cr1=All&cr2=All&cr3=All&cr4=All&R=1&prior=search")
    
    
    ##get school name by searching html page returned from query- if not found, return None.
    try:
        parsed1 = parse(urlopen(query1))
        doc=parsed1.getroot()
        options = doc.findall('.//option')
        for option in options:
            ##Schools in districts 1-32
            if re.match('District', option.text_content()):
                school_name = option.text_content()
                school_name = re.sub('--','',school_name)
                school_name = re.sub('District:\s','', school_name)
                school_name = re.sub('\s','+', school_name)
                school_name = re.sub('[^A-Za-z0-9\s+.]', hexencode, school_name)
                school_name = str(DBN) + school_name
                return school_name
            
            ##Schools in district 75- citywide special education district
            elif re.match('Citywide', option.text_content()):
                school_name = option.text_content()
                school_name = re.split('--',school_name)[1]
                school_name = re.sub('\s','+',school_name)
                school_name = re.sub('\.\+?','+',school_name)
                ##Note even though it's district 75, it's coded as 97 in the url
                school_name = str(DBN) + str(97) + str(school_name)
                school_name = re.sub('[^A-Za-z0-9\s+.]', hexencode, school_name)
                return school_name 
            
            ##Schools in district 79- alternative HS's
            elif re.match('Alternative HS', option.text_content()):
                school_name = option.text_content()
                school_name = re.split('--',school_name)[1]
                school_name = re.sub('\s+','+',school_name)
                school_name = str(DBN) + str(79) + str(school_name)
                school_name = re.sub('[^A-Za-z0-9\s+.]', hexencode, school_name)
                return school_name
            
        ##If not found, return None- school expenditure report not available.
        return None
            
    except HTTPError:
        return None
    
    except URLError:
        return None
    
@retry(retry_on_exception=retry_if_URL_error_not_HTTP_error, wait_fixed=2000, stop_max_delay=10000)
def get_all_school_data(year,DBN):
    '''
    Takes a year and DBN as input. Searches expenditure reports for that DBN to get
    the school name (URL for school expenditure report). If a school name found, then
    reads in the school's expenditure report page, parses it, and returns a dataframe with
    per student expenditures for that year.
    '''
    
    ##Build URL to get school expenditure data
    school_name = get_school_name_from_year_and_DBN(year, DBN)
    if school_name is None:
        return None

    ##if found, use school name to build new query to get expenditure report for year:
    years = str(year-1) + '_' + str(year)
    query2 = ("https://www.nycenet.edu/offices/d_chanc_oper/budget/exp01/y" + years +
             "/function.asp?district=All&search=" + DBN + "&LCMS=" + school_name +
             "&schoolgo=Go&GRANT=NO&cr1=All&cr2=All&cr3=All&cr4=All&R=1&prior=search")
    
    try: ##Try opening the URL page and parsing it.
        parsed = parse(urlopen(query2))
        doc = parsed.getroot()
        tables = doc.findall('.//table')
        
        ##Table 5 data includes the school name, district, and it's Title 1 status
        rows = tables[4].findall('.//tr')
        elts = rows[2].findall('.//td')
        
        ## This will work for Districts 1-32, but not 75 or 79, which are formatted differently
        if int(school_name[4:6]) in range(1,33): 
            for val in elts[0]:
                table_5_dat = val.text_content()
                table_5_dat = re.split('[\xa0]+[\s]?',table_5_dat)
                school_features = {}
                for i in table_5_dat:
                    school_features[str(re.sub('\s','_', re.split(':\s',i)[0]))]=str(re.split(':[\s]+',i)[1])
        
        ## Handles districts 75 and 79
        else:
            for val in elts[0]:
                table_5_dat = val.text_content()
                table_5_dat = re.split('[\s]?[\xa0]+[\s]?',table_5_dat)
                school_features = {}
                school_features['District'] = str(re.sub('\s', '_', table_5_dat[0]))
                for i in table_5_dat[1:]:
                    school_features[str(re.sub('\s','_', re.split(':\s',i)[0]))]=str(re.split(':[\s]+',i)[1])
        
        ## Now we need to convert the text district names to numeric district codes:
        if school_features['District'] == 'Citywide_Sp_Ed_(75)':
            school_features['District'] = 75
        elif  school_features['District'] == 'Alternative_HS':
            school_features['District'] = 79
        
        ##Make expenditure dict:
        expenditures = {}
        
        ##Table 7 includes part of the per student expenditures
        rows = tables[6].findall('.//tr')
        for row in rows:
            elts = row.findall('.//td')
            for pair in zip(elts[0],elts[3]):
                key = re.sub('[\xa0]+','_', pair[0].text_content())
                key = re.sub('.*?\._','',key)
                key = re.sub('[^A-Za-z_]','',key)
                expenditures[key] = re.sub('[^0-9]','', pair[1].text_content())
                 
        ##Table 10 includes the rest of the per student expenditures.
        rows = tables[9].findall('.//tr')
        for row in rows:
            elts = row.findall('.//td')
            for pair in zip(elts[0],elts[3]):
                key = re.sub('[\xa0]+','_', pair[0].text_content())
                key = re.sub('.*?\._','',key)
                key = re.sub('[^A-Za-z_]','',key)
                expenditures[key] = re.sub('[^0-9]','', pair[1].text_content())
                                           
    ## Note- @retry wrapper will retry if URLerror but not HTTPError (so if network connectivity issue we'll retry)
    ## If HTTPError, we want to just return- the page doesn't exisT
    
    except HTTPError:
        return
    
    ## If data not available it will throw an IndexError (list out of bounds).
    ## This reflects missing data (i.e. missing tables, or rows, or cells) so we return 'none'.
    
    except IndexError:
        return
    
    ##clean up expenditures- read in one null value that should be deleted due to table structure
    
    del expenditures['_']
    
    ##join two dictionaries and return as series
    school_features.update(expenditures)
    school_features = pd.Series(school_features.values(), index=school_features.keys(), name=DBN)
    return school_features

def get_DBN_list():
    '''
    Helper function that gets the list of DBN's available from NYC open data- these are the DBNs
    we'll use to query the expenditure report tool.
    '''
    
    query = 'https://nycopendata.socrata.com/api/views/ihfw-zy9j/rows.csv?accessType=DOWNLOAD'
    Demo_and_Account = pd.read_csv(query)
    all_DBNs = Demo_and_Account['DBN']
    unique_DBNs = all_DBNs.unique()
    for i in range(len(unique_DBNs)):
        unique_DBNs[i] = unique_DBNs[i][2:]
    return unique_DBNs

def build_expenditure_dataframe(year):
    '''
    Get's school expenditure data for all available DBN's for the input year. Returns
    all school data as a dataframe.
    '''
    
    unique_DBNs = get_DBN_list()
    results_for_year = get_all_school_data(year, unique_DBNs[0])
    for DBN in unique_DBNs[1:]:
        school_results = get_all_school_data(year, DBN)
        results_for_year = pd.concat([results_for_year, school_results], axis=1)
    results_for_year = results_for_year.T
    return results_for_year

def save_2006_to_2012_data():
    '''
    Scrapes data for all years, 2006-2012. Saves expenditure data for all
    available schools for these years in csv files.
    '''
    
    print 'Starting to get data'
    for year in range(2006,2013):
        print 'Starting to get data for', year
        save_path = "../data/raw_school_expenditures_by_year/year_" + str(year) + ".csv"
        year_expenditure_data = build_expenditure_dataframe(year)
        print 'Got data for year', year
        year_expenditure_data.to_csv(save_path)
        print 'Saved data for year', year
    print 'Done'