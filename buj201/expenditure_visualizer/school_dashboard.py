'''
Created on Dec 11, 2015

@author: Benjamin Jakubowski
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from ipywidgets import widgets, interactive
import re
from IPython.display import display, clear_output

class school_dashboard(object):
    '''
    Class to encapsulate data and methods for interactive school dashboard. Once the dashboard
    has been initialized, it accepts as text string as a search term. It then returns a dropdown
    menu listing up to 20 matching school names. If the user selects one of the schools from
    the dropdown menu, the school_dashboard returns a set of plots showing:
        - The total expenditures per student for the school, and the average total expenditures
        per student for a reference group. For a given year, the reference group is either:
            (i) all other Title 1 NYC schools (if the input school was Title 1 for that year)
            (ii) all other non-Title 1 NYC schools (if the input school was not Title 1 for that year)
        - The distribution of expenditures across the expenditure-group subtotals (again, expenditures
        are grouped into categories such as "Building Services" and "Classroom Instruction"). This plot
        again includes bars showing the expenditure distribution averaged across the reference group.
    '''
    
    def __init__(self):
        self.all_years_data = self.get_data()
        
        ##Make initial widget
        self.container = widgets.Box()
        self.container.border_color = 'red'
        self.container.border_style = 'dotted'
        self.container.border_width = 3
        self.Search = widgets.Text(description='Search:', value='Enter school name here')
        self.container.children=[self.Search]
        display(self.container)
        self.Search.on_submit(self.update_dropdown)
    
    def get_data(self):
        '''
        Reads in the merged data set containing expenditure and demographic features for each school,
        for each year 2006-2012.
        '''
        all_years_data={}
        for year in range(2006, 2013):
            all_years_data[year] = pd.read_csv('../data/merged_data/expenditure_demo_account_year_{}.csv'.format(year), index_col=0)
        return all_years_data
    
    def update_dropdown(self, search):
        '''
        Takes a search string as input. If this search string matches the name of any schools in the
        dataset, returns a dropdown menu containing up to the first twenty results. Initially, the dashboard
        plots are generated for the first matching school (to illustrate the output of this plot).
        If the user selects a different school from this dropdown menu, the dashboard plots are
        generated for the selected school.
        '''
        clear_output()
        schools = self.search_function(search)
        if len(schools)>1:
            self.plot_school(schools[0])
            select_from = interactive(self.plot_school, school=widgets.Dropdown(options = schools, description = 'Select school to plot: '))
            self.container.children=[self.Search,select_from]
        if len(schools)==1:
            self.plot_school(schools[0])
            select_from = interactive(self.plot_school, school=widgets.Dropdown(options = schools, description = 'Select school to plot: '))
            self.container.children=[self.Search,select_from]
        if len(schools)==0:
            print '{} not found- please search for a different school'.format(self.Search.value)
            select_from = interactive(self.plot_school, school=widgets.Dropdown(options = schools, description = 'Select school to plot: '))
            self.container.children=[self.Search,select_from]
        
    def search_function(self, searched_school):
        '''
        search_function takes an input search string, parses it, then searches for matching (parsed)
        school names in the dataset. If more than 20 results are found, prints a warning message
        that only the first two are returned. Then returns all matching schools (to present in the
        dropdown menu).
        '''
        searched_school = searched_school.value
        ## Get school_names
        unique_schools = []
        for year in self.all_years_data:
            self.all_years_data[year].Name = self.all_years_data[year].Name.map(lambda x: str(x).strip()) #strip whitespace
            self.all_years_data[year].Name = self.all_years_data[year].Name.map(lambda x: re.sub('[^a-zA-Z0-9\s]','',x)) #strip non alphanumeric characters
            self.all_years_data[year].Name = self.all_years_data[year].Name.map(lambda x: str(x).upper()) #make uppercase
            unique_schools.extend(list(self.all_years_data[year].Name))
        unique_schools = list(set(unique_schools))

        ## Search through school names
        upper_school = re.sub('[^0-9a-zA-Z\s]', '', searched_school).upper()
        matches = [re.search(upper_school, name) for name in unique_schools]
        matching_schools = [i.string for i in matches if i != None]
        if len(matching_schools)<20:
            return matching_schools
        else:
            print '{} results found- here are 20 results. Re-search using more specific search terms.'.format(len(matching_schools))
            return matching_schools[0:20]
    
    
    def plot_school(self, school):
        '''
        Takes an input school name (note plot_school is called by update_dropdown, and as such the
        input school name is already matches a records in the dataset). plot_school then returns the
        a plot with the following subplots:
             - The total expenditures per student for the school, and the average total expenditures
            per student for a reference group. For a given year, the reference group is either:
                (i) all other Title 1 NYC schools (if the input school was Title 1 for that year)
                (ii) all other non-Title 1 NYC schools (if the input school was not Title 1 for that year)
            - The distribution of expenditures across the expenditure-group subtotals (again, expenditures
            are grouped into categories such as "Building Services" and "Classroom Instruction"). This plot
            again includes bars showing the expenditure distribution averaged across the reference group.
        '''
        
        plt.figure(figsize=(16,12))
        total_per_student = {}
        mean_by_T1_status = {}
        title_1 = {'Title 1':[],'non-Title 1':[]}
        for year in self.all_years_data:

            #Get group mean for comparison
            if self.all_years_data[year].loc[self.all_years_data[year]['Name'] == school,'Title_1'].isin([1]).values:
                title_1['Title 1'].append(year)
                mean_by_T1_status[year] = self.all_years_data[year].loc[self.all_years_data[year]['Title_1'] == 1,'Total'].mean()
            elif self.all_years_data[year].loc[self.all_years_data[year]['Name'] == school,'Title_1'].isin([0]).values:
                title_1['non-Title 1'].append(year)
                mean_by_T1_status[year] = self.all_years_data[year].loc[self.all_years_data[year]['Title_1'] == 0,'Total'].mean()

            #If school exists, get data for year
            if len(self.all_years_data[year].loc[self.all_years_data[year]['Name'] == school,'Total'])>0:
                total_per_student[year] = self.all_years_data[year].loc[self.all_years_data[year]['Name'] == school,'Total']

        mean_by_T1_status = pd.DataFrame.from_dict(mean_by_T1_status, orient='index')
        mean_by_T1_status.sort(inplace=True)
        total_per_student = pd.DataFrame.from_dict(total_per_student, orient='index')
        total_per_student.sort(inplace=True)


        ##Ax one- total expenditure comparison
        ax1 = plt.subplot(3,1,1)
        ax1.plot(total_per_student.index, total_per_student.values, marker='s', markersize=10, label='Expenditures per student at {}'.format(school.title()))

        ##Make label for comparison plot:
        if len(title_1['Title 1']) == 0:
            comparison_label = 'Average expenditures across all non-Title 1 schools citywide'
        elif len(title_1['non-Title 1']) == 0:
            comparison_label = 'Average expenditures across all Title 1 schools citywide'
        else: ##Need to specify years for comparison
            comparison_label = 'Average expenditures across Title 1 schools (years {})\nand non-Title 1 schools (years {})'.format(str(title_1['Title 1']).strip('[]'),str(title_1['non-Title 1']).strip('[]'))
            
        ##Make first plot (scatter plot of total funding)
        ax1.plot(mean_by_T1_status.index, mean_by_T1_status.values, marker='o', markersize=10, label=comparison_label)
        title = 'Total expenditures per student by year'
        ax1.set_title(title)
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Total expenditures per student ($)')
        ax1.set_xlim((2006,2012))
        min_val = min(mean_by_T1_status.values.min(), total_per_student.values.min())-2000
        max_val = max(mean_by_T1_status.values.max(), total_per_student.values.max())+1000
        ax1.set_ylim((min_val,max_val))
        ax1.ticklabel_format(useOffset=False)
        ax1.legend(loc='lower center', fancybox=True, shadow=True, ncol=2, fontsize='medium')
        
        ##Make the bar charts comparing the distribution of the school's per-category expenditures.
        ##To the city-wide comparison group. Note make_all_subplots take a DBN as input, so we first
        ##map the school name returned by the search to a DBN for (at least) one year.
        DBN = []
        for year in self.all_years_data:
            DBN.extend(self.all_years_data[year].loc[self.all_years_data[year]['Name'] == school,'School'])
        if len(DBN) > 0:
            self.make_all_subs(list(set(DBN))[0])
        plt.show()
        return 
    
    def make_sub_plot(self, year, DBN):
        '''
        Takes an input year and DBN (from plot_school) and return a single subplot showing the distribuion
        of expenditures by category for the year, for both the input school and the comparison group.
        '''
        matches = [re.search(r'_All_Funds', x) for x in list(self.all_years_data[year].columns)]
        matches = [x for x in matches if x is not None]
        matches = [x.string for x in matches]
    
        matches_keys = [' '.join(re.findall('[A-Z][^A-Z]*', x)) for x in matches]
        matches_keys = [re.sub('_',' ', x) for x in matches_keys]
        matches_keys = [re.sub('  ', ' ', x) for x in matches_keys]
        matches_keys = [re.sub('Srcs', 'Services', x) for x in matches_keys]
        matches_keys = [re.sub(' All Funds', '', x) for x in matches_keys]
        map_cols_to_keys = dict(zip(matches, matches_keys))
        
        possible_categories = ['Instructional Support Services', 'Central Instructional Support',
                               'Central Administration', 'Leadership Supervision Support',
                               'Ancillary Support Services', 'Building Services', 'Regional Support',
                               'Classroom Instruction', 'Instructional Support and Administration',
                               'Other Regional Costs', 'Referral and Evaluation Services',
                               'Field Support', 'Instructional Support Services', 'Other Field Support Costs',]
        
        color_scale = [plt.get_cmap('Set1')(i) for i in np.linspace(0, 1, len(possible_categories))]
        map_keys_to_colors = dict(zip(possible_categories,color_scale))
    
        #School data
        target_school = self.all_years_data[year].loc[DBN, matches]
        target_school.index = [map_cols_to_keys[x] for x in target_school.index]
        target_school.sort(inplace=True, ascending=False)
        target_school = target_school/target_school.sum()
        target_school.name = ''
        school_colors=[map_keys_to_colors[x] for x in target_school.index]
        handles = [mpatches.Patch(color=map_keys_to_colors[x], label=str(x)) for x in list(target_school.index)]
        
        #Comparison data
        compare_groups = self.all_years_data[year].groupby('Title_1')
        mean_expenditures = compare_groups.get_group(self.all_years_data[year].loc[DBN,'Title_1'])[matches].mean()
        mean_expenditures.index = [map_cols_to_keys[x] for x in mean_expenditures.index]
        mean_expenditures.sort(inplace=True, ascending=False)
        mean_expenditures = mean_expenditures/mean_expenditures.sum()
        mean_expenditures.name = ''
        compare_colors=[map_keys_to_colors[x] for x in mean_expenditures.index]
        handles.extend([mpatches.Patch(color=map_keys_to_colors[x], label=str(x)) for x in list(mean_expenditures.index)])
        
        xs_for_bar = dict(zip(possible_categories, range(1, len(possible_categories)+1)))
        ax = plt.gca()
        ax.set_axisbelow(True)
        plt.grid(color='k', axis='y', linestyle='-', linewidth=0.5)
        school = plt.bar([xs_for_bar[x] for x in target_school.index], target_school.values, width=0.4, color=school_colors)
        compare = plt.bar([xs_for_bar[x] + 0.4 for x in mean_expenditures.index], mean_expenditures.values, width=0.4,  color=compare_colors)
        for bar in compare:
            bar.set_hatch('//')
        plt.xticks([],[])
        return (handles, school, compare)
    
    def make_all_subs(self,DBN):
        '''
        Takes a given DBN, and makes all the bar subplots (calling make_sub_plot for each year
        between 2006 and 2012. Additionally, makes a legend including all colors used for bars
        across the 7 years. Returns all the subplots as the 2nd and 3rd row in a 3x4 subplot array.
        '''
        handles = []
        handle_labels = []
        for year in range(2006,2010):
            ax = plt.subplot(3,4, year-2001)
            ax.set_title(str(year))
            try:
                handle_for_school, school, compare = self.make_sub_plot(year, DBN)
                if year == 2006:
                    plt.ylabel('Percent of Total Expenditures')
                handles.extend(handle_for_school)
            except KeyError: ##School not in dataset for year
                ax.axis('off')
                ax.text(0.5, 0.5,'Data not available\nfor {}'.format(str(year)), fontsize=16,
                        horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
                
        for year in range(2010, 2013):
            ax = plt.subplot(3,4, year-2001)
            ax.set_title(str(year))
            try:
                handle_for_school, school, compare = self.make_sub_plot(year, DBN)
                if year == 2010:
                    plt.ylabel('Percent of Total Expenditures')
                handles.extend(handle_for_school)
            except KeyError: ##School not in dataset for year
                ax.axis('off')
                ax.text(0.5, 0.5,'Data not available\nfor {}'.format(str(year)), fontsize=16,
                        horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    
        legend_corner = plt.subplot(3,4,12)
        legend_corner.axis('off')
        unique_handles = []
        for patch in handles:
            if patch.get_label() in handle_labels:
                pass
            else:
                handle_labels.append(patch.get_label())
                unique_handles.append(patch)
        plt.legend(handles=unique_handles, fontsize='medium', loc='center', title='Legend')



from check_data_and_ipython_call import try_call_function
try_call_function(school_dashboard)