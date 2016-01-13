#!/usr/bin/env python

from datetime import datetime,timedelta
import csv
import os
import subprocess
import sys
import shutil

lma_data_processing='/home/jaime/Documents/LMA/Analysis/rawAnalyzer'

csv.register_dialect('read', delimiter=' ', skipinitialspace=True)

def process_CSV(fname,dt=None,max_stations=None):
    ## assume that DT does not change the date

    if dt!=None:
        DT=dt
        DT_TD=timedelta(seconds=dt)
    os.chdir(lma_data_processing)
    with open('/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/CSV/'+fname+'.txt', 'rU') as fin:
        csv_file = csv.reader(fin, dialect='read')
        # csv_file.next() ##read off header

        for line in csv_file:
            if len(line)==0:
                continue
            elif line[0].split()[0][0] == "#":
                continue

            event_num = line[2]

            dd = '{0} {1}'.format(line[0], line[1])
            timestamp = datetime.strptime(dd.split('.')[0], '%Y-%m-%d %H:%M:%S')

            if dt==None:
                DT = int(line[3])
                DT_TD=timedelta(seconds=DT)

            print "Processing event:",event_num
            set_location_file(timestamp)
            
            if max_stations:
                analyze_timespan(timestamp-DT_TD, 2*DT, max_stations)
            else:
                analyze_timespan(timestamp-DT_TD, 2*DT, 5)

def set_location_file(timestamp):
    if timestamp<datetime(year=2013, month=06, day=04):
        fname='iclrt_original.loc'
    elif timestamp<datetime(year=2013, month=06, day=27):
        fname='iclrt_temp1.loc'
    elif timestamp<datetime(year=2013, month=8, day=1):
        fname='iclrt_temp1_fdot.loc'
    elif timestamp<datetime(year=2014, month=7, day=23):
        fname='iclrt_temp2.loc'
    else:
        fname='iclrt_temp3.loc'

    shutil.copyfile(fname, './iclrt.loc')

def analyze_timespan(start_timestamp, DT, max_stations=None):
    ## analyzes LMA data over a period of time
    
    if max_stations > 5:
        stations = 6
    else:
        stations = max_stations

    analyze_times=[]
    initial=start_timestamp
    ten_min=timedelta(minutes=10)
    TD_DT=timedelta(seconds=DT)
    while initial<start_timestamp+TD_DT:
        file_start_minutes=int(initial.minute/10)
        file_start_timestamp=datetime(year=initial.year, month=initial.month, day=initial.day, hour=initial.hour, minute=file_start_minutes, second=0)
        end_file=min([initial+ten_min,start_timestamp+TD_DT])
        analyze_times.append([initial, end_file])
        initial=end_file

    for start,stop in analyze_times:
        DT=(stop-start).total_seconds()
        analyze_single_file(start,DT, stations)


def analyze_single_file(start_timestamp, DT, stations=None):
    ##this function will analyize lma data if the start and end are in the same file
    ##note: error checking is not great at making sure that the start and stop are in the same file
    data_file_minute=start_timestamp.strftime('%M')[0]
    file_hour_minute=start_timestamp.strftime('%H')+data_file_minute+'0'

        # Write configuration file
    if DT<600:
        line = ".\/lma_analysis -d %s -t %s -s %d -l iclrt -x 5.0 -y 500.0 -n %d -v -a -q -b -o output  ../PythonAnalyzer/data/L*%s_%s*dat\n" % (start_timestamp.strftime('%Y%m%d'), start_timestamp.strftime('%H%M%S'), DT, stations , start_timestamp.strftime('%m%d'), file_hour_minute)
        ## error checking
        seconds=int(start_timestamp.strftime('%M')[1])*60 + int(start_timestamp.strftime('%S'))+DT
        if seconds>600:
            print "Event may slip off end of file"

    elif DT==600:
        line = ".\/lma_analysis -d %s -t %s -s %d -l iclrt -x 5.0 -y 500.0 -n %d -v -a -q -b -o output  ../PythonAnalyzer/data/L*%s_%s*dat\n" % (start_timestamp.strftime('%Y%m%d'), file_hour_minute+'00', 600, stations, start_timestamp.strftime('%m%d'), file_hour_minute)

    else:
        print "DT must be equal to, or less than, 600 seconds"
        return

    fh = open('./analyze', "w")
    fh.write(line)
    fh.close()

    # Command Output log
    log = '/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/log' + "/%s-%s-out-analyze.log" % (start_timestamp.strftime('%y%m%d'), start_timestamp.strftime('%H%M%S'))
    alog = open(log, "w")

    # Command Error log
    err = '/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/log' + "/%s-%s-error-analyze.log" % (start_timestamp.strftime('%y%m%d'), start_timestamp.strftime('%H%M%S'))
    aerrlog = open(err, "w")

    # Run command
    command = "sh analyze"
    proc = subprocess.Popen(command, bufsize=-1,shell=True, stderr=aerrlog, stdout=alog)

    if proc.poll() is None:
        sys.stdout.write("  - Running analyze... ")
        sys.stdout.flush()

    return_code = proc.wait()
    alog.close()
    aerrlog.close()

    if return_code != 0:
        sys.stdout.write("Error! Check '%s' for details\n" % err)
        return

    sys.stdout.write("done!\n")


if __name__ == '__main__':
    process_CSV('130614')  # Filename (CSV), delta_t

