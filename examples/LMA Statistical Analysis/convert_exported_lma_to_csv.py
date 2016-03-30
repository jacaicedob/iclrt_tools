
# coding: utf-8

# In[1]:

file_names = ['/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1120-exported.dat',
              '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1130-exported.dat',
              '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1140-exported.dat',
              '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1150-exported.dat',
              '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1200-exported.dat',
              '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1210-exported.dat',
              '/home/jaime/Documents/ResearchTopics/Publications/LightningEvolution/PossibleStorms/Storm-02-24-2016/LMA/ChargeAnalysis_1220-exported.dat']


# In[2]:

for file_name in file_names:
    
    lines = ''
    
    f = open(file_name, 'r')
    for line in f:
        words = f.readline().split()
        lines += ','.join(words)
        lines += '\n'
        
    f.close()
    
    f1 = open(file_name, 'w')
    f1.write(lines)
    f1.close()    


# In[ ]:



