#!/usr/bin/env python

"""
Converts the exported files from the xlma software into .csv files.
"""

import sys

if len(sys.argv) > 1:
    files = sys.argv[1:]
    print(files)
    for file in files:
        lines = ''

        # Read and convert all lines
        with open(file, 'r') as f:
            print("Reading File: {0}".format(file))
            lines += f.readline()
            for line in f:
                words = line.split()
                lines += ','.join(words) + '\n'

        # Write all lines
        out = file[:-3] + 'csv'
        with open(out, 'w') as f:
            print("Writing File: {0}".format(out))
            f.write(lines)

        print('Done \n\n')
