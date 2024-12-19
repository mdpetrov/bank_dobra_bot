import telebot
from telebot import types
from telebot.util import quick_markup
import random
import datetime
import time
import json
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(asctime)s. %(levelname)s %(module)s - %(funcName)s: %(message)s')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Custom packages

from bank_dobra_bot.config import config
from bank_dobra_bot.params_operation import ParamsOperations
from bank_dobra_bot.log_operation import LogOperations
from bank_dobra_bot.bot_operation import BotOperations
from bank_dobra_bot.markup_operation import MarkupOperations
from bank_dobra_bot.transaction_operation import TransactionOperations

path = config.path

# Open bot
with open(path['token'], 'rt', encoding='utf8') as fp:
    token = fp.read()

bot = telebot.TeleBot(token, threaded=False)

res = {}
for f in listdir(path['transaction_dir']):
    if not isfile(join(path['transaction_dir'], f)):
        continue
    file_name = f[f.rfind('/') + 1:]
    left = file_name.rfind('_')
    right = file_name.rfind('.')
    user_id = int(file_name[left + 1:right])
    user_name = file_name[:left]
    with open(join(path['transaction_dir'], f), 'r', encoding='utf8') as fp:
        user_stat = json.load(fp)
    user_stat_df = pd.DataFrame(user_stat)
    if len(user_stat_df) > 0:
        res[user_name] = user_stat_df


res_df = pd.DataFrame(res)
dg = res_df.groupby('fund')['sum'].sum()

stat_print =  [f"{fund} - {sum}" for fund,sum in dg.to_dict().items()]

bot.send_message(chat_id=159783, text=stat_print)
