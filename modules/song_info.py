import subprocess
from datetime import datetime
from time import sleep

curr_ts = datetime.now()
prev_ts = datetime.now()

def get_song_info():
    title = False
    station = False
    with open('/home/pi/flask_projects/radio_ctrl/files/current_station.txt', 'r') as file:
        url = file.read().split(' : ')[1]
    cmd = 'omxplayer -i ' + url + ' > /home/pi/flask_projects/radio_ctrl/files/omx_output.txt 2>&1'
    subprocess.call(cmd, shell=True)
    with open('/home/pi/flask_projects/radio_ctrl/files/omx_output.txt', 'r') as file:
        for line in file:
            if line.lstrip()[:11] == 'StreamTitle':
                title = line.split(':')[1].strip()
            if line.lstrip()[:8] == 'icy-name':
                station = line.split(':')[1].strip()
    if title and station:
        with open('/home/pi/flask_projects/radio_ctrl/files/omx_title.txt', 'w') as file:
            file.writelines([title + '\n', station])
    
while True:
    get_song_info()
    sleep(2)
    # curr_ts = datetime.now()
    # delta = curr_ts - prev_ts
    # if delta.seconds >= 15:
    #     get_song_info()
    #     prev_ts = curr_ts

