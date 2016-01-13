import os
from copy import copy
from datetime import datetime,timedelta
from shutil import copy
from csv import reader as csv_reader
import cPickle as pickle
seperator='/'

##LMA_data_location='\\\\10.230.226.225\\LMA Data\\10microsecond'  ## not sure if this will work.  need 10.230.226.225
##final_data_location='D:\\lma\\lma_data_processing\\data'

final_data_location='/home/jaime/Documents/LMA/Analysis/rawAnalyzer/data'
drive_name='/media/lma-data'

##LMA_file_locations={'blanding_10':'blanding', 'blast_10':'blast', 'dupont_N_10':'dupont_N', 'dupont_S_10':'dupont_S', 'fl_dot_10':'fl_dot', 'golf_10':'golf','warehouse_10':'warehouse', 'wildlife_10':'wildlife' }
##
##LMA_letters={'blanding':'g', 'blast':'a', 'dupont_N':'d', 'dupont_S':'c', 'fl_dot':'e', 'golf':'b', 'warehouse':'f', 'wildlife':'h', 'Test':'h'}

##def timestamp_to_fname(site, timestamp, upper=False):
##    letter=LMA_letters[site]
##    if upper:
##        letter=letter.upper()
##    else:
##        letter=letter.lower()
##
##    return 'L'+letter+'_ICLRT_'+site+timestamp.strftime('_%y%m%d_%H%M%S')+'.dat'
##
def load_file_10MIN(timestamp):
    ##copies all data files for the timestamp
    ##returns start time of the file, and if is succssesfull
    succsses=False
    mins=timestamp.strftime('%M')
    mins=mins[0]+'0'
    timestamp_floor=timestamp.replace(minute=int(mins), second=0)

    date_folder=timestamp_floor.strftime('%y%m%d')
    if os.path.isdir(drive_name+seperator+date_folder): ##the date folder exists
        fname_ending='_'+date_folder+'_'+timestamp_floor.strftime('%H%M%S')+'.dat'
        fname=[f for f in os.listdir(drive_name+seperator+date_folder) if f.endswith(fname_ending)][0]
        if os.path.isfile(drive_name+seperator+date_folder+seperator+fname):
            copy(drive_name+seperator+date_folder+seperator+fname, final_data_location+seperator+fname)
            succsses=True
        else:
            print "    file not found:", drive_name+seperator+date_folder_seperator+fname
    else:
        print "    folder not found:", drive_name+seperator+date_folder

    return timestamp_floor, succsses



##    N_moved=0
##    for loc_file in LMA_file_locations:
##        if os.path.isdir(LMA_data_location+seperator+loc_file+seperator+date_folder): ##the date folder exists
##            ##wildlife stuff, sometimes we do not want to processes wildlife data
##            if LMA_file_locations[loc_file]=='wildlife' and not wildlife:
##                continue
##
##            if os.path.isfile(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor)):
##                N_moved+=1
##                copy(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor),  final_data_location+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor))
##                print "    copied:",LMA_file_locations[loc_file]
##
##            elif os.path.isfile(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor,upper=True)):
##                print "    cannot do 80 microsecond data"
####                N_moved+=1
####                copy(LMA_data_location+'\\'+loc_file+'\\'+date_folder+'\\'+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor),  final_data_location+'\\'+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor,upper=True))
##
##            elif LMA_file_locations[loc_file]=='wildlife' and  os.path.isfile(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname('Test',timestamp_floor)):
##                ## sometimes wildlife goes under the name 'Test'
##                N_moved+=1
##                copy(LMA_data_location+seperator+loc_file+seperator+date_folder+seperator+timestamp_to_fname('Test',timestamp_floor),  final_data_location+seperator+timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor))
##                print "    copied:",LMA_file_locations[loc_file]
##
##            else:
##                print "    Error: file not found:",timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor), 'or', timestamp_to_fname(LMA_file_locations[loc_file],timestamp_floor, upper=True)
##        else:
##            print "    folder not found:", LMA_data_location+seperator+loc_file+seperator+date_folder
##
##    return N_moved,timestamp_floor


def copy_all(fname,dt=None):
    if dt!=None:
        DT_TD=timedelta(seconds=dt)
    ten_min=timedelta(minutes=10)

    with open(fname+'.csv', 'rU') as fin:
        csv_file=csv_reader(fin)
        csv_file.next() ##read off header

        for line in csv_file:
            if len(line)==0:
                continue

            event_num=line[1]
            timestamp=datetime.strptime(line[0].split('.')[0], '%Y-%m-%d %H:%M:%S')
            if dt==None:
                DT_TD=timedelta(seconds=int(line[2]))

            print
            print "copying event", event_num
            present_time=timestamp-DT_TD
            while True:
                print "  start time:", present_time
                file_start,s=load_file_10MIN(present_time)
                if file_start+ten_min>=timestamp+DT_TD:
                    break
                present_time=file_start+ten_min


if __name__ == '__main__':
    wildlife=True
    copy_all('061114',None)
