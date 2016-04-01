#!/usr/bin/env python

import pandas as pd
import datetime
import iclrt_tools.lma.analysis.storm_analysis as st

# File names for first and second part of storm analysis
file1 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-1of2-exported.csv'
file2 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-2of2-exported.csv'

dates = ['08/27/2015', '08/28/2015']

file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA Analysis 08272015.csv'

storm_lma = st.Storm.from_lma_files([file1, file2], dates)
storm_ods = st.Storm.from_ods_file(file_name)

storm_ods.get_flash_rate(category='CG')
storm_ods.get_flash_rate(category='IC')

storm_lma.plot_all_charge_regions(show_plot=True)