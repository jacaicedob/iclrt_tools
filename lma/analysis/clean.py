#!/usr/bin/env python

import os

input_file_directory='/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/data'
output_file_directory='/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/output'
log_file_directory='/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/log'
loc_file_location='/home/jaime/Documents/LMA/Analysis/rawAnalyzer/iclrt.loc'

def main():
	## clean the input files
    print("Cleaning the input files...")

    input_files = [ f for f in os.listdir(input_file_directory) if
                    os.path.isfile(os.path.join(input_file_directory,f)) and
                    f.endswith('.dat') and f[0]=='L']

    for i_f in input_files:
        os.remove(input_file_directory+'/'+i_f)

    ## clean output files
    print "Clean output data"
    output_files = [ f for f in os.listdir(output_file_directory) if os.path.isfile(os.path.join(output_file_directory,f)) and (f.endswith('.gz') or f[-4:]=='.log' or f[-4:]=='.dat') and f[0:6]=='LYLOUT']
    for o_f in output_files:
        os.remove(output_file_directory+'/'+o_f)

    print "clean logs"
    log_files = [ f for f in os.listdir(log_file_directory) if os.path.isfile(os.path.join(log_file_directory,f)) and f.endswith('analyze.log')]
    for l_f in log_files:
        os.remove(log_file_directory+'/'+l_f)

    print "delete iclrt.loc"
    if os.path.isfile(loc_file_location):
        os.remove(loc_file_location)


if __name__ == '__main__':
	main()
    
