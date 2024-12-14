import pandas as pd
import json
import datetime
from bank_dobra_bot.log_operation import LogOperations


class TransactionOperations(object):
    def __init__(self, config):
        self.config = config
        self.LO = LogOperations(config)
    

    def add_transaction(self, chat, amount, fund):
        path = self.config.path
        LO = self.LO
        LO.write_log(chat.id, 'Trying to add a new transaction')
        file_dir = path['transaction_dir']
        file_name = f"{chat_id.username}.json"
        file_path = os.path.join(file_dir, file_name)
        
        id = transaction_list[-1]['id'] + 1
        transaction_to_add = {'timestamp':datetime.datetime.now().strftime('%Y-%h-%d %H-%M-%S'),
                                     'id':id,
                                     'fund':fund,
                                     'sum':amount}
        if os.path.isfile(file_path):
            with open(file_path, mode='rt', encoding='utf-8') as con:
                transaction_list = json.load(con)
            transaction_list.append()
            LO.write_log(chat.id, 'Transaction added')
        else:
            transaction_list = [transaction_to_add]
            LO.write_log(chat.id, 'Created new transaction list')
        with open(file_path, mode='wt', encoding='utf-8') as con:
            json.dump(transaction_list, con)
        LO.write_log(chat.id, 'Transaction list is saved')
                
