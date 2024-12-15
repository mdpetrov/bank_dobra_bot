import pandas as pd
import json
import datetime
from bank_dobra_bot.log_operation import LogOperations
import os

class TransactionOperations(object):
    def __init__(self, config):
        self.config = config
        self.LO = LogOperations(config)
    

    def add_transaction(self, chat, amount, fund):
        path = self.config.path
        LO = self.LO
        LO.write_log(chat, 'Trying to add a new transaction')
        if not amount.isdigit():
            LO.write_log(chat, 'Wrong transaction amount')
            return "Неверная сумма транзакции. Попробуйте заново."
        amount = float(amount)
        file_dir = path['transaction_dir']
        file_name = f"{chat.username}.json"
        file_path = os.path.join(file_dir, file_name)
        
        id = 0 
        transaction_to_add = {'timestamp':datetime.datetime.now().strftime('%Y-%h-%d %H-%M-%S'),
                                     'id':id,
                                     'fund':fund,
                                     'sum':amount}
        if os.path.isfile(file_path):
            with open(file_path, mode='rt', encoding='utf-8') as con:
                transaction_list = json.load(con)
            if len(transaction_list) > 0:
                id = transaction_list[-1]['id'] + 1
            transaction_list.append(transaction_to_add)
            LO.write_log(chat, 'Transaction added')
        else:
            transaction_list = [transaction_to_add]
            LO.write_log(chat, 'Created new transaction list')
        with open(file_path, mode='wt', encoding='utf-8') as con:
            json.dump(transaction_list, con)
        LO.write_log(chat, 'Transaction list is saved')
        
        total_sum = self.transaction_sum(transaction_list)
        
        return f"Успешно добавлено {amount} рублей в фонд {fund}. Общая сумма {total_sum} рублей"
        
        
    def remove_last_transaction(self, chat):
        path = self.config.path
        LO = self.LO
        LO.write_log(chat, 'Trying to remove the last transaction')
        file_dir = path['transaction_dir']
        file_name = f"{chat.username}.json"
        file_path = os.path.join(file_dir, file_name)
        
        if os.path.isfile(file_path):
            with open(file_path, mode='rt', encoding='utf-8') as con:
                transaction_list = json.load(con)
            if len(transaction_list) > 0:
                last_transaction = transaction_list.pop()
                LO.write_log(chat, 'Transaction removed')

                with open(file_path, mode='wt', encoding='utf-8') as con:
                    json.dump(transaction_list, con)
                LO.write_log(chat, 'Transaction list is saved')
                return f"Последняя транзакция на сумму {last_transaction['sum']} удалена"
            else:
                return "Нечего удалять"
        else:
            return "Нечего удалять"
            
    def transaction_sum(self, transaction_list):
        total_sum = 0
        for transaction in transaction_list:
            try:
                total_sum += int(transaction['sum'])
            except Exception as e:
                continue
        return total_sum
