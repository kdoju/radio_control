import subprocess

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

with open('/home/pi/flask_projects/radio_ctrl/files/omx_title.txt', 'w') as file:
    file.writelines([title + '\n', station])
    
