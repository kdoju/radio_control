from flask import Flask, render_template, request, flash, url_for
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import SubmitField, SelectField
import os, subprocess, PTN
import subtitles as subs

def get_titles():
    cmd_1 = ['find', '/mnt/HP_Vids', '-name', '*.mkv']
    cmd_2 = ['find', '/mnt/HP_Vids', '-name', '*.avi']
    cmd_3 = ['find', '/home/pi/Videos', '-name', '*.mkv']
    cmd_4 = ['find', '/home/pi/Videos', '-name', '*.avi']

    fpaths = subprocess.check_output(cmd_1, universal_newlines=True)
    fpaths = fpaths + subprocess.check_output(cmd_2, universal_newlines=True)
    fpaths = fpaths + subprocess.check_output(cmd_3, universal_newlines=True)
    fpaths = fpaths + subprocess.check_output(cmd_4, universal_newlines=True)

    fpaths = fpaths.replace(' ','\ ').replace('(', '\(').replace(')', '\)').split('\n')
    fpaths.sort()
    fpaths = list(filter(None, fpaths))
    
    titles = [PTN.parse(fpath.split('/')[-1]) for fpath in fpaths]

    for i in range(len(titles)):
        titles[i]['fpath'] = fpaths[i]

    titles_zip = zip([title['fpath'] for title in titles],
                    [(title['title'] if '/mnt/HP_Vids' in title['fpath'] else '[Pi] ' + title['title']).replace('\ ',' ').replace('\\','') \
                    + (' S' + (str(0) + str(title['season']) if title['season'] < 10 else str(title['season'])) if 'season' in title else '') \
                    + ('E' + (str(0) + str(title['episode']) if title['episode'] < 10 else str(title['episode'])) if 'episode' in title else '') \
                    for title in titles])
    
    return titles_zip

titles_zip = get_titles()

class MyForm(FlaskForm):
    titles = SelectField(label="Title", choices=titles_zip)
    sub_switch = SelectField(label="Download", choices=[('1','YES'),('0','NO')])
    language = SelectField(label="Lang", choices=[('eng','EN'),('pol','PL')])
    sub_no = SelectField(label="No.", choices=zip([str(x) for x in range(10)], range(1,11)))
    sub_size = SelectField(label="Size", choices=zip([str(x) for x in range(40,80,5)], range(40,80,5)), default=60)
    play = SubmitField(label="Play")
    resume = SubmitField(label="Resume")
    pause = SubmitField(label="Pause")
    stop = SubmitField(label="Stop")
    vol_up = SubmitField(label="Volume +")
    vol_down = SubmitField(label="Volume -")
    forward = SubmitField(label="+30s")
    backward = SubmitField(label="-30s")
    forward_2 = SubmitField(label="+10m")
    backward_2 = SubmitField(label="-10m")
    prev_chapter = SubmitField(label="Prev ch")
    next_chapter = SubmitField(label="Next ch")
    toggle_subs = SubmitField(label="Toggle subs")
    sub_delay_minus = SubmitField(label="- 250 ms")
    sub_delay_plus = SubmitField(label="+ 250 ms")

application = Flask(__name__)
bootstrap = Bootstrap(application)
application.config['SECRET_KEY'] = 'well-secret-password'


os.system("rm -r files/cmd")
os.system("mkfifo files/cmd")
os.system("chmod 777 files/cmd")
os.system("pkill omxplayer")

with open('files/video_state.txt', 'w') as file:
    file.write('stopped')

@application.route('/', methods=['GET','POST'])
def index():
    form=MyForm()
    title = ''

    if form.validate_on_submit():

        if form.play.data or form.resume.data:
            os.system("pkill omxplayer")

            path = form.titles.data
            title = dict(titles_zip).get(form.titles.data).replace('[Pi] ','')
            language = form.language.data
            sub_no = int(form.sub_no.data)
            sub_size = form.sub_size.data
            sub_switch = bool(int(form.sub_switch.data))
            if sub_switch:
                message = subs.get_subtitles(title, path, language, sub_no)
                flash(message)

            if form.play.data:
                os.system("omxplayer " + path + " --vol -900 --font-size " + sub_size + " -g < files/cmd &")
            elif form.resume.data:
                resume_time = get_resume_time(title)
                flash('Starting from: ' + resume_time)
                os.system("omxplayer " + path + " --vol -900 --font-size " + sub_size + " -g -l " + resume_time + " < files/cmd &")
            os.system("echo . > files/cmd")
            flash("Now playing " + title)
            with open('files/video_title.txt', 'w') as file:
                file.write(title)
            with open('files/video_state.txt', 'w') as file:
                file.write('playing')
        
        elif form.pause.data:
            if read_player_state() == 'playing':
                os.system('echo -n p > files/cmd')
                flash('Paused/Resumed')
            else:
                flash('Forbidden action')
        
        elif form.stop.data:
            if read_player_state() == 'playing':
                os.system("echo -n q > files/cmd")
                flash("Player stopped")
                with open('files/video_state.txt', 'w') as file:
                    file.write('stopped')
            else:
                flash('Forbidden action')
        
        elif form.vol_up.data:
            if read_player_state() == 'playing':
                os.system("echo -n + > files/cmd")
                flash("Volume increased")
            else:
                flash('Forbidden action')
        
        elif form.vol_down.data:
            if read_player_state() == 'playing':
                os.system("echo -n - > files/cmd")
                flash("Volume decreased")
            else:
                flash('Forbidden action')
        
        elif form.backward.data:
            if read_player_state() == 'playing':
                os.system("echo -n ^[[D > files/cmd")
                flash("Back 30 seconds")
            else:
                flash('Forbidden action')

        elif form.forward.data:
            if read_player_state() == 'playing':
                os.system("echo -n ^[[C > files/cmd")
                flash("Forward 30 seconds")
            else:
                flash('Forbidden action')

        elif form.backward_2.data:
            if read_player_state() == 'playing':
                os.system("echo -n ^[[B > files/cmd")
                flash("Back 10 minutes")
            else:
                flash('Forbidden action')

        elif form.forward_2.data:
            if read_player_state() == 'playing':
                os.system("echo -n ^[[A > files/cmd")
                flash("Forward 10 minutes")
            else:
                flash('Forbidden action')

        elif form.prev_chapter.data:
            if read_player_state() == 'playing':
                os.system("echo -n i > files/cmd")
                flash("Previous chapter")
            else:
                flash('Forbidden action')

        elif form.next_chapter.data:
            if read_player_state() == 'playing':
                os.system("echo -n o > files/cmd")
                flash("Next chapter")
            else:
                flash('Forbidden action')

        elif form.toggle_subs.data:
            if read_player_state() == 'playing':
                os.system("echo -n s > files/cmd")
                flash("Toggle subtitles")
            else:
                flash('Forbidden action')

        elif form.sub_delay_minus.data:
            if read_player_state() == 'playing':
                os.system("echo -n d > files/cmd")
                flash("Decrease subtitle delay (- 250 ms)")
            else:
                flash('Forbidden action')

        elif form.sub_delay_plus.data:
            if read_player_state() == 'playing':
                os.system("echo -n f > files/cmd")
                flash("Increase subtitle delay (+ 250 ms)")
            else:
                flash('Forbidden action')

    if form.errors:
        for error_field, error_message in form.errors.iteritems():
            flash("Field : {field}; error : {error}".format(field=error_field, error=error_message))

    return render_template('video_index.html', title=title, form=form)


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=5001)

def get_resume_time(title):
    with open('files/video_title.txt', 'r') as file:
        prev_title = file.readline()
    if title == prev_title:
        with open('omxplayer.log', 'r') as file:
            for line in reversed(file.readlines()):
                if line.find('DEBUG: Normal M:') > -1:
                    millis = line.split('DEBUG: Normal M:')[1].split('(')[0].strip()
                    # print "Millis: " + millis
                    hours = int(float(millis)/(60*60*1000000))
                    minutes = int(float(millis)/(60*1000000))-hours*60
                    seconds = int(float(millis)/1000000)-minutes*60-hours*60*60-10
                    resume_time = str(hours).zfill(2) + ':' + str(minutes).zfill(2) + ':' + str(seconds).zfill(2)
                    # print "Resume time: " + resume_time
                    return resume_time
    else:
        return '00:00:00'

def read_player_state():
    with open('files/video_state.txt', 'r') as file:
        state = file.read()
        return state
    