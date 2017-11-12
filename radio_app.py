from flask import Flask, render_template, request, flash, url_for
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import SubmitField, SelectField
import os

stations =  [('http://pr320.pinguinradio.com', 'PINGUIN RADIO'),
            ('http://po192.pinguinradio.com', 'PINGUIN ON THE ROCKS'),
            ('http://pc192.pinguinradio.com', 'PINGUIN CLASSICS'),
            ('http://pu192.pinguinradio.com', 'PINGUIN PLUCHE')]

default_volume = -2400
default_volume_lvl = 5
min_volume_lvl = 1
max_volume_lvl = 15
default_timeout = 90

class MyForm(FlaskForm):
    volume = SelectField(label="Volume", choices=zip([str(x) for x in range(1,16)], range(1,16)), default=default_volume_lvl)
    station = SelectField(label="Station", choices=stations)
    play = SubmitField(label="Play")
    pause = SubmitField(label="Pause")
    stop = SubmitField(label="Stop")
    vol_up = SubmitField(label="Volume Up")
    vol_down = SubmitField(label="Volume Down")
    timeout = SelectField(label="Timeout [m]", choices=zip([str(x) for x in range(30,181,30)], range(30,181,30)), default=default_timeout)

application = Flask(__name__)
bootstrap = Bootstrap(application)
application.config['SECRET_KEY'] = 'well-secret-password'

with open('/home/pi/flask_projects/radio_ctrl/files/current_station.txt', 'r') as file:
    station = file.read().split(' : ')[1].strip()

with open('/home/pi/flask_projects/radio_ctrl/files/current_volume.txt', 'w') as file:
    file.write(str(default_volume_lvl))


os.system("rm -r files/cmd")
os.system("mkfifo files/cmd")
os.system("chmod 777 files/cmd")
os.system("pkill omxplayer")
os.system("timeout " + str(default_timeout) + "m" + \
            " omxplayer " + station + \
            " --vol " + str(default_volume) + \
            " -o hdmi " + \
            "< files/cmd &")
os.system("echo . > files/cmd")

@application.route('/', methods=['GET','POST'])
def index():
    form=MyForm()
    saved_title, saved_station = get_song_info()

    station_url = get_current_station()
    station_name = dict(stations).get(station_url)
    if station_name.lower() != saved_station.lower():
        saved_title = ''
                
    if form.validate_on_submit():

        if form.play.data:
        
            volume_lvl = form.volume.data
            volume = default_volume + (-5 + int(volume_lvl)) * 300
            save_volume_lvl(volume_lvl)

            station_url = form.station.data
            station_name = dict(stations).get(station_url)
            save_current_station(station_name, station_url)

            timeout = form.timeout.data

            os.system("pkill omxplayer")
            os.system("timeout " + timeout + "m" + \
                        " omxplayer " + station_url + \
                        " --vol " + str(volume) + \
                        " -o hdmi " + \
                        "< files/cmd &")
            os.system("echo . > files/cmd")
            
            flash("Now playing " + station_name)
        
        elif form.pause.data:
            os.system("echo -n p > files/cmd")
            flash("Paused/Resumed")
        
        elif form.stop.data:
            os.system("echo -n q > files/cmd")
            flash("Player stopped")
        
        elif form.vol_up.data:
            if int(form.volume.data) != max_volume_lvl:
                os.system("echo -n + > files/cmd")
                volume_lvl = int(form.volume.data) + 1
                save_volume_lvl(volume_lvl)
                flash("Volume increased")
            else:
                flash("Volume max level")
        
        elif form.vol_down.data:
            if int(form.volume.data) != min_volume_lvl:
                os.system("echo -n - > files/cmd")
                volume_lvl = int(form.volume.data) - 1
                save_volume_lvl(volume_lvl)
                flash("Volume decreased")
            else:
                flash("Volume min level")

    if form.errors:
        for error_field, error_message in form.errors.iteritems():
            flash("Field : {field}; error : {error}".format(field=error_field, error=error_message))

    form.volume.data = get_volume_lvl()
    form.station.data = get_current_station()

    return render_template('radio_index.html', title=saved_title, form=form)

def get_song_info():
    with open('/home/pi/flask_projects/radio_ctrl/files/omx_title.txt', 'r') as file:
        title = file.readline().split('(')[0].split('[')[0]
        station = file.readline().split('(')[0].split(',')[0].strip()
        return title, station

def save_current_station(station_name, station_url):
    with open('/home/pi/flask_projects/radio_ctrl/files/current_station.txt', 'w') as file:
        file.write(station_name + " : " + station_url)

def get_current_station():
    with open('/home/pi/flask_projects/radio_ctrl/files/current_station.txt', 'r') as file:
        station_url = file.read().split(' : ')[1].strip()
        return station_url

def save_volume_lvl(volume):
    with open('/home/pi/flask_projects/radio_ctrl/files/current_volume.txt', 'w') as file:
        file.write(str(volume))

def get_volume_lvl():
    with open('/home/pi/flask_projects/radio_ctrl/files/current_volume.txt', 'r') as file:
        volume = file.read()
        return volume

if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)

