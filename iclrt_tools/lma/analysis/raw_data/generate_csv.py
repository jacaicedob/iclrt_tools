#!/usr/bin/env python

import datetime

path = '/home/jaime/Documents/LMA/Analysis/PythonAnalyzer/CSV/'
file_name = path + 'hello.txt'

start = '04/02/2016 09:00:00.0'
end = '04/02/2016 13:00:00.0'

t_start = datetime.datetime.strptime(start, '%m/%d/%Y %H:%M:%S.%f')
t_end = datetime.datetime.strptime(end, '%m/%d/%Y %H:%M:%S.%f')
t_diff = t_end - t_start

t = t_start + t_diff/2
s = datetime.datetime.strftime(t, '%Y-%m-%d %H:%M:%S')
s += ' 0 {0}'.format(int((t_diff/2).total_seconds()))

print(s)

header = '# Format:\n# timestamp event dt\n\n# Event\n'

with open(file_name, 'w') as f:
    f.write(header)
    f.write(s)

