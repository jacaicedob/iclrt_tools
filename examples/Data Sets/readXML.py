#!/usr/bin/env python

import xml.etree.ElementTree as ET

eventName = '1309'
xml_file = './UF%s.xml' % eventName

tree = ET.parse(xml_file)

root = tree.getroot()

day = root.find('date').find('day').text
month = root.find('date').find('month').text
year = root.find('date').find('year').text[-2:]

eventDate = '%s%s%s' % (month, day, year)
#####################
eventName = root.find('name').text
rs = int(root.find('return_stroke').text)

print("Event: %s" % eventName)
print("Date : %s" % eventDate)
print("RS   : #%d" % rs)
print()

data = {}

for scope in root.iter('scope'):
    name = scope.find('name').text
    brand = scope.find('type').text
    path = scope.find('path').text
    
    print("%s - %s (%s)" % (name, brand, path))
    
    scope_data = {}
    
    for measurement in scope.iter('measurement'):
        meas = {}
        
        meas['name'] = measurement.find('name').text
        meas['file'] = measurement.find('file').text
        meas['trace'] = int(measurement.find('trace').text)
        meas['cal_factor'] = float(measurement.find('cal_factor').text)
        meas['units'] = measurement.find('units').text
        meas['distance'] = float(measurement.find('distance').text)
        
        scope_data[meas['name']] = meas
        
    data.update(scope_data)
    
print(data.keys())
