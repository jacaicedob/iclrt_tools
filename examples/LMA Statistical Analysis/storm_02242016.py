#!/usr/bin/env python

import pandas as pd
import datetime

import iclrt_tools.lma.analysis.storm_analysis as st

cell_1_files = [
    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1120-exported.csv',
    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1130-exported.csv',
    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1140-exported.csv',
    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1150-exported.csv',
    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1200-exported.csv',
    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1210-exported.csv',
    '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/LMA/ChargeAnalysis_1220-exported.csv']

dates = ['02/24/2016']

file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-02-24-2016/Cell1 Analysis 02242016.csv'


storm_lma = st.Storm.from_lma_files(cell_1_files, dates)
storm_ods = st.Storm.from_ods_file(file_name)

storm_ods.get_flash_rate(category='IC')
storm_lma.plot_charge_region(show_plot=True)
storm_lma.plot_all_charge_regions(show_plot=True)
storm_lma.analyze_subset('2016-02-24 11:25:00.0', '2016-02-24 13:30:00.0', plot=True)

