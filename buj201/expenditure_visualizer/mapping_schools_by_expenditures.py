'''
Created on Dec 11, 2015

@author: Benjamin Jakubowski
'''

'''This module provides the merged data and methods necessary to interactively map school by year,
colored by their percentile score for a user-input expenditure category.'''

import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from ipywidgets import interactive
from IPython.display import display

class NYC_school_interactive_map(object):
    '''
    Class to encapsulate data and methods for interactive NYC map, which maps
    NYC schools as colored points. The interactivity allows the user to select:
        - Which year (2010, 2011, or 2012) to plot
        - Which expenditure category to color the schools by (with school's colored
        based on their percentile score for the selected category).
    Instantiating the class produces an ipywidget box (with two drop down menus to accept
    user input), and an initial school map.
    
    Note this class will only behave as expected in the Jupyter iPython notebook environment
    since it uses is built on the ipywidget package.
    '''
   
    def __init__(self, feature = 'Total', year = 2012):
        self.feature = feature
        self.year = year
        self.all_years_data = self.read_and_merge_data()
        self.basemap, self.ax, self.fig = self.make_NYC_basemap()
        self.color_bar = self.create_color_bar(feature = 'Total', year = 2012)
        self.features_for_widget = self.features_for_interaction()
        w = interactive(self.interactive_update, Expenditure = self.features_for_widget, Year={'2010':2010, '2011':2011, '2012':2012})
        w.border_color = 'red'
        w.border_style = 'dotted'
        w.border_width = 3
        display(w)
        
    def read_and_merge_data(self):
        '''
        Reads in the merged data set containing expenditure and demographic features for each school,
        for each year 2010-2012.
        '''
        #Read in expenditure/demographic data
        all_years_data = {}
        for year in range(2010,2013):
            all_years_data[year] = pd.read_csv('../data/merged_data/expenditure_demo_account_year_{}.csv'.format(str(year)), index_col=0)
    
        SCHMA = pd.read_csv('../data/clean_SCHMA.csv', index_col=0).reset_index(drop=True)
    
        for year in all_years_data:
            ##Drop non-expenditure and non-numeric fields, then normalize
            numeric = all_years_data[year].drop(['School','District','Title_1', 'Name', 'schoolyear',
                                                 'fl_percent', 'frl_percent', 'total_enrollment', 'ell_percent',
                                                 'sped_percent', 'asian_per', 'black_per', 'hispanic_per', 'white_per',
                                                 'male_per', 'female_per', 'poverty_level', 'elementary_school',
                                                 'middle_school', 'high_school'], axis=1)
            numeric = numeric.div(numeric.Total, axis='index')
            
            ##Concatenate the normed numeric features and the non-numeric/non-expenditure features
            all_years_data[year] = all_years_data[year].join(numeric, how='inner',  rsuffix='_percent_of_total')
            
            #Finally merge in SCHMA lat/long coordinates
            all_years_data[year] = pd.merge(all_years_data[year], SCHMA[SCHMA['YEAR'] == year], how='inner', left_index=True, right_on='BNLONG')
            all_years_data[year].set_index(all_years_data[year].BNLONG, inplace=True)
            all_years_data[year].drop(['YEAR','BNLONG'], axis=1, inplace=True)
        
        return all_years_data

    def make_NYC_basemap(self, ax=None, lllat=40.45, urlat=40.95, lllon=-74.3, urlon=-73.68):
        '''
        This function creates the initial NYC basemap. It is only called once (in the initialization
        of an NYC_school_interactive_map instance), since it has a relatively long run-time (it queries
        the ESRI REST server to get a relatively high-resolution basemap image).
        ''' 
            
        fig = plt.figure(figsize=(12,12))
        ax = plt.subplot(111)
            
        m = Basemap(ax = ax, 
                       lon_0=(urlon + lllon)/2,
                       lat_0=(urlat + lllat)/2,
                       llcrnrlat=lllat, urcrnrlat=urlat,
                       llcrnrlon=lllon, urcrnrlon=urlon,
                       resolution='f', epsg=3857) ###epsg is the projection code for ESRI world shaded relief basemap
    
        #m.arcgisimage queries the ESRI REST API (server below) to get the basemap 
        #http://server.arcgisonline.com/arcgis/rest/services
        m.arcgisimage(service='World_Shaded_Relief', xpixels = 1500)
    
        # Add county lines, since boroughs map onto counties
        m.drawcounties(linewidth=0.5)
        
        return m, ax, fig
        
    def create_color_bar(self, feature, year):
        '''
        This function creates the colorbar. This function is only called once, then the colorbar is stored as an
        object attribute, since it is used across all the NYC maps produced using the interactive widget.'''
        
        self.fig
        ax = self.ax
        m = self.basemap
        data = self.all_years_data[year]
        ##add points and color bar for the default feature- note the same colormap is used for 
        ##all plots produced by interactive_update, so the specific feature used is irrelevant.
        percentiles = [stats.percentileofscore(data[feature],x,kind='weak')/100.0 for x in data[feature]]
        schools = m.scatter(data['LCGGEOX'].values, data['LCGGEOY'].values, latlon=True, s=30, c=percentiles, alpha=0.8, cmap='cool')
        ax.set_title('NYC Schools, colored by ranked on\n{} expenditures for year = {}'.format(self.features_for_labels(feature), str(year)))
        cbar = m.colorbar(schools,location='bottom',pad="5%")
        label = 'Rank (percentile score) of each school for selected expenditure category'
        cbar.set_label(label)
        return cbar
        
    def interactive_update(self, Expenditure, Year):
        '''
        interactive_update takes an Expenditure type and a Year as input- the allowed Expenditures are the values in self.features_for_widget,
        and the allowed years are 2010, 2011, and 2012.
        Note this function receives input from the widget, and as such no input validation is needed.
        '''
        
        plt.close('all')
        fig = self.fig
        ax = self.ax
        m = self.basemap
        self.color_bar
        
        data = self.all_years_data[Year]
        ##add points title
        percentiles = [stats.percentileofscore(data[Expenditure],x,kind='weak')/100.0 for x in data[Expenditure]]
        m.scatter(data['LCGGEOX'].values, data['LCGGEOY'].values, latlon=True, s=30, c=percentiles, alpha=0.8, cmap='cool')
        ax.set_title('NYC Schools, colored by ranked on\n{} expenditures for year = {}'.format(self.features_for_labels(Expenditure), str(Year)))
        return fig
    
    def features_for_interaction(self):
        '''
        This method can be called to get the dictionary mapping .
        '''
        features = {'Ancillary Support Services- Percent of Total': 'Ancillary_Support_Services_All_Funds_percent_of_total',
 'Building Services- Percent of Total': 'Building_Services_All_Funds_percent_of_total',
 'Central Administration- Percent of Total': 'Central_Administration_All_Funds_percent_of_total',
 'Central Instructional Support- Percent of Total': 'Central_Instructional_Support_All_Funds_percent_of_total',
 'Classroom Instruction- Percent of Total': 'Classroom_Instruction_All_Funds_percent_of_total',
 'Field Support- Percent of Total': 'Field_Support_All_Funds_percent_of_total',
 'Instructional Support And Administration- Percent of Total': 'Instructional_Support_and_Administration_All_Funds_percent_of_total',
 'Instructional Support Services- Percent of Total': 'Instructional_Support_Srcs_All_Funds_percent_of_total',
 'Leadership, Supervision, and Support- Percent of Total': 'LeadershipSupervisionSupport_All_Funds_percent_of_total',
 'Other Field Support Costs- Percent of Total': 'Other_Field_Support_Costs_All_Funds_percent_of_total',
 'Referral And Evaluation Services- Percent of Total': 'Referral_and_Evaluation_Services_All_Funds_percent_of_total',
 'Total': 'Total'}
        return features
    
    def features_for_labels(self, feature):
        '''
        This function inverts the self.features_for_widgets dictionary (mapping values back to keys), so the dictionary
        is in the format expected by the interactive widget.
        ''' 
        features=self.features_for_interaction()
        features = {v: k for k, v in features.items()}
        return features[feature]


from check_data_and_ipython_call import try_call_function

try_call_function(NYC_school_interactive_map)
