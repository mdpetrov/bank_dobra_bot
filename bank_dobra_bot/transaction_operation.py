import pandas as pd
import json
import datetime
from bank_dobra_bot.log_operation import LogOperations
import os
from zoneinfo import ZoneInfo

class TransactionOperations(object):
    def __init__(self, config):
        self.config = config
        self.LO = LogOperations(config)
    
    def _transaction_sum(self, transaction_list):
        '''Calculate sum of all transactions in the list'''
        total_sum = 0
        for transaction in transaction_list:
            try:
                total_sum += int(transaction['sum'])
            except Exception as e:
                continue
        return total_sum
    
    def _get_transaction_file_path(self, chat):
        path = self.config.path
        file_dir = path['transaction_dir']
        file_name = f"{chat.username}.json"
        file_path = os.path.join(file_dir, file_name)
        return file_path
       
    def _update_transaction_list(self, id, fund, amount):
        transaction_to_add = {'id':id,
                              'timestamp':datetime.datetime.now(ZoneInfo('Europe/Moscow')).strftime('%Y-%h-%d %H:%M:%S'),
                              'fund':fund,
                              'sum':amount}
        return transaction_to_add
        
    def add_transaction(self, chat, amount, fund):
        '''Add transaction to transaction list'''
        LO = self.LO
        LO.write_log(chat, 'Trying to add a new transaction')
        if not amount.isdigit():
            LO.write_log(chat, 'Wrong transaction amount: not a number')
            return "Неверная сумма транзакции. Ничего не добавлено."
        elif amount <= 0:
            LO.write_log(chat, 'Wrong transaction amount: less or equal zero')
            return "Неверная сумма транзакции. Ничего не добавлено."
        amount = int(amount)


        file_path = self._get_transaction_file_path(chat=chat)
        if os.path.isfile(file_path):
            with open(file_path, mode='rt', encoding='utf-8') as con:
                transaction_list = json.load(con)
            if len(transaction_list) > 0:
                id = transaction_list[-1]['id'] + 1
            else:
                id = 1
            LO.write_log(chat, f'Transaction list exists with lenght {len(transaction_list)}')
            transaction_to_add = _update_transaction_list(id=id, amount=amount, fund=fund)
            transaction_list.append(transaction_to_add)
        else:
            id = 1
            transaction_to_add = _update_transaction_list(id=id, amount=amount, fund=fund)
            transaction_list = [transaction_to_add]
            LO.write_log(chat, 'Created new transaction list')
        with open(file_path, mode='wt', encoding='utf-8') as con:
            json.dump(transaction_list, con)
        LO.write_log(chat, 'Transaction list is saved')
        
        total_sum = self._transaction_sum(transaction_list)
        
        return f"Успешно добавлено {amount} рублей в фонд {fund}. Общая сумма {total_sum} рублей"
        
        
    def remove_last_transaction(self, chat):
        LO = self.LO
        LO.write_log(chat, 'Trying to remove the last transaction')
        file_path = self._get_transaction_file_path(chat=chat)
        
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
    
    def get_transaction_list(self, chat, limit=10):
        LO = self.LO
        LO.write_log(chat, f'Last {limit} transactions have been requested')
        file_path = self._get_transaction_file_path(chat=chat)
        if os.path.isfile(file_path):
            with open(file_path, mode='rt', encoding='utf-8') as con:
                transaction_list = json.load(con)
            if len(transaction_list) > 0:
                if len(transaction_list) <= limit:
                    transaction_list_return = transaction_list
                else:
                    transaction_list_return = transaction_list[:limit]
                transaction_str_return = [
                    f"{x['id']} -- {x['timestamp']} -- {x['fund']} -- {x['sum']}" 
                        for x in transaction_list_return
                 ]
                transaction_str_return.insert(0, '*id - Время - Фонд - Сумма*\n')
                LO.write_log(chat, f'Returning {len(transaction_str_return)} transactions')
                text = [f'Последние {len(transaction_str_return)} транзакций', "\n".join(transaction_str_return)]
                return '\n'.join(text)
            else:
                return "Ничего нет"
        else:
            return "Ничего нет"
    
    def get_transaction_stat(self, chat):
        LO = self.LO
        LO.write_log(chat, 'Transaction statistics has been requested')
        file_path = self._get_transaction_file_path(chat=chat)
        if not os.path.isfile(file_path):
            return "Ничего нет"
        
        with open(file_path, mode='rt', encoding='utf-8') as con:
            transaction_list = json.load(con)
        if len(transaction_list) == 0:
            return "Ничего нет"
        transaction_df = pd.DataFrame.from_dict(transaction_list)
        transaction_dg = transaction_df.groupby('fund')['sum'].sum().reset_index(drop=False)
        stat_print = [f"{r['fund']} - {r['sum']}" for r in transaction_dg.iterrows()]
        stat_print.insert(0, 'Статистика по фондам:')
        return '\n'.join(stat_print)
