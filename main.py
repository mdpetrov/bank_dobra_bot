import telebot
from telebot import types 
from telebot.util import quick_markup
import random
import datetime
import time
import json
import os
import numpy as np
import pandas as pd
import re
import logging

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Custom packages

from bank_dobra_bot.config import config
from bank_dobra_bot.params_operation import ParamsOperations
from bank_dobra_bot.log_operation import LogOperations
from bank_dobra_bot.bot_operation import BotOperations
from bank_dobra_bot.markup_operation import MarkupOperations

path = config.path

# Open bot
with open(path['token'], 'rt', encoding='utf8') as fp:
    token = fp.read()
    
bot = telebot.TeleBot(token, threaded=False)

PO = ParamsOperations(config=config)
LO = LogOperations(config=config)
BO = BotOperations(bot=bot)
MO = MarkupOperations()

@bot.message_handler(commands=['start'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 10))
def get_message_start(message):
    local_params = PO.load_params(message.chat.id)
    # BO.send_message(message.chat.id, text='ДАУБИ БОТ', params=local_params)
    start_text = '''Банк добра 😊
Выберите команду'''
    markup = quick_markup({
        'Добавить транзакцию': {'callback_data': 'add_transaction'},
        # 'Сделать рандом': {'callback_data': 'make_random'}
        # 'Загрузить фильмы': {'callback_data': 'load_movies'}
    })
    BO.send_message(message.chat.id, text=start_text, params=local_params,reply_markup=markup)
    PO.save_params(message.chat.id, local_params)


@bot.callback_query_handler(func=lambda call: (call.data == 'add_transaction') and (time.time() - call.message.date <= 60))
def add_transaction(call): 
    local_params = PO.load_params(call.message.chat.id)
    message_text = 'Выберите фонд'
    fund_list = config.fund_list
    
    markup = MO.gen_markup_from_list(fund_list, columns=1)
    message = BO.edit_message_text(text=message_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    
    bot.answer_callback_query(call.id)
    PO.save_params(message.chat.id, local_params)
    
    
if __name__ == '__main__':
    while True:
        try:
            LO.write_log(0, 'Restart the bot')
            bot.polling(none_stop=True, interval=1) #обязательная для работы бота часть
        except Exception as e:
            LO.write_log(0, 'Error in execution')
            # LO.write_log(0, e)
            logging.basicConfig(level=logging.DEBUG)
            logging.error(e, exc_info=True)
            time.sleep(1*60) # 1 minute
            logging.basicConfig(level=logging.INFO)