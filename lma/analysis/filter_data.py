#!/usr/bin/env python

import os
from subprocess import call

data_folder='/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/data' # Data location
filter_EXE='/home/jaime/Documents/LMA/Analysis/rawAnalyzer/data/v11_to_v9.out'

def filter_all():
    os.chdir(data_folder)

    data_files = [ f for f in os.listdir('./') if os.path.isfile(os.path.join('./',f)) and f.endswith('.dat') and f[0]=='L' and f[1].islower()]
    
    no_delete_data_files = [ f for f in os.listdir('./') if os.path.isfile(os.path.join('./',f)) and f.endswith('.dat') and f[0]=='L' and f[1].isupper()]

    for df in data_files:
        call([filter_EXE,df])

    new_data_files = [ f for f in os.listdir('./') if os.path.isfile(os.path.join('./',f)) and f.endswith('.dat') and f[0]=='L']
    
    print "\nRenaming files..."
    for ndf in new_data_files:
        if ndf[-7:]=='_v9.dat':
            new_name='L'+ndf[1].upper()+ndf[2:]
            os.rename('./'+ndf, './'+new_name)
        elif ndf not in no_delete_data_files:
            os.remove(ndf)


if __name__ == '__main__':

    print "--fitering data--"
    filter_all()
