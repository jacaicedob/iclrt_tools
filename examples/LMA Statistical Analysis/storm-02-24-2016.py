
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
get_ipython().magic('matplotlib inline')

import seaborn as sns


# In[2]:

# File names for first and second cell of storm
cell_1_files = ['/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1120-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1130-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1140-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1150-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1200-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1210-exported.csv',
                '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1220-exported.csv']


# In[3]:

# Create Pandas objects
cell_1_pds = []

for file_name in cell_1_files:
    print(file_name)
    cell_1_pds.append(pd.read_csv(file_name))


# In[4]:

# Combine all the DataFrames into one bigger one per cell
cell_1 = pd.concat(cell_1_pds)


# In[5]:

# d = datetime.datetime.strptime('03/04/2016', '%m/%d/%Y')
# for i in cell_1['time(UT-sec-of-day)']:
#     cell_1['time(UT-sec-of-day)'][i] = d + datetime.timedelta(seconds=i)
    
# for i in cell_2['time(UT-sec-of-day)']:
#     cell_2['time(UT-sec-of-day)'][i] = d + datetime.timedelta(seconds=i)


# In[6]:

# Insert a column with the appropriate date for each cell
cell_1.insert(0,'Date', '02/24/2016')
cell_1['time'] = cell_1['time(UT-sec-of-day)'] * 1e-3
# cell_1.set_index('time(UT-sec-of-day)', inplace=True)


# In[7]:

# Generate a DataFrame for all positive  and negative charge sources of cell 1
cell_1_pos_charge = cell_1[cell_1['charge'] == 3]  # positive
cell_1_neg_charge = cell_1[cell_1['charge'] == -3]  #negative


# In[8]:

# Get quick statistics on the charge sources of cell 1
cell_1_pos_charge.describe()


# In[9]:

cell_1_neg_charge.describe()


# In[10]:

# Get quick statistics on the positive charge sources
# positive_charge.describe()
# mean = positive_charge['alt(m)'].mean()
# stdev = positive_charge['alt(m)'].std()
# minn = positive_charge['alt(m)'].min()
# maxx = positive_charge['alt(m)'].max()

# print('Positive charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(mean, stdev, minn, maxx))


# In[11]:

# Get quick statistics on the negative charge sources
# negative_charge.describe()
# mean = negative_charge['alt(m)'].mean()
# stdev = negative_charge['alt(m)'].std()
# minn = negative_charge['alt(m)'].min()
# maxx = negative_charge['alt(m)'].max()


# In[12]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

cell_1_pos_charge.plot('time', 'alt(m)',
                       kind='scatter', c='r', lw=0, alpha=0.01,
                       ax=ax)

cell_1_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                 color='r', alpha=0.5, bins=1000, lw=0)

ax.set_title('Cell 1 - Positive Charge Sources')
ax2.set_title('Altitude Histogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[13]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

cell_1_neg_charge.plot('time', 'alt(m)',
                       kind='scatter', c='b', lw=0, alpha=0.01,
                       ax=ax)

cell_1_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                 color='b', alpha=0.5, bins=1000, lw=0)

ax.set_title('Cell 1 - Negative Charge Sources')
ax2.set_title('Altitude Histogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[14]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

cell_1_pos_charge.plot('time', 'alt(m)',
                       kind='scatter', c='r', lw=0, alpha=0.01,
                       ax=ax)
cell_1_neg_charge.plot('time', 'alt(m)',
                       kind='scatter', c='b', lw=0, ax=ax, alpha=0.01)

cell_1_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                 color='r', alpha=0.5, bins=1000, lw=0)
cell_1_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                 color='b', alpha=0.5, bins=1000, lw=0)


ax.set_title('All Sources')
ax2.set_title('Altitude Histogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[ ]:



