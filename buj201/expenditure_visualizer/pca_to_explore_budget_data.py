'''
Created on Dec 11, 2015

@author: Benjamin Jakubowski
'''
'''
This module provides methods for PCA analysis of school budget data.
'''
import pandas as pd
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from scipy import stats
import re
from ipywidgets import interactive, widgets
from IPython.display import display

class pca_explorer(object):
    '''
    Class to encapsulate data and methods for interactive school expenditure visualization.
    The class uses principal components analysis to aid visualization of the school
    expenditure data. School expenditures are reported for approximately 50 categories. While
    this dimensionality can be reduced by visualizing only total expenditures (or any single category), this approach
    will miss potentially interesting variation between schools by expenditure category.
    Thus, pca_explorer:
        - Finds the principal components for the expenditure data for each year
        - Projects the schools onto the first two principal components (which capture the majority
        of the variation)
        - Plots schools on these two dimensions, labeling schools as (i) Title 1 or non-title 1
        - Colors schools based on their percentile rank with regards to the demographic variable
        selected by the user (from the 2006-2012 NYC School Demographics and Accountability Snapshot).
    Note this class will only behave as expected in the Jupyter iPython notebook environment
    since it is built on the ipywidget package.
    '''
    
    def __init__(self, feature = 'total_enrollment'):
        self.feature = feature
        self.all_years_data = self.norm_numeric()
        self.trans_x = self.PCA_fit()
        self.widget_keys =  self.make_keys_for_interactive_widget()
        self.w = interactive(self.plot_in_transformed_dimensions,
                             feature=widgets.Dropdown(options = self.widget_keys, description='Group schools by feature:', value="total_enrollment"))
        self.w.border_color = 'red'
        self.w.border_style = 'dotted'
        self.w.border_width = 3
        display(self.w)
         
    def read_data(self):
        '''
        read_data reads in the merged data set containing expenditure and demographic features for each school,
        for each year 2006-2012.
        '''
        all_years_data={}
        for year in range(2006,2013):
            all_years_data[year] = pd.read_csv('../data/merged_data/expenditure_demo_account_year_{}.csv'.format(str(year)), index_col=0)
        return all_years_data
        
    def norm_numeric(self):
        '''
        norm_numeric centers the expenditure features (by subtracting the mean), then scales them
        (dividing by the maximum). This is necessary so that PCA will identify the directions of
        maximal variation.
        '''
        all_years_data = self.read_data()
        for year in all_years_data:
            numeric = all_years_data[year].drop(['School','District','Title_1', 'Name', 'schoolyear',
                                                'fl_percent', 'frl_percent', 'total_enrollment', 'ell_percent',
                                                'sped_percent', 'asian_per', 'black_per', 'hispanic_per', 'white_per',
                                                'male_per', 'female_per', 'poverty_level', 'elementary_school',
                                                'middle_school', 'high_school'], axis=1)
            numeric = (numeric - numeric.mean())
            numeric = numeric / numeric.max()
            all_years_data[year] = pd.concat([numeric, all_years_data[year][['School','District','Title_1', 'Name', 'schoolyear',
                                                'fl_percent', 'frl_percent', 'total_enrollment', 'ell_percent',
                                                'sped_percent', 'asian_per', 'black_per', 'hispanic_per', 'white_per',
                                                'male_per', 'female_per', 'poverty_level', 'elementary_school',
                                                'middle_school', 'high_school']]], axis=1)
        return all_years_data
    
    def PCA_fit(self):
        '''
        PCA_fit uses principal component analysis (i.e. projecting the data onto the left singular vectors).
        It returns the transformed data (i.e. data expressed in the basis of the left singular vectors).
        '''
        all_years_data = self.all_years_data
        trans_x = {}
        for year in all_years_data:
            X = all_years_data[year].drop(['School','District','Title_1', 'Name', 'schoolyear',
                                                 'fl_percent', 'frl_percent', 'total_enrollment', 'ell_percent',
                                                 'sped_percent', 'asian_per', 'black_per', 'hispanic_per', 'white_per',
                                                 'male_per', 'female_per', 'poverty_level', 'elementary_school',
                                                 'middle_school', 'high_school'], axis=1)
            pca = PCA()
            trans_x[year] = pca.fit_transform(X)
        return trans_x
    
    def plot_in_transformed_dimensions(self, feature='total_enrollment'):
        '''
        Plot_in_transformed_dimensions takes a demographic feature as input. Then, for each year, it produces
        scatter plots of the schools on the first two principal components. In these plots, 
            - schools are identified as (i) Title 1 or non-title 1
            - schools are colored on their percentile rank, with regards to the demographic variable
            (from the 2006-2012 NYC School Demographics and Accountability Snapshot) selected by the
            user.
        '''
        plt.close('all')
        all_years_data = self.all_years_data
        trans_x = self.trans_x
        self.feature = feature
        fig = plt.figure(figsize=(13,23))   
        fig.subplots_adjust(hspace = .3, wspace=.2) 
        for year in all_years_data:
            ax = plt.subplot(4,2,year-2005)
            mask = (all_years_data[year]['Title_1'] == 1)
            colors = pd.Series([stats.percentileofscore(all_years_data[year][feature],x,kind='weak')/100.0 for x in all_years_data[year][feature]], index=all_years_data[year][feature].index)
            title1schools = ax.scatter(trans_x[year][mask.values,0],trans_x[year][mask.values,1], marker='+', c=colors[mask], cmap='cool', label='Title 1 schools')
            ax.scatter(trans_x[year][~mask.values,0],trans_x[year][~mask.values,1], marker='o', c=colors[~mask], cmap='cool', label='Non-Title 1 schools')
            Title = ' Title 1 vs non-Title 1 schools for year = {}\nSchools colored by {}'.format(str(year), self.map_feature_to_key(feature))
            ax.set_title(Title)
            ax.set_ylabel('Component 2')
            ax.set_xlabel('Component 1')
            
            legend = ax.legend()
            handles, labels = ax.get_legend_handles_labels() 
            legend.remove()
    
        ax = plt.subplot(4,2,8)
        ax.axis('off')
        ax.text(0, 1.05,"Explanation:\nIn these figures, Principal Components\nAnalysis (PCA) is used to reduce the\n"
        "dimensionality of the expenditure datset\n(from approximately 50 features) to just\n"
        "two dimensions. Then each school is plotted\nin this transformed space.\nNote the axes in these plots do not\n"
        "correspond to any single expenditure\n(or expenditure category). Instead, they\nallow the user to more easily visualize\n"
        "the expenditure data to identify\ntrends or clusters in the data.\nOn a more technical note, PCA is applied to each\n"
        "year individually, so the axes are variable.", fontsize=11, horizontalalignment='left', verticalalignment='top',
        multialignment='left', transform=ax.transAxes)
        ax.legend(handles, labels, shadow=True, loc='lower center', scatterpoints=1, title='School Category', fontsize='small')
        cbar = fig.colorbar(title1schools, orientation='horizontal', pad=0.02)
        cbar.set_label("School's percentile score for {}".format(self.map_feature_to_key(feature)))
        return
    
    def make_labels_from_features(self):
        '''
        make_labels_from_feature parses the name of the demographic features and returns a dictionary mapping
        the column names to human readable, informative feature descriptions.
        '''
        plot_by_feature = ['total_enrollment', 'ell_percent', 'sped_percent', 'asian_per', 'black_per', 'hispanic_per', 'white_per', 'male_per', 'female_per', 'poverty_level', 'elementary_school', 'middle_school', 'high_school']
        keys = [re.sub('_', ' ', x) for x in plot_by_feature]
        keys = [re.sub('sped', 'Special Education',  x) for x in keys]
        keys = [re.sub('ell', 'English Language Learner', x) for x in keys]
        keys = [re.sub('per$', 'percent', x) for x in keys]
        keys = [x.title() for x in keys]
        map_features_to_keys = dict(zip(plot_by_feature, keys))
        return map_features_to_keys
    
    def map_feature_to_key(self, feature):
        '''
        This function maps an input feature name to the corresponding human-readable, informative description produced
        by make_labels_from_features.
        '''
        map_feature_to_keys = self.make_labels_from_features()
        return map_feature_to_keys[feature]
    
    def make_keys_for_interactive_widget(self):
        '''
        This function inverts the self.features_for_widgets dictionary (mapping values back to keys), so the dictionary
        is in the format expected by the interactive widget.
        ''' 
        features=self.make_labels_from_features()
        features = {v: k for k, v in features.items()}
        return features
    


from check_data_and_ipython_call import try_call_function
try_call_function(pca_explorer)