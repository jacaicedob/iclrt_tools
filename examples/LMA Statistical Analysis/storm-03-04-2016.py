#!/usr/bin/env python

import pandas as pd
import datetime
import iclrt_tools.lma.analysis.storm_analysis as st
import matplotlib.pyplot as plt
import seaborn as sns

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

storm_lma_1 = st.StormLMA.from_lma_files(cell_1_files, dates)
storm_lma_2 = st.StormLMA.from_lma_files(cell_2_files, dates)

storm_ods_1 = st.StormODS.from_ods_file(file_name)
storm_ods_2 = st.StormODS.from_ods_file(file_name_2)

# storm_lma_2.plot_charge_region(charge='positive')
# storm_lma_2.plot_charge_region(charge='negative')
# storm_lma_2.plot_all_charge_regions(show_plot=True)

ics = storm_ods_1.get_flash_type('IC')
cgs = storm_ods_1.get_flash_type('-CG')

# ic_series = ics['Initiation Height (km)']
# cg_series = cgs['Initiation Height (km)']
ic_series = ics['Area (km^2)']
cg_series = cgs['Area (km^2)']

data_frame = pd.DataFrame({' ICs': ic_series, '-CGs': cg_series})
fig, ax = plt.subplots(1, 1, figsize=(12, 6))
data_frame.plot.hist(alpha=0.5, ax=ax)
# ax.set_title('Histogram of initiation heights for ICs and -CGs')
# ax.set_xlabel('Initiation Height (km)')
ax.set_title('Histogram of flash areas for ICs and -CGs')
ax.set_xlabel(r'Flash Area (km$^2$)')
ax.legend()
plt.show()


# storm_ods_1.get_flash_rate(category='IC')
# storm_ods_1.get_flash_rate(category='CG')
# storm_lma_1.plot_all_charge_regions()
#
# storm_ods_2.get_flash_rate(category='IC')
# storm_ods_2.get_flash_rate(category='CG')
# storm_lma_2.plot_all_charge_regions(show_plot=True)
