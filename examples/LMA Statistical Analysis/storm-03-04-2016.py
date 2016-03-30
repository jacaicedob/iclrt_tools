
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


# In[3]:

# Create Pandas objects
cell_1_pds = []
cell_2_pds = []

for file_name in cell_1_files:
    cell_1_pds.append(pd.read_csv(file_name))

for file_name in cell_2_files:
    cell_2_pds.append(pd.read_csv(file_name))


# In[4]:

# Combine all the DataFrames into one bigger one per cell
cell_1 = pd.concat(cell_1_pds)
cell_2 = pd.concat(cell_2_pds)

cell_1['time'] = cell_1['time(UT-sec-of-day)'] * 1e-3
cell_2['time'] = cell_2['time(UT-sec-of-day)'] * 1e-3


# In[5]:

# d = datetime.datetime.strptime('03/04/2016', '%m/%d/%Y')
# for i in cell_1['time(UT-sec-of-day)']:
#     cell_1['time(UT-sec-of-day)'][i] = d + datetime.timedelta(seconds=i)
    
# for i in cell_2['time(UT-sec-of-day)']:
#     cell_2['time(UT-sec-of-day)'][i] = d + datetime.timedelta(seconds=i)


# In[6]:

# Insert a column with the appropriate date for each cell
cell_1.insert(0,'Date', '03/04/2016')
cell_2.insert(0,'Date', '03/04/2016')
# cell_1.set_index('time(UT-sec-of-day)', inplace=True)


# In[7]:

# Generate a DataFrame for all positive  and negative charge sources of cell 1
cell_1_pos_charge = cell_1[cell_1['charge'] == 3]  # positive
cell_1_neg_charge = cell_1[cell_1['charge'] == -3]  #negative

# Generate a DataFrame for all positive  and negative charge sources of cell 2
cell_2_pos_charge = cell_2[cell_2['charge'] == 3]  # positive
cell_2_neg_charge = cell_2[cell_2['charge'] == -3]  #negative


# In[8]:

# Get quick statistics on the charge sources of cell 1
cell_1_pos_charge.describe()


# In[9]:

cell_1_neg_charge.describe()


# In[10]:

# Get quick statistics on the charge sources of cell 2
cell_2_pos_charge.describe()


# In[11]:

cell_2_neg_charge.describe()


# In[12]:

# Get quick statistics on the positive charge sources
# positive_charge.describe()
# mean = positive_charge['alt(m)'].mean()
# stdev = positive_charge['alt(m)'].std()
# minn = positive_charge['alt(m)'].min()
# maxx = positive_charge['alt(m)'].max()

# print('Positive charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(mean, stdev, minn, maxx))


# In[13]:

# Get quick statistics on the negative charge sources
# negative_charge.describe()
# mean = negative_charge['alt(m)'].mean()
# stdev = negative_charge['alt(m)'].std()
# minn = negative_charge['alt(m)'].min()
# maxx = negative_charge['alt(m)'].max()


# In[14]:

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


# In[15]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

cell_2_pos_charge.plot('time', 'alt(m)',
                       kind='scatter', c='r', lw=0, alpha=0.01,
                       ax=ax)

cell_2_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                 color='r', alpha=0.5, bins=1000, lw=0)

ax.set_title('Cell 2 - Positive Charge Sources')
ax2.set_title('Altitude Histogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[16]:

both = pd.concat([cell_1, cell_2])


# In[17]:

both_pos_charge = both[both['charge'] == 3]  # positive
both_neg_charge = both[both['charge'] == -3]  #negative


# In[18]:

both_pos_charge.describe()


# In[19]:

both_neg_charge.describe()


# In[20]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

both_pos_charge.plot('time', 'alt(m)',
                     kind='scatter', c='r', lw=0, alpha=0.01,
                     ax=ax)
both_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='r', alpha=0.5, bins=1000, lw=0)

ax.set_title('Both cells - Positive Charge')
ax2.set_title('Altitude Histogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[21]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

both_neg_charge.plot('time', 'alt(m)',
                     kind='scatter', c='b', lw=0, alpha=0.01,
                     ax=ax)
both_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='b', alpha=0.5, bins=1000, lw=0)

ax.set_title('Both cells - Negative Charge')
ax2.set_title('Altitude Histogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[22]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

both_pos_charge.plot('time', 'alt(m)',
                     kind='scatter', c='r', lw=0, alpha=0.01,
                     ax=ax)
both_neg_charge.plot('time', 'alt(m)',
                     kind='scatter', c='b', lw=0, ax=ax, alpha=0.01)

both_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='r', alpha=0.5, bins=1000, lw=0)
both_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='b', alpha=0.5, bins=1000, lw=0)

ax.set_title('Both cells - All Charge')
ax2.set_title('Altitude Histogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[ ]:



