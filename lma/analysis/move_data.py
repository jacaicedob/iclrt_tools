#!/usr/bin/env python

from os import listdir, rename, makedirs
from os.path import isfile, join
import gzip
from shutil import move

data_folder='/home/jaime/Documents/LMA/Analysis/rawAnalyzer/output'
output_folder='/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/output'

def main(max_stations=0, folder='.'):
    try:
        makedirs(output_folder+'/'+folder)
    except OSError:
        pass

    all_files = [ f for f in listdir(data_folder) if isfile(join(data_folder,f)) and f.endswith('.gz') ]
    
    for ndf in all_files:
        string = '_%dstations' % max_stations
        new_name=ndf[:-7]+string+ndf[-7:]
        rename(data_folder+'/'+ndf, data_folder+'/'+new_name)
        
    all_files = [ f for f in listdir(data_folder) if isfile(join(data_folder,f)) and f.endswith('.gz') ]
    
    for a_f in all_files:
        move(data_folder+'/'+a_f, output_folder+'/'+folder+'/'+a_f)
        print "Moved:", a_f[0:-3]
        
    data_files = [ f for f in listdir(output_folder+'/'+folder) if isfile(join(output_folder+'/'+folder,f)) and f.endswith('.dat.gz') ]

    print "\n"

    for d_f in data_files:
        fin = gzip.open(output_folder+'/'+folder+'/'+d_f, 'rb')
        data = fin.read()
        fin.close()

        with open(output_folder+'/'+folder+'/'+d_f[0:-3],'w') as fout:
            fout.write(data)

        print "Unzipped:", d_f[0:-3]


if __name__ == '__main__':
    main(max_stations=6)
