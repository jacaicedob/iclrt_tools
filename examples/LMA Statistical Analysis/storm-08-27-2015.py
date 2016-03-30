
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
get_ipython().magic('matplotlib inline')

import seaborn as sns


# In[2]:

# File names for first and second part of storm analysis
file_name = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-1of2-exported.csv'
file_name_2 = '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/Storm-08-27-2015/LMA/ChargeAnalysis-2of2-exported.csv'


# In[3]:

# Create Pandas objects
storm_1 = pd.read_csv(file_name)
storm_2 = pd.read_csv(file_name_2)


# In[4]:

# Insert a column with the appropriate date for each part
storm_1.insert(0,'Date', '08/27/2015')
storm_2.insert(0,'Date', '08/28/2015')


# In[5]:

d = datetime.timedelta(days=1).total_seconds()

storm_2['time(UT-sec-of-day)'] = storm_2['time(UT-sec-of-day)'] + d


# In[6]:

#  storm_1.head()


# In[7]:

#  storm_2.head()


# In[8]:

# Combine both DataFrames into one
storm = pd.concat([storm_1, storm_2])
storm['time'] = storm['time(UT-sec-of-day)'] * 1e-3
#  storm


# In[9]:

# Generate a DataFrame for all positive charge sources
positive_charge = storm[storm['charge'] == 3]

# Generate a DataFrame for all negative charge sources
negative_charge = storm[storm['charge'] == -3]


# In[10]:

# Get quick statistics on the positive charge sources
#positive_charge.describe()
mean = positive_charge['alt(m)'].mean()
stdev = positive_charge['alt(m)'].std()
minn = positive_charge['alt(m)'].min()
maxx = positive_charge['alt(m)'].max()

print('Positive charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(mean, stdev, minn, maxx))


# In[11]:

positive_charge.describe()


# In[12]:

# Get quick statistics on the negative charge sources
# negative_charge.describe()
mean = negative_charge['alt(m)'].mean()
stdev = negative_charge['alt(m)'].std()
minn = negative_charge['alt(m)'].min()
maxx = negative_charge['alt(m)'].max()

print('Negative charge alt (m) statistics:\nMean: {0:0.2f}\nStd. dev.: {1:0.2f}\nMinimum: {2:0.2f}\nMaximum: {3:0.2f}\n'.format(mean, stdev, minn, maxx))


# In[13]:

negative_charge.describe()


# In[14]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(8,6), sharey=True)

positive_charge.plot('time', 'alt(m)',
                     kind='scatter', c='r', lw=0, alpha=0.01,
                     ax=ax)

positive_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='r', alpha=0.5, bins=1000, lw=0)

ax.set_title('Positive Charge Sources')
ax2.set_title('Altitude Histrogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[15]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(8,6), sharey=True)

negative_charge.plot('time', 'alt(m)',
                     kind='scatter', c='b', lw=0, alpha=0.01,
                     ax=ax)

negative_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='b', alpha=0.5, bins=1000, lw=0)


ax.set_title('Negative Charge Sources')
ax2.set_title('Altitude Histrogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[16]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(8,6), sharey=True)

positive_charge.plot('time', 'alt(m)',
                     kind='scatter', c='r', lw=0, alpha=0.01,
                     ax=ax)
negative_charge.plot('time', 'alt(m)',
                     kind='scatter', c='b', lw=0, ax=ax, alpha=0.01)


positive_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='r', alpha=0.5, bins=1000, lw=0)
negative_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                               color='b', alpha=0.5, bins=1000, lw=0)


ax.set_title('Sources')
ax2.set_title('Altitude Histrogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[17]:

print(d - datetime.timedelta(minutes=20).total_seconds())
print(d)


# In[18]:

subset = storm[storm['time(UT-sec-of-day)'] < 83050]
# subset = subset[subset['time(UT-sec-of-day)'] > 85200.0]


# In[19]:

# Generate a DataFrame for all positive charge sources
subset_pos_charge = subset[subset['charge'] == 3]

# Generate a DataFrame for all negative charge sources
subset_neg_charge = subset[subset['charge'] == -3]


# In[20]:

subset_pos_charge.describe()


# In[21]:

subset_neg_charge.describe()


# In[22]:

fig, (ax, ax2) = plt.subplots(1,2,figsize=(8,6), sharey=True)

subset_pos_charge.plot('time', 'alt(m)',
                       kind='scatter', c='r', lw=0, alpha=0.01,
                       ax=ax)
subset_neg_charge.plot('time', 'alt(m)',
                       kind='scatter', c='b', lw=0, ax=ax,
                       alpha=0.01)

subset_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                 color='r', alpha=0.5, bins=1000, lw=0)
subset_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                 color='b', alpha=0.5, bins=1000, lw=0)

# xlims = ax.get_xlim()
# ax.plot([xlims[0], xlims[1]], 
#         [subset_pos_charge.mean(), subset_pos_charge.mean()],
#         'g')
# ax.plot([xlims[0], xlims[1]], 
#         [subset_neg_charge.mean(), subset_neg_charge.mean()],
#         'g')

ax.set_title('Positive Charge Sources (Subset)')
ax2.set_title('Altitude Histrogram')

ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
ax2.set_xlabel('Number of sources')

ax.set_ylabel('Altitude (m)')

ax.grid(True)
ax.set_ylim([0,16000])


# In[23]:

t_increment = 5*60  # seconds

start_time = positive_charge['time(UT-sec-of-day)'].min()
end_time = start_time + t_increment

while start_time < positive_charge['time(UT-sec-of-day)'].max():
    subset = storm[storm['time(UT-sec-of-day)'] < end_time]
    subset = subset[subset['time(UT-sec-of-day)'] > start_time]
    
    subset_pos_charge = subset[subset['charge'] == 3]
    subset_neg_charge = subset[subset['charge'] == -3]
    
    try:
        fig, (ax, ax2) = plt.subplots(1,2,figsize=(12,6), sharey=True)

        subset_pos_charge.plot('time', 'alt(m)',
                               kind='scatter', c='r', lw=0, alpha=0.01,
                               ax=ax)
        subset_neg_charge.plot('time', 'alt(m)',
                               kind='scatter', c='b', lw=0, ax=ax,
                               alpha=0.01)

        subset_pos_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                         color='r', alpha=0.5, bins=1000, lw=0)
        subset_neg_charge['alt(m)'].hist(ax=ax2, orientation='horizontal',
                                         color='b', alpha=0.5, bins=1000, lw=0)
        
        
        ax.set_title('Sources')
        ax2.set_title('Altitude Histrogram')
        
        ax.set_xlabel(r'Time $\times 10^3$ (sec of day) ')
        ax2.set_xlabel('Number of sources')
        
        ax.set_ylabel('Altitude (m)')
        
        ax.grid(True)
        ax.set_ylim([0, 16e3])
        
        fig.savefig('./storm-08-27-2015_%d.png' % start_time, 
                    format='png', dpi=300)
    except TypeError as e:
        pass    
    
    start_time = end_time
    end_time += t_increment


# In[ ]:



