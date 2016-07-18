#!/usr/bin/env python

"""
Converts the exported files from the xlma software into .csv files.
"""

import sys
import gzip

if len(sys.argv) > 1:
    files = sys.argv[1:]

    for file in files:
        lines = ''

        if 'gz' in file[-3:]:
            # Read and convert all lines
            with gzip.open(file, 'rt') as f:
                print("Reading File: {0}".format(file))

                while not '*** data ***' in f.readline():
                    pass

                lines += 'time(UT-sec-of-day),lat,lon,alt(m),reduced-chi^2,' \
                         '#-of-stations-contributed,P(dBW),flash-number,' \
                         'charge,mask\n'

                for line in f:
                    words = line.split()
                    lines += ','.join(words) + '\n'

            # Write all lines
            out = file[:-6] + 'csv'
            with open(out, 'w') as f:
                print("Writing File: {0}".format(out))
                f.write(lines)

        else:
            # Read and convert all lines
            with open(file, 'rt') as f:
                print("Reading File: {0}".format(file))

                while not '*** data ***' in f.readline():
                    pass

                lines += 'time(UT-sec-of-day),lat,lon,alt(m),reduced-chi^2,' \
                         '#-of-stations-contributed,P(dBW),flash-number,' \
                         'charge,mask\n'

                for line in f:
                    words = line.split()
                    lines += ','.join(words) + '\n'

            # Write all lines
            out = file[:-3] + 'csv'
            with open(out, 'w') as f:
                print("Writing File: {0}".format(out))
                f.write(lines)

        print('Done \n\n')
