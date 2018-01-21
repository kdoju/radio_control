#!/usr/bin/python

import datetime

with open('/home/pi/flask_projects/radio_ctrl/omxplayer.log') as log:
    for line in reversed(log.readlines()):
        omx_time = line.split()[0]
#        print omx_time
        break

now = datetime.datetime.now()
hour = now.hour
min = now.minute
second = now.second
curr_time = str(hour).zfill(2) + ':' + str(min).zfill(2) + ':' + str(second).zfill(2)
#print curr_time

prs_curr_time = datetime.datetime.strptime(curr_time, '%H:%M:%S')
# print 'current time: ' + str(prs_curr_time)

prs_omx_time = datetime.datetime.strptime(omx_time, '%H:%M:%S')
# print 'omx time: ' + str(prs_omx_time)

if int(str(prs_curr_time - prs_omx_time).split(':')[2]) == 0 or \
 int(str(prs_curr_time - prs_omx_time).split(':')[1]) == 0:
    print 0
else:
    print 1
