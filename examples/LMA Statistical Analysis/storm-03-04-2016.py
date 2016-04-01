#!/usr/bin/env python

import pandas as pd
import datetime
import iclrt_tools.lma.analysis.storm_analysis as st

# File names for first and second cell of storm
cell_1_files = ['/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0540-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0550-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0600-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0610-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell1_0620-exported.csv']

cell_2_files = ['/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0600-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0610-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0620-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0630-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0640-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0650-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/LMA/ChargeAnalysis_Cell2_0700-exported.csv']

dates = ['03/04/2016']

file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/Cell1 Analysis 03042016.csv'

file_name_2 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-03-04-2016/Cell2 Analysis 03042016.csv'

storm_lma_1 = st.Storm.from_lma_files(cell_1_files, dates)
storm_lma_2 = st.Storm.from_lma_files(cell_2_files, dates)

storm_ods_1 = st.Storm.from_ods_file(file_name)
storm_ods_2 = st.Storm.from_ods_file(file_name_2)

storm_ods_1.get_flash_rate(category='IC')
storm_ods_1.get_flash_rate(category='CG')
storm_lma_1.plot_all_charge_regions()

storm_ods_2.get_flash_rate(category='IC')
storm_ods_2.get_flash_rate(category='CG')
storm_lma_2.plot_all_charge_regions(show_plot=True)
