#!/usr/bin/env python

"""
This code is a Python port of the MATLAB code written by Terry Ngin to process the field mill data files.

It is a combination of both CampSciWrite and CampSciPoint.
"""

import os
import datetime
import csv
import numpy as np


class FieldMillData(object):
    """
    This newer class (01/07/2016) was made to represent field mill
    data and allow for ease of manipulation and plotting.
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.read_data()

    def read_data(self):
        times = []
        Es = []

        with open(self.file_name) as csv_file:
            reader = csv.reader(csv_file)
            i = 0
            for row in reader:
                if i < 3:
                    if i == 0:
                        self.station = row[1]
                        self.type = row[-1]

                    i += 1
                    continue
                else:
                    if row[0] == '':
                        continue
                    times.append(row[0])
                    Es.append(row[3])

        self.t = []
        self.E = np.array(Es)

        for t in times:
            try:
                self.t.append(datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f'))
            except ValueError:
                self.t.append(datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S'))
                pass


class FieldMillDataold(object):
    """
    This class was used to get the field mill data for all stations
    when writing the Flash Summaries.
    """
    def __init__(self, dataDir, outDir, launchTime, dataSetName='Test'):
        if isinstance(launchTime, datetime.datetime):
            self.launchTime = launchTime
        else:
            raise TypeError
        
        self.dataDir = dataDir
        self.outDir = outDir
        self.dataSetName = dataSetName
        
        self.getRawDataFiles()
        
    def __str__(self):
        data, average = self.getAverage()
        
        s = ""
        s += "-" * 50
        s += "\nSummary of data set '%s':\n" % (self.dataSetName)
        s += "-" * 50
        s += "\n  Station   =>   Field Value\n  "
        s += "-" * 26
        s += "\n"
        
        for d in data:
            s += "    %s => %0.1f V/m\n" % (d, data[d])
        
        s += "\n  Average: %0.1f V/m" % (average)
        
        return s
        
    def getLatex(self):
        data, average = self.getAverage()
        
        s = ""
        s += "-" * 50
        s += "\nLaTeX output of data set '%s':\n" % (self.dataSetName)
        s += "-" * 50
        s += "\n\n"
        
        keys = [d for d in data]
        
        for i in range(len(data)/2):
            s += "%s & %0.1f & %s & %0.1f \\\\\n" % (keys[2*i], data[keys[2*i]]*1E-3, keys[2*i+1], data[keys[2*i+1]]*1E-3)
            s += "\\hline\n\n"
            
        s += "Average: %0.1f" % (average*1E-3)
        print(s)
        
    def get2minData(self):
        ### Directory structure setup
        # Make sure the directory for the data set exists
        
        dir2min = self.outDir + "/" + self.dataSetName + "/2min"

        try:
            os.makedirs(dir2min)
    
        except os.error as e:
            print("Directories for '%s' already exist, so not created" %
                  self.dataSetName)
    
        # Process the data
        
        codeDir = "%s/%s/" % (self.outDir, self.dataSetName)
    
        for rf in self.raw_files:
            print("  Parsing %s" % rf)
        
            station = rf.split('_')[0]
    
            if 'Office' in station:
                station = "OT"
            elif 'Launch' in station:
                station = "LC"
        
            inputFile = "%s/%s" % (self.dataDir, rf)
            outputFile2min = "%s/%s_%s_%s_2min.dat" % (codeDir + "2min", \
                                                       station, \
                                                       date.isoformat(), \
                                                       self.dataSetName)        
        
            startTime2min = "%s" % (self.launchTime - \
                                       datetime.timedelta(0,60))
        
            self.getDataInterval(inputFile, outputFile2min, startTime2min ,120)
            
    def get30sData(self):
         ### Directory structure setup
        # Make sure the directory for the data set exists
        
        dir30s = self.outDir + "/" + self.dataSetName + "/30s"

        try:
            os.makedirs(dir30s)
    
        except os.error as e:
            print("Directories for '%s' already exist, so not created" %
                  self.dataSetName)
    
        # Process the data
        
        codeDir = "%s/%s/" % (self.outDir, self.dataSetName)
    
        for rf in self.raw_files:
            print("  Parsing %s" % rf)
        
            station = rf.split('_')[0]
    
            if 'Office' in station:
                station = "OT"
            elif 'Launch' in station:
                station = "LC"
        
            inputFile = "%s/%s" % (self.dataDir, rf)
            outputFile30s = "%s/%s_%s_%s_30s.dat" % (codeDir + "30s", \
                                                     station, \
                                                     date.isoformat(), \
                                                     self.dataSetName)
        
            startTime30s = "%s" % (self.launchTime - \
                                       datetime.timedelta(0,15))
        
            self.getDataInterval(inputFile, outputFile30s, startTime30s,30)    
    
    def getAverage(self):
        results = self.getLaunchTimeData()
        sum = 0
    
        for r in results:
            sum += results[r]
        
        average = round((sum / len(results))/100)*100
        
        return results, average
    
    def getDataPoint(self, inputFile, pointDateTime, quiet=False):
        """"
        This is a rewrite of CampSciPoint. It gets the field mill value at a 
        particular point in time.
        """
    
        try:
            with open(inputFile, 'r') as f:
                # Get the header
                header = ""
                data = ""
                for x in range(4):
                    header += f.readline()
            
                flag = False
            
                while not(flag):
                
                    try:
                        line = f.readline()
                    
                    except EOFError:
                        flag = True
                        found = False
                
                    if line != '':
                        words = line.split(',')
                
                        date_time = words[0]
                        sample_number = words[1]
                        e_field = words[3]
                
                        if pointDateTime in date_time:
                            flag = True
                            found = True  
                    else:
                        flag = True
                        found = False             
            
                if found:
                    if not(quiet):
                        print("    Found %s on %s" %
                              (pointDateTime, inputFile))
                    
                    data = line
                    
                else:
                    if not(quiet):
                        print("    Did not find %s on %s" % (pointDateTime,
                                                             inputFile))

            return header, data
        
        except IOError as e:
            print(str(e))
    
    def getDataInterval(self, inputFile, outputFile, startTime, duration, quiet=False):
        """
        This is a rewrite of CampSciWrie. It gets the field mill data for a 
        period of time centered around startTime.
        """
    
        dataLength = 5*duration + 1  # Five samples for one second, 
                                     # plus time zero.
        found = False
        
        try:
            with open(inputFile, 'r') as f:
                # Get the header
                with open(outputFile, 'w') as ff:
                    for x in range(4):
                        ff.write(f.readline())
            
                flag = False
            
                while not(flag):
                
                    try:
                        line = f.readline()
                    
                    except EOFError:
                        flag = True
                        found = False
                
                    if line != '':
                        words = line.split(',')
                
                        date_time = words[0]
                        sample_number = words[1]
                        e_field = words[3]
                
                        if startTime in date_time:
                            flag = True
                            found = True  
                    else:
                        flag = True
                        found = False             
            
                if found:
                    if not(quiet):
                        print("    Found %s on %s" % (startTime, inputFile))
                    data = line
                
                    for i in range(dataLength-1):
                        data += f.readline()
                    
                    with open(outputFile, 'a') as ff:
                        ff.write(data)    
                    
                else:
                    if not(quiet):
                        print("    Did not find %s on %s" % (startTime,
                                                             inputFile))
        
        except IOError as e:
            print(str(e))
    
    def getLaunchTimeData(self, quiet=True):
        values = {}
        
        for rf in self.raw_files:
            station = rf.split('_')[0]
         
            if 'Office' in station:
                station = "OT"
            elif 'Launch' in station:
                station = "LC"
            
            inputFile = "%s/%s" % (self.dataDir, rf)
            
            pointDateTime = "%s"  % (self.launchTime)
                                     
            header, data = self.getDataPoint(inputFile, pointDateTime, quiet)
            
            if data != "":
                values[station] = round(float(data.split(',')[3])/100)*100
        
        return values
    
    def getRawDataFiles(self):
        self.raw_files = [rf for rf in os.listdir(self.dataDir) if '.dat' in \
                          rf]
