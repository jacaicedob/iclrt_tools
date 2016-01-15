#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import all other modules
import datetime

import JaimePackages.field_mill.field_mill as fm

# Variables

dataDir = "/Volumes/OSX2/Users/jaime/Flash Summaries/081514/Field Mill Data"
outDir = "/Volumes/OSX2/Users/jaime/Flash Summaries/081514/Field Mill Data/out"

launchCodes = ['UF1453', 'UF1454', 'UF1455', 'UF1456', 'UF1457']
date = datetime.date(2014,8,15)
launchTimes = [datetime.datetime(2014,8,15,16,56,47),
               datetime.datetime(2014,8,15,17,4,14),
               datetime.datetime(2014,8,15,17,45,33),
               datetime.datetime(2014,8,15,17,46,32),
               datetime.datetime(2014,8,15,18,20,15)]

launchTimes = dict(zip(launchCodes, launchTimes))

for lc in launchCodes:
    test = fm.FieldMillDataold(dataDir, outDir, launchTimes[lc], lc)

    test.getLatex()
