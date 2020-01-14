#!/bin/bash

tmux new -s "remote" -d
tmux send-keys -t "remote" "cd /src/3bot && uwsgi --socket 0.0.0.0:5000 --protocol=http -w app:app" C-m
