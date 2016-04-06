#!/usr/bin/env python

"""
Code to copy the LMA data files from the LMA HDD (or RAID array) to
the local computer for processing.

Original code by: Brian Hare
Modified by: Jaime Caicedo, PhD Student, ICLRT

Last modified: 07/31/2014

"""


import os
from copy import copy
from datetime import datetime,timedelta
from shutil import copy
import csv
import cPickle as pickle

csv.register_dialect('read', delimiter=' ', skipinitialspace=True)

seperator='/'

final_data_location='/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/data'
LMA_data_location='/media/jaime/Data/10microsecond_data'
# LMA_data_location='/media/jaime/ICLRTArray/LMA/10microsecond_data'
# LMA_data_location='/media/jaime/LarsenArray/LMA/10microsecond'

LMA_file_locations={'blanding_10':'blanding', 'blast_10':'blast', 'dupont_N_10':'dupont_N', 'dupont_S_10':'dupont_S', 'fl_dot_10':'fl_dot', 'golf_10':'golf','warehouse_10':'warehouse', 'wildlife_10':'wildlife' }

LMA_letters={'blanding':'g', 'blast':'a', 'dupont_N':'d', 'dupont_S':'c', 'fl_dot':'e', 'golf':'b', 'warehouse':'f', 'wildlife':'h', 'Test':'h'}

def timestamp_to_fname(site, timestamp, upper=False):
    letter=LMA_letters[site]
    if upper:
        letter=letter.upper()
    else:
        letter=letter.lower()

    return 'L'+letter+'_ICLRT_'+site+timestamp.strftime('_%y%m%d_%H%M%S')+'.dat'

def load_file_10MIN(timestamp, wildlife=False):
    ##copies all data files for the timestamp
    ##returns number of stations copied, and timestamp of file start

    mins = timestamp.strftime('%M')
    mins = mins[0]+'0'
    timestamp_floor = timestamp.replace(minute=int(mins), second=0)

    date_folder = timestamp_floor.strftime('%y%m%d')

    N_moved = 0
    for loc_file in LMA_file_locations:
        if os.path.isdir(LMA_data_location+seperator+loc_file+seperator+date_folder): ##the date folder exists
            ##wildlife stuff, sometimes we do not want to processes wildlife data
            if LMA_file_locations[loc_file]=='wildlife' and not wildlife:
                print "skipping wildlife station"
                continue

            if os.path.isfile(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor)):
                N_moved+=1
                copy(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor),  final_data_location+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor))
                print "    Copied:",LMA_file_locations[loc_file]

            elif os.path.isfile(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor,upper=True)):
                print "    Cannot do 80 microsecond data"
                #~ N_moved+=1
                #~ copy(LMA_data_location+'\\'+loc_file+'\\'+date_folder+'\\'+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor),  final_data_location+'\\'+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor,upper=True))

            elif LMA_file_locations[loc_file]=='wildlife' and  os.path.isfile(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname('Test',timestamp_floor)):
                ## sometimes wildlife goes under the name 'Test'
                N_moved+=1
                copy(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname('Test',timestamp_floor),  final_data_location+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor))
                print "    Copied:",LMA_file_locations[loc_file]

            else:
                print "    Error: file not found:",timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor), 'or', timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor, upper=True)
        else:
            print "    Folder not found:", LMA_data_location+seperator+loc_file+seperator+date_folder

    return N_moved,timestamp_floor


def copy_all(fname,dt=None, wildlife=False):
    if dt != None:
        DT_TD = timedelta(seconds=dt)
        
    ten_min = timedelta(minutes=10)

    with open('./CSV/'+fname+'.txt', 'rU') as fin:
        csv_file = csv.reader(fin, dialect='read')
        #~ csv_file.next() ##read off header
        
        for line in csv_file:
            if len(line)==0:
                continue
            elif line[0].split()[0][0] == "#":
                continue

            event_num = line[2]

            dd = '{0} {1}'.format(line[0], line[1])
            timestamp = datetime.strptime(dd.split('.')[0], '%Y-%m-%d %H:%M:%S')
            
            if dt==None:
                DT_TD=timedelta(seconds=int(line[3]))

            print
            print "Copying event", event_num
            num_stations_all = []
            present_time = timestamp - DT_TD
            while True:
                print "  Start time:", present_time
                num_stations, file_start = load_file_10MIN(present_time, wildlife)
                num_stations_all.append(num_stations)
                
                if file_start+ten_min >= timestamp + DT_TD:
                    break
                present_time = file_start + ten_min
            
            max_stations = max(num_stations_all)
            print "  Copied",max_stations,"stations max"
            
    return max_stations
        
if __name__ == '__main__':
    #~ wildlife=True  # True processes wildlife data
    copy_all('130609',None,True)       # Filename (CSV), delta_t in seconds (None to get delta_t from csv file), wildlife flag
