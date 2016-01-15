#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import JaimePackages.nldn.nldn_parser as nldn


if len(sys.argv) < 3:
    print("Error!\nUsage:")
    print("./nldn_parser.py inputFile outputFile")
    sys.exit(1)
    
else:
    fileIn = sys.argv[1]
    fileOut = sys.argv[2]

nldn.parse_nldn(fileIn, fileOut)