#!/usr/bin/env python

# Add personal packages directory to path
import sys
sys.path.append('/home/jaime/Documents/Python Code')

# Import other modules
import os
import pickle
import xml.etree.ElementTree as et

# Import custom modules
import iclrt_tools.data_sets.waveforms as wvf

parent = '/home/jaime/Documents/Python Code/Data Sets'
data_files = '/home/jaime/Documents/Python Code/Data Sets/DataFiles'

lst = os.listdir(data_files)
files = [data_files + '/' + l for l in lst if '.p' in l]

for f in files:
    old_data = pickle.load(open(f, 'rb'))
    print('Opened file: {0}'.format(f))

    data = {}
    e = f[-24:-18]
    rs = f[-3:-2]

    xml_file = parent + '/XML/{e}.xml'.format(e=e)

    root = et.parse(xml_file)

    day = root.find('date').find('day').text
    month = root.find('date').find('month').text
    year = root.find('date').find('year').text[-2:]

    eventDate = '%s%s%s' % (month, day, year)
    eventName = root.find('name').text

    for rss in root.iter('return_stroke'):
        r_s = int(rss.find('number').text)

        if r_s != int(rs):
            continue

        print('  Processing RS: {0}'.format(r_s))

        for scope in rss.find('data').iter('scope'):
            scope_data = {}
            scope_name = scope.find('name').text
            scope_type = scope.find('type').text
            scope_path = scope.find('path').text

            print('    Processing scope: {0}'.format(scope_name))

            for meas in scope.iter('measurement'):
                measurement_name = meas.find('name').text

                if measurement_name not in old_data.keys():
                    continue

                measurement_file = meas.find('file').text
                file_name = '{0}/{1}'.format(scope_path,
                                             measurement_file)
                trace_number = int(meas.find('trace').text)
                cal_factor = float(meas.find('cal_factor').text)
                units = meas.find('units').text
                distance = float(meas.find('distance').text)
                t_start = float(meas.find('t_start').text)
                t_end = float(meas.find('t_end').text)

                print("      Processing '{0}'".format(measurement_name))

                measurement = wvf.Waveform(flash_name=eventName,
                                           event_date=eventDate,
                                           return_stroke=r_s,
                                           measurement_name=measurement_name,
                                           scope_name=scope_name,
                                           scope_type=scope_type,
                                           file_name=file_name,
                                           trace_number=trace_number,
                                           cal_factor=cal_factor,
                                           units=units, distance=distance,
                                           t_start=t_start, t_end=t_end)

                scope_data[measurement_name] = measurement

            data.update(scope_data)

        for key in data:
            print("    Getting data for '{0}'".format(key))
            data[key].set_data(old_data[key]['data'])
            data[key].set_time(old_data[key]['time'])
            # data[key].set_plot()

    new_file = '{0}_oo{1}'.format(f[:-2], f[-2:])
    print('Saving the data to: {0}'.format(new_file))
    pickle.dump(data, open(new_file, 'wb'))

sys.exit(1)

# Remove the plots that were added to the Waveform objects
events ={'UF0920-3': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF0920_data_061809_rs3.p',
         'UF0925-1': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF0925_data_062909_rs1.p',
         'UF0925-6': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF0925_data_062909_rs6.p',
         'UF0929-1': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF0929_data_063009_rs1.p',
        'UF0929-5': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF0929_data_063009_rs5.p',
        'UF0932-1': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF0932_data_070709_rs1.p',
        'UF1309-1': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF1309_data_060913_rs1.p',
        'UF1333-1': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF1333_data_081713_rs1.p',
        'UF1426-1': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF1426_data_071414_rs1.p',
        'UF1442-1': '/home/jaime/Documents/Python Code/Data Sets/DataFiles/UF1442_data_080214_rs1.p'}

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

    pickle.dump(out, open(out_file,'wb'))

sys.exit(1)
