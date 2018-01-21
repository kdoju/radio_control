#!/usr/bin/fish

set var (python /home/pi/flask_projects/radio_ctrl/test.py);
if math "$var != 0"
    /home/pi/flask_projects/radio_ctrl/restart.txt
end
