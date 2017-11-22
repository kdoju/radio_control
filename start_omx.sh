#!/usr/bin/fish

set var (python test.py);
if math "$var != 0"
    restart.txt
end
