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

logger = logging.getLogger(__name__)
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')

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

PO = ParamsOperations(config=config)
LO = LogOperations(config=config)
BO = BotOperations(bot=bot)
MO = MarkupOperations()
TO = TransactionOperations(config)

@bot.message_handler(commands=['start'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 10))
def get_message_start(message):
    local_params = PO.load_params(message.chat.id)
    start_text = '''Банк добра 😊
Список команд:'''
    # markup = quick_markup({
        # 'Добавить транзакцию': {'callback_data': 'add_transaction'},
        # 'Удалить последнюю транзакцию': {'callback_data': 'remove_last_transaction'}
    # })
    start_text += '''
/start - Приветственное сообщение
/add_transaction - Добавить транзакцию
/remove_last_transaction - Удалить последнюю транзакцию
/show_transaction_list - Вывести список последних транзакций
/show_statistics - Вывести статистику по фондам
'''
    BO.send_message(message.chat.id, text=start_text, params=local_params)
    PO.save_params(message.chat.id, local_params)

@bot.message_handler(commands=['add_transaction'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 600))
def get_message_add_transaction(message):
    local_params = PO.load_params(message.chat.id)
    message_text = 'Выберите фонд'
    fund_list = config.fund_list
    
    markup = MO.gen_markup_from_list(fund_list, callback_data_template='fund', columns=1)
    message = BO.send_message(text=message_text, chat_id=message.chat.id, reply_markup=markup, params=local_params)
    
    PO.save_params(message.chat.id, local_params)

@bot.message_handler(commands=['show_transaction_list'], chat_types=['private'], func=lambda m: (time.time() - m.date <= 600))
def get_message_show_transaction_list(message):
    local_params = PO.load_params(message.chat.id)
    message_text = TO.get_transaction_list(message.chat)
    BO.send_message(text=message_text, chat_id=message.chat.id, params=local_params)
    PO.save_params(message.chat.id, local_params)

@bot.message_handler(commands=['remove_last_transaction'], chat_types=['private'])
def get_message_remove_last_transaction(message):
    local_params = PO.load_params(message.chat.id)
    remove_last_transaction(message)
    
    PO.save_params(message.chat.id, local_params)
    
@bot.message_handler(commands=['show_statistics'], chat_types=['private'])
def get_message_show_statistics(message):
    local_params = PO.load_params(message.chat.id)
    message_text = TO.get_transaction_stat(message.chat)
    BO.send_message(text=message_text, chat_id=message.chat.id, params=local_params)
    
    PO.save_params(message.chat.id, local_params)


# @bot.callback_query_handler(func=lambda call: (call.data == 'remove_last_transaction') and (time.time() - call.message.date <= 600))
# def remove_last_transaction(call):
    # local_params = PO.load_params(call.message.chat.id)

    # message_text = TO.remove_last_transaction(call.message.chat)
    # message = BO.send_message(text=message_text, chat_id=call.message.chat.id, params=local_params)
    
    # bot.answer_callback_query(call.id)
    # PO.save_params(call.message.chat.id, local_params)

# @bot.callback_query_handler(func=lambda call: (call.data == 'add_transaction') and (time.time() - call.message.date <= 600))
# def add_transaction_choose_fund(call): 
    # local_params = PO.load_params(call.message.chat.id)
    # message_text = 'Выберите фонд'
    # fund_list = config.fund_list
    
    # markup = MO.gen_markup_from_list(fund_list, columns=1)
    # message = BO.edit_message_text(text=message_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    
    # bot.answer_callback_query(call.id)
    # PO.save_params(call.message.chat.id, local_params)

@bot.callback_query_handler(func=lambda call: (call.data[:5] == 'fund_') and (time.time() - call.message.date <= 60))
def add_transaction_enter_amount(call): 
    local_params = PO.load_params(call.message.chat.id)
    LO.write_log(call.message.chat, 'Fund chosen')
    fund_id = int(call.data[5:])
    fund_name = config.fund_list[fund_id]
    message_text = f'Выбран фонд {fund_name}. Введите сумму:'
    
    message = BO.send_message(text=message_text, chat_id=call.message.chat.id, params=local_params)
    bot.register_next_step_handler(call.message, add_transaction_save_transaction, fund=fund_name)
    bot.answer_callback_query(call.id)
    PO.save_params(call.message.chat.id, local_params)

def add_transaction_save_transaction(message, fund): 
    local_params = PO.load_params(message.chat.id)
    message_text = TO.add_transaction(chat=message.chat, amount=message.text, fund=fund)
    # message_text = f'Успешно добавлено {message.text} рублей в фонд {fund}'
    BO.send_message(message.chat.id, text=message_text, params=local_params)
    PO.save_params(message.chat.id, local_params)
    
def remove_last_transaction(message):
    local_params = PO.load_params(message.chat.id)
    last_transaction = TO.get_transaction_list(message.chat, limit=1)
    if last_transaction == 'Ничего нет':
        message_text = [last_transaction]
    else:
        message_text = ['Последняя транзакция:\n']
        message_text.append(last_transaction)
        message_text.append("\nУдалить последнюю транзакцию? (Да/Нет)")
        bot.register_next_step_handler(message, remove_last_transaction_confirm)
    message = BO.send_message(text='\n'.join(message_text), chat_id=message.chat.id, params=local_params)
    
    PO.save_params(message.chat.id, local_params)

def remove_last_transaction_confirm(message):
    local_params = PO.load_params(message.chat.id)
    if message.text.lower() == 'да':
        message_text = TO.remove_last_transaction(message.chat)
    else:
        message_text = 'Ничего не удалено'
    message = BO.send_message(text=message_text, chat_id=message.chat.id, params=local_params)
    
    PO.save_params(message.chat.id, local_params)

if __name__ == '__main__':
    while True:
        try:
            logger.info('Restart the bot')
            bot.polling(none_stop=True, interval=1) #обязательная для работы бота часть
        except Exception as e:
            logger.error('Error in execution')
            # LO.write_log(0, e)
            
            logging.error(e, exc_info=True)
            time.sleep(1*60) # 1 minute