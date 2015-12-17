'''
Created on Dec 11, 2015

@author: Benjamin Jakubowski
'''

'''This module provides the data and methods necessary to interactively generate boxplots
showing school expenditures by category, for schools grouped by demographic attributes.'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interactive, widgets
import re
from IPython.display import display

class boxplot_comparisons(object):
    '''
    Class to encapsulate data and methods for interactive boxplots. Once boxplot_comparisons
    has been initialized, a user input menus is generated, allowing the user to select
        - An expenditure (i.e. Teachers, Principals, textbooks) to plot
        - A demographic feature to group schools by
        - A checkbox allowing the user to specify whether the expenditure should be normalized
        (so the expenditures are plotted as a percent of a school's total expenditures).
    Upon new user input through the ipywidget menu, a new array of boxplots is generated and
    output to the screen.
    
    Note this class will only behave as expected in the Jupyter iPython notebook environment
    since it uses is built on the ipywidget package.
    '''
    
    def __init__(self):
        self.all_years_data = self.read_all_years_data()
        self.expenditure_options = self.build_expenditure_dicts()
        self.groupby_options = self.build_groupby_dicts()
        w = interactive(self.make_boxplot,
                        expenditure=widgets.Dropdown(options=self.expenditure_options,value='Total',description='Expenditure category:'),
                        groupby_feature=widgets.Dropdown(options=self.groupby_options,value='Title_1',description='Group schools by feature:'),
                        normalized=widgets.Checkbox(description='Plot expenditure as percent of total:', value=False))
        w.border_color = 'red'
        w.border_style = 'dotted'
        w.border_width = 3
        display(w)
    
    def read_all_years_data(self):
        '''
        Reads in all the data for boxplot analysis.
        '''
        all_years_data={}
        for year in range(2006, 2013):
            all_years_data[year] = pd.read_csv('../data/merged_data/expenditure_demo_account_year_{}.csv'.format(year), index_col=0)
            all_years_data[year] = all_years_data[year][~all_years_data[year].duplicated()]
        return all_years_data
    
    def make_boxplot(self, expenditure, groupby_feature, normalized):
        '''
        Takes as input:
            expenditure: expenditure type (ex: Total, Teachers)
            groupby_feature: demographic or other school characteristic (ex: poverty_level)
            normalized: boolean
        Note input is not accepted directly from the user, but instead passed from the interactive iPywidget.
        
        When %matplotlib inline magic on in ipython notebook, prints a plot with 7 boxplots
        comparing the input expenditure, by groupby_feature, across all years (2006-2012).
        '''
        plt.close('all')
        ##Bin the expenditure feature, if needed
        quartiles_or_fewer_bins = self.map_onto_quartile(groupby_feature)
        
        
        ## Set data depending on normalization
        data = self.normalize_expenditures(normalized)
        
        ## find maximum value of 'expenditure' to set ylims:
        max_val = 0
        for year in range(2006,2013):
            if data[year][expenditure].max() > max_val:
                max_val = data[year][expenditure].max()
        
        ## Create dictionary for labeling
        feature_labels = self.make_labels_from_features()
        
        ## Create plots 
        fig = plt.figure(figsize=(16,16))
        for year in range(2006,2013):
            axes = {}
            axes[year] = plt.subplot(4,2, year-2005)
            data[year].boxplot(column=expenditure, by=quartiles_or_fewer_bins[year], ax=axes[year], widths=0.3)
            
            ## Add simple linear regression line
            line_of_best_fit = np.polyfit(quartiles_or_fewer_bins[year], data[year][expenditure], deg=1)
            num_vals = len(quartiles_or_fewer_bins[year].value_counts())
            xs = np.arange(0.5,num_vals+1,1)
            ys = line_of_best_fit[0]*xs + line_of_best_fit[1]
            if normalized:
                label = r'Linear regression $\beta_{slope}$' + '= ' + '%s' % float('%.2g' % line_of_best_fit[0])
            else:
                label = r'Linear regression $\beta_{slope}$' + '= ' + '%s' % float('%.2g' % line_of_best_fit[0])
            plt.plot(xs, ys, 'g--', linewidth=1, label=label)
            
            ## Get medians for each level of group, and label medians on plot
            grouped = data[year].groupby(quartiles_or_fewer_bins[year])[expenditure].median()
            i = 1.16 ## indexer for label position
            for group in grouped:
                if normalized:
                    axes[year].text(i, group, '- {}%'.format(str(round(group,2))), verticalalignment='center')
                    i+=1
                else:
                    axes[year].text(i, group, '- ${}'.format(str(int(group))), verticalalignment='center')
                    i+=1
            
            ## Add labels to x and axis, ticks, legend
            axes[year].set_title(str(year))
            axes[year].set_xlabel('')
            axes[year].set_ylim((0,max_val)) ##want comparability across years
            axes[year].set_xlim((0,len(quartiles_or_fewer_bins[year].value_counts())+1))
            axes[year].set_xticklabels(self.make_xtick_labels(groupby_feature)[year].values())
            axes[year].legend(loc='best')
            
        ## In 8th axis, add informative plot summary
        axes['key'] = plt.subplot(4,2,8)
        axes['key'].axis('off')
        axes['key'].text(0, 1,"Explanation:\n\nThese boxplots show per student expenditures\n"
                         "for the expenditure variable '{0}'\n"
                         "for each school year between 2005-2006 and 2011-2012,\n"
                         "grouped by the school characteristic '{1}'.\n".format(feature_labels[expenditure], feature_labels[groupby_feature]) +
                         "For reference, recall the middle red line is the median,\n"
                         "the boxes span the inner quartile range\n"
                         "(25th-75th percentiles), and the whiskers are \n"
                         "1.5 times the IQR. Finally, outliers are plotted as + signs.\n"
                         r"Additionally, note the regression coefficient $\beta_{slope}$" + "\n"
                         "provided in the legend is for regression on the grouped feature\n"
                         "(comparing across either binary classes or quartile groups).", fontsize=12,
                        horizontalalignment='left', verticalalignment='top')
        if normalized:
            title = "Comparing per student expenditures on {0},\n (as % of school's total budget) grouped by {1}".format(feature_labels[expenditure], feature_labels[groupby_feature])
        else:
            title = "Comparing per student expenditures on {0}\ngrouped by {1}".format(feature_labels[expenditure], feature_labels[groupby_feature])
        fig.suptitle(title, x=0.5, y= 0.95, fontsize=16)
        return
        
    def map_onto_quartile(self, expenditure):
        '''
        Accepts an expenditure feature as input. If this features value_counts is less than 4,
        maps each year's data for these features onto one of four quartiles. Returns the data,
        mapped onto quartiles, for each year as a dictionary. Else returns dictionary with
        original binary feature.
        '''
        quartiles = {}
        for year in range(2006,2013):
                if len(self.all_years_data[year][expenditure].value_counts())>4:
                    quartiles[year] = pd.qcut(self.all_years_data[year][expenditure], 4, labels=range(1,5))
                else:
                    quartiles[year] = self.all_years_data[year][expenditure]
        return quartiles
    
    def make_xtick_labels(self, groupby_feature):
        '''
        If a quartiles_or_fewer_bins is binary, returns dictionary of binary labels
        (ex: High Schools, non-High Schools). Else returns quartile labels.
        '''
        labels = {}
        for year in range(2006,2013):
                if len(self.all_years_data[year][groupby_feature].value_counts()) == 2:
                    label = self.make_labels_from_features()[groupby_feature]
                    ##Append "school" to features like Title_1, which lacks "school" string.
                    if 'School' not in label:
                        label = label + ' school'
                    labels[year] = {1:'{}s'.format(label), 0:'non-{}s'.format(label)}
                    
                else: ##Non-binary feature
                    labels[year] = {i:'Quartile {}'.format(i) for i in range(1,5)}
        return labels
    
    def normalize_expenditures(self, boolean):
        '''
        If input boolean == True, then normalizes the expenditure data (dividing each expenditure
        for a given school by that school's total expenditures. Returns this normalized data.
        If boolean == False, returns the original data.
        '''
        data = {}
        if boolean:
            for year in self.all_years_data:
                ##Drop non-expenditure and non-numeric fields, then normalize
                numeric = self.all_years_data[year].drop(['School','District','Title_1', 'Name', 'schoolyear',
                                                     'fl_percent', 'frl_percent', 'total_enrollment', 'ell_percent',
                                                     'sped_percent', 'asian_per', 'black_per', 'hispanic_per', 'white_per',
                                                     'male_per', 'female_per', 'poverty_level', 'elementary_school',
                                                     'middle_school', 'high_school'], axis=1)
                numeric = numeric.div(numeric.Total, axis='index')
    
                ##Concatenate back together
                data[year] = pd.merge(numeric, self.all_years_data[year][['School','District','Title_1', 'Name', 'schoolyear',
                                                     'fl_percent', 'frl_percent', 'total_enrollment', 'ell_percent',
                                                     'sped_percent', 'asian_per', 'black_per', 'hispanic_per', 'white_per',
                                                     'male_per', 'female_per', 'poverty_level', 'elementary_school',
                                                     'middle_school', 'high_school']], left_index=True, right_index=True)
        else:
            data = self.all_years_data
        return data
    
    def make_labels_from_features(self):
        '''
        Parses feature names to get informative, human readable descriptions. Then
        maps the original feature names onto these descriptions, and returns this
        mapping as a dictionary.
        '''
        columns = []
        for year in self.all_years_data:
            for column in self.all_years_data[year]:
                columns.append(column)
        list(set(columns))
        keys = [re.sub('_+', ' ', x) for x in columns]
        keys = [re.sub('sped', 'Special Education',  x) for x in keys]
        keys = [re.sub('ell', 'English Language Learners', x) for x in keys]
        keys = ['Percent students {}'.format(x) if (' per' in x) else x for x in keys ]
        keys = [re.sub('per$', '', x) for x in keys]
        keys = [re.sub('All Funds', '(All Funds)', x) for x in keys]
        keys = [re.sub('Srcs', 'Services', x) for x in keys]
        keys = [re.sub('LeadershipSupervisionSupport', 'Leadership, Supervision, and Support', x) for x in keys]
        keys = [x.title() for x in keys]
        map_features_to_keys = dict(zip(columns, keys))
        return map_features_to_keys
    
    def build_expenditure_dicts(self):
        return {'After School And Student Activities': 'After_School_and_Student_Activities',
 'Assistant Principals': 'Assistant_Principals',
 'Attendance Outreach Services': 'Attendance__Outreach_Services',
 'Building Maintenance': 'Building_Maintenance',
 'Classroom Instruction (All Funds)': 'Classroom_Instruction_All_Funds',
 'Contracted Instructional Services': 'Contracted_Instructional_Services',
 'Counseling Services': 'Counseling_Services',
 'Custodial Services': 'Custodial_Services',
 'Drug Prevention Programs': 'Drug_Prevention_Programs',
 'Education Paraprofessionals': 'Education_Paraprofessionals',
 'Energy': 'Energy',
 'Food Services': 'Food_Services',
 'Instructional Supplies And Equipment': 'Instructional_Supplies_and_Equipment',
 'Leadership, Supervision, And Support (All Funds)': 'LeadershipSupervisionSupport_All_Funds',
 'Librarians And Library Books': 'Librarians_and_Library_Books',
 'Other Classroom Staff': 'Other_Classroom_Staff',
 'Parent Involvement Activities': 'Parent_Involvement_Activities',
 'Principals': 'Principals',
 'Professional Development': 'Professional_Development',
 'Referral And Evaluation Services (All Funds)': 'Referral_and_Evaluation_Services_All_Funds',
 'Sabbaticals, Leaves, and Termination Pay': 'Sabbaticals_Leaves_Termination_Pay',
 'School Safety': 'School_Safety',
 'Secretaries, School Aides, and Other Support Staff': 'Secretaries_School_Aides__Other_Support_Staff',
 'Summer And Evening School': 'Summer_and_Evening_School',
 'Supervisors': 'Supervisors',
 'Leadership Supplies, Materials, Equipment, and Telephones': 'Supplies_Materials_Equipment_Telephones',
 'Teachers': 'Teachers',
 'Text Books': 'Text_Books',
 'Total': 'Total',
 'Transportation': 'Transportation'}
    
    def build_groupby_dicts(self):
        return {'Elementary School': 'elementary_school',
 'High School': 'high_school',
 'Middle School': 'middle_school',
 'Percent Students Asian ': 'asian_per',
 'Percent Students Black ': 'black_per',
 'Percent Students English Language Learners': 'ell_percent',
 'Percent Students Female ': 'female_per',
 'Percent Students Hispanic ': 'hispanic_per',
 'Percent Students Male ': 'male_per',
 'Percent Students Special Education': 'sped_percent',
 'Percent Students White ': 'white_per',
 'Poverty Level': 'poverty_level',
 'Title 1': 'Title_1',
 'Total Enrollment': 'total_enrollment'}
        

from check_data_and_ipython_call import try_call_function

try_call_function(boxplot_comparisons)
        