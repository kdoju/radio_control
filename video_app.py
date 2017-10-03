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
                    [(title['title'] if '/mnt/HP_Vids' in title['fpath'] else '[Pi] ' + title['title']).replace('\ ',' ') \
                    + (' S' + (str(0) + str(title['season']) if title['season'] < 10 else str(title['season'])) if 'season' in title else '') \
                    + ('E' + (str(0) + str(title['episode']) if title['episode'] < 10 else str(title['episode'])) if 'episode' in title else '') \
                    for title in titles])
                    # + (' (' + str(title['year']) + ')' if 'year' in title else '') for title in titles])
    
    return titles_zip

titles_zip = get_titles()

class MyForm(FlaskForm):
    titles = SelectField(label="Title", choices=titles_zip)
    language = SelectField(label="Subs", choices=[('eng','EN'),('pol','PL')])
    sub_no = SelectField(label="Sub.No.", choices=zip([str(x) for x in range(10)], range(1,11)))
    sub_size = SelectField(label="Size", choices=zip([str(x) for x in range(40,80,5)], range(40,80,5)), default=60)
    play = SubmitField(label="Play")
    pause = SubmitField(label="Pause")
    stop = SubmitField(label="Stop")
    vol_up = SubmitField(label="Volume +")
    vol_down = SubmitField(label="Volume -")
    forward = SubmitField(label="+30s")
    backward = SubmitField(label="-30s")
    forward_2 = SubmitField(label="+10m")
    backward_2 = SubmitField(label="-10m")
    info = SubmitField(label="Info")
    prev_chapter = SubmitField(label="Previous")
    next_chapter = SubmitField(label="Next")
    toggle_subs = SubmitField(label="Toggle subtitles")
    sub_delay_minus = SubmitField(label="- 250 ms")
    sub_delay_plus = SubmitField(label="+ 250 ms")

application = Flask(__name__)
bootstrap = Bootstrap(application)
application.config['SECRET_KEY'] = 'well-secret-password'


os.system("rm -r files/cmd")
os.system("mkfifo files/cmd")
os.system("chmod 777 files/cmd")
os.system("pkill omxplayer")

@application.route('/', methods=['GET','POST'])
def index():
    form=MyForm()
    title = ''

    if form.validate_on_submit():

        if form.play.data:
            os.system("pkill omxplayer")

            path = form.titles.data
            title = dict(titles_zip).get(form.titles.data).replace('[Pi] ','')
            language = form.language.data
            sub_no = int(form.sub_no.data)
            sub_size = form.sub_size.data
            message = subs.get_subtitles(title, path, language, sub_no)

            os.system("omxplayer " + path + " --vol 0 --font-size " + sub_size + " < files/cmd &")
            os.system("echo . > files/cmd")
            flash(message)
            flash("Now playing " + title)
        
        elif form.pause.data:
            os.system("echo -n p > files/cmd")
            flash("Paused/Resumed")
        
        elif form.stop.data:
            os.system("echo -n q > files/cmd")
            flash("Player stopped")
        
        elif form.vol_up.data:
            os.system("echo -n + > files/cmd")
            flash("Volume increased")
        
        elif form.vol_down.data:
            os.system("echo -n - > files/cmd")
            flash("Volume decreased")
        
        elif form.backward.data:
            os.system("echo -n ^[[D > files/cmd")
            flash("Back 30 seconds")

        elif form.forward.data:
            os.system("echo -n ^[[C > files/cmd")
            flash("Forward 30 seconds")

        elif form.backward_2.data:
            os.system("echo -n ^[[B > files/cmd")
            flash("Back 10 minutes")

        elif form.forward_2.data:
            os.system("echo -n ^[[A > files/cmd")
            flash("Forward 10 minutes")

        elif form.info.data:
            os.system("echo -n z > files/cmd")
            flash("Showing movie info")

        elif form.prev_chapter.data:
            os.system("echo -n i > files/cmd")
            flash("Previous chapter")

        elif form.next_chapter.data:
            os.system("echo -n o > files/cmd")
            flash("Next chapter")

        elif form.toggle_subs.data:
            os.system("echo -n s > files/cmd")
            flash("Toggle subtitles")

        elif form.sub_delay_minus.data:
            os.system("echo -n d > files/cmd")
            flash("Decrease subtitle delay (- 250 ms)")

        elif form.sub_delay_plus.data:
            os.system("echo -n f > files/cmd")
            flash("Increase subtitle delay (+ 250 ms)")

    if form.errors:
        for error_field, error_message in form.errors.iteritems():
            flash("Field : {field}; error : {error}".format(field=error_field, error=error_message))

    return render_template('video_index.html', title=title, form=form)


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True, port=5001)

