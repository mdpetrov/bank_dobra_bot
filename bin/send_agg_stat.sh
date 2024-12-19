#!/bin/bash

prog_path=/dev/prog/bot/bank_dobra_bot
cd $prog_path
source $prog_path/venv/bin/activate

python3 agg_user_stat.py
