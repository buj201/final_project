# NYC School Expenditure Visualizer

Author: Benjamin Jakubowski

Date: 12/15/2015

The purpose of this tool is to allow users to visually explore:

1. Differences in funding across NYC schools, and the relationship between school expenditures and characteristics (described <a href='http://schools.nyc.gov/Offices/DBOR/SBER/costvary.htm'> here by NYC Department of Education</a>).

2. Expenditures, by category, for a user-input school across the years 2006-2012. For context, the majority of schools' budgets are discretionary, with funds used at the principal's discretion (see, for example, <a href='http://schools.nyc.gov/offices/d_chanc_oper/budget/dbor/allocationmemo/fy12_13/FY13_PDF/FSF_Guide.pdf'>Fair Student Funding and School Budget Resource Guide </a>). This tool allows the user to see how, in fact, a school's principal is choosing to use these fair school funds.

## Installation

This program has many dependencies. In addition to packages in the standard library (urllib2, sys, os), additional required packages are listed below, along with URL’s for download instructions.
- pandas, scipy, matplotlib, and numpy: http://www.scipy.org/install.html (full SciPy stack)
- mpl_toolkits.basemap: http://matplotlib.org/basemap/users/installing.html
- ipywidgets: https://github.com/ipython/ipywidgets
- Jupyter Notebook (formerly known as iPython Notebook): http://jupyter.readthedocs.org/en/latest/install.html
- sklearn: http://scikit-learn.org/stable/install.html
- lxml.html: http://lxml.de/installation.html
- retrying: https://pypi.python.org/pypi/retrying
- six (note retrying requires six versions 1.7.0 or greater): https://pypi.python.org/pypi/six

## Usage

The program is divided into two packages: (1) get_clean_data and (2) expenditure_visualizer.

These programs are run as follows:

1. get_clean_data:
This program gets and cleans the 2006-2012 NYC School Expenditure data, gets and cleans the NYC Demographics and Accountability data, and cleans the SCHMA data (a csv file included in this repository). It is run from the terminal (after cd-ing into the get_clean_data directory) with the command ‘python main.py’.

2. expenditure_visualizer:
This program contains the modules and classes necessary to visualize the NYC School expenditure data. It is run from the Jupyter/iPython Notebook by:

  1. Opening Jupyter/iPython notebook (terminal command: ‘jupyter notebook’ or equivalently ‘ipython notebook’).

  2. Using the Jupyer GUI to navigating to the expenditure_visualizer directory in your filesystem.

  3. Opening the ‘main.ipynb’ iPython notebook and running the code cells (with python %run magic being used to call each of the visualization modules in the package).

## Credits

Data sources used include:

1. The <a href='https://data.cityofnewyork.us/Education/School-Demographics-and-Accountability-Snapshot-20/ihfw-zy9j'> NYC School Demographics and Accountability Snapshot 2006-2012 </a>, which includes demographic information for all NYC Public schools from 2006-2012;

2. The Research Alliance for New York City Schools <a href='http://steinhardt.nyu.edu/research_alliance/research/schma'>School-Level Master File (SCHMA)</a>, which (in this work) is only used to obtain geographic coordinates for schools from 2010-2012;

3. NYC <a href='http://schools.nyc.gov/Offices/DBOR/SBER/default.htm'>School-Based Expenditure Reports</a>, which were scraped to get the expenditure data used for all visualizations.