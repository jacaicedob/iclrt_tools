#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code/iclrt_tools')

# Import other modules
import iclrt_tools.nldn.xlma_nldn_parser as nldn


if len(sys.argv) < 3:
    print("Error!\nUsage:")
    print("./nldn_parser.py inputFile outputFile")
    sys.exit(1)
    
else:
    fileIn = sys.argv[1]
    fileOut = sys.argv[2]

nldn.parse_nldn(fileIn, fileOut)