#!/usr/bin/env python

# Add personal packages directory to path
import sys
import os

# Import other modules
# import iclrt_tools.data_sets.data_sets_non_oo as ds
import iclrt_tools.data_sets.data_sets as ds


def usage():
    s =  """
Usage:

    ./generateDataSet.py [action] [event] [params]
    
    Event formats:
        UF1308
        1308
    
    Available actions:
        get   --> acquire data
        reget --> acquire data rewriting file
        plot  --> plot data
        
    get Params:
        RS number (i.e. 1)
        measurement (i.e. E_12F)
        
        Examples:
            Get all RSs and measurements from xml file:
                ./generateDataSet.py get 1308
                
            Get a specific RS from xml file:
                ./generateDataSet.py get 1308 3
            
            Get a specific measurement from a specific RS:
                ./generateDataSet.py get 1308 3 E_12F
        
    reget Params:
        RS number (i.e. 1)
        measurement (i.e. E_12F)
        
        Examples:
            Get all RSs and measurements from xml file:
                ./generateDataSet.py reget 1308
                
            Get a specifi RS from xml file:
                ./generateDataSet.py reget 1308 3
            
            Get a specific measurement from a specific RS:
                ./generateDataSet.py reget 1308 3 E_12F

    plot Params:
        RS number (i.e. 1)
        measurement (i.e. E_12F)
        duration (in us)
        
        Examples:
            Plot all RSs and measurements:
                ./generateDataSet.py plot 1308
                
            Plot all RSs and measurements with specific duration:
                ./generateDataSet.py plot 1308 all all 50
                
            Plot a specifi RS:
                ./generateDataSet.py plot 1308 3
            
            Plot a specifi RS with specific duration:
                ./generateDataSet.py plot 1308 3 all 50
            
            Plot a specific measurement from a specific RS:
                ./generateDataSet.py plot 1308 3 E_12F 
                  
            Plot a specific measurement from a specific RS with specific duration:
                ./generateDataSet.py plot 1308 3 E_12F 50
    """
    
    print(s)


def main():
    os.chdir('/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/')
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    else:
        eventName = sys.argv[2]
        if "uf" in eventName.lower():
            xml_file = './XML/%s.xml' % eventName
        else:
            xml_file = './XML/UF%s.xml' % eventName

        dataSet = ds.DataSet(xml_file)

    if "reget" in sys.argv[1].lower():
        
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = 'all'
            
        if len(sys.argv) > 4 and sys.argv[4]:
            meass = sys.argv[4]
        else:
            meass = 'all'
            
        dataSet.get_data_set(rs=rs, meass=meass)
    
    elif "get" in sys.argv[1].lower():
        if sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = 'all'
            
        dataSet.get_data_set(rs=rs)
    
    elif "plotnorm" in sys.argv[1].lower():
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = -1
            
        if len(sys.argv) > 4 and sys.argv[4]:
            meass = sys.argv[4]
        else:
            meass = 'all'
            
        if len(sys.argv) > 5 and sys.argv[5]:
            lim = sys.argv[5]
        else:
            lim = 20
            
        if len(sys.argv) > 6 and sys.argv[6]:
            window = int(sys.argv[6])
        else:
            window = 1.0
            
        dataSet.plot_data_set(rs=rs, meass=meass, lim=lim, window=window,
                              norm=True)
        
    elif "plot" in sys.argv[1].lower():
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = -1
            
        if len(sys.argv) > 4 and sys.argv[4]:
            meass = sys.argv[4]
        else:
            meass = 'all'
            
        if len(sys.argv) > 5 and sys.argv[5]:
            lim = sys.argv[5]
        else:
            lim = 20
            
        if len(sys.argv) > 6 and sys.argv[6]:
            window = int(sys.argv[6])
        else:
            window = 1.0
            
        dataSet.plot_data_set(rs=rs, meass=meass, lim=lim, window=window)
    
    elif "rise" in sys.argv[1].lower():
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = -1
            
        if len(sys.argv) > 4 and sys.argv[4]:
            meass = sys.argv[4]
        else:
            meass = 'all'
    
        dataSet.calc_rise(rs=rs, meass=meass)

    elif "pulse" in sys.argv[1].lower():
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = -1

        if len(sys.argv) > 4 and sys.argv[4]:
            meass = sys.argv[4]
        else:
            meass = 'all'

        dataSet.calc_dE_pulse(rs=rs, meass=meass)

    elif sys.argv[1].lower() == "dip":
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = -1
            
        if len(sys.argv) > 4 and sys.argv[4]:
            meass = sys.argv[4]
        else:
            meass = 'all'
    
        if len(sys.argv) > 5 and sys.argv[5]:
            window = float(sys.argv[5])
        else:
            window = 1.0
    
        dataSet.calc_dip(rs=rs, meass=meass)
        
    elif sys.argv[1].lower() == "diptime":
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = -1
            
        if len(sys.argv) > 4 and sys.argv[4]:
            meass = sys.argv[4]
        else:
            meass = 'all'

        if len(sys.argv) > 5 and sys.argv[5]:
            lim = sys.argv[5]
        else:
            lim = 20

        if len(sys.argv) > 6 and sys.argv[6]:
            window = int(sys.argv[6])
        else:
            window = 1.0
    
        dataSet.calc_dip_time(rs=rs, meass=meass, window=window)
        
    elif "keys" in sys.argv[1].lower():
        if len(sys.argv) > 3 and sys.argv[3]:
            rs = sys.argv[3]
        else:
            rs = -1
        
        dataSet.print_keys(rs=rs)

if __name__ == "__main__":
    main()
