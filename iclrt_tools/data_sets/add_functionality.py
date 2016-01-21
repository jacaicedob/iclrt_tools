#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import os
import pickle
import xml.etree.ElementTree as et
import numpy as np

# Import custom modules
import iclrt_tools.data_sets.waveforms as wave

# Remove the plots that were added to the Waveform objects
events ={'UF0920-3': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF0920_data_061809_rs3.p',
         'UF0925-1': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF0925_data_062909_rs1.p',
         'UF0925-6': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF0925_data_062909_rs6.p',
         'UF0929-1': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF0929_data_063009_rs1.p',
        'UF0929-5': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF0929_data_063009_rs5.p',
        'UF0932-1': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF0932_data_070709_rs1.p',
        'UF1309-1': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF1309_data_060913_rs1.p',
        'UF1333-1': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF1333_data_081713_rs1.p',
        'UF1426-1': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF1426_data_071414_rs1.p',
        'UF1442-1': '/home/jaime/Documents/ResearchTopics/Publications/Current Reflections/Data Sets/DataFiles/UF1442_data_080214_rs1.p'}

for key in sorted(events.keys()):
    print("Converting {}".format(key))
    out_file = events[key]  #[:-5] + events[key][-2:]
    out = {}
    data = pickle.load(open(events[key], 'rb'))

    for k in sorted(data.keys()):
        print("  {}".format(k))
        flash_name = data[k].flash_name
        date = data[k].date
        return_stroke = data[k].return_stroke
        if return_stroke == 0:
            return_stroke = 1

        measurement_name = data[k].measurement_name
        scope_name = data[k].scope_name
        scope_type = data[k].scope_type
        file_name = data[k].file_name
        trace_number = data[k].trace_number
        cal_factor = data[k].cal_factor
        units = data[k].units
        distance = data[k].distance
        t_start = data[k].t_start
        t_end = data[k].t_end
        ddata = data[k].data
        dataTime = data[k].dataTime

        w = wave.Waveform(flash_name, date, return_stroke,
                          measurement_name, scope_name, scope_type,
                          file_name, trace_number, cal_factor, units,
                          distance, t_start, t_end)
        w.set_data(ddata)

        if np.diff(data[k].dataTime)[0] < 1e-6:
            w.set_dataTime(dataTime)
        else:
            w.set_dataTime(dataTime*1e-6)

        out[k] = w

    pickle.dump(out, open(out_file, 'wb'))

sys.exit(1)
