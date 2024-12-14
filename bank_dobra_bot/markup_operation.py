from telebot import types 

class MarkupOperations(object):
    def __init__(self):
        pass

    def gen_markup_from_list(self, markup_name_list, columns=2):
        callback_data = [f'fund_{i}' for i,x in enumerate(markup_name_list)]

        l = len(callback_data)
        markup_arr = []
        row_arr = []
        for i in range(l):
            btn = types.InlineKeyboardButton(markup_name_list[i], callback_data=callback_data[i])
            row_arr.append(btn)
            if (len(row_arr) >= columns) or (i == l - 1):
                markup_arr.append(row_arr)
                row_arr = []
        # markup_arr.append([types.InlineKeyboardButton('Главное меню', callback_data='main')])
        # print(markup_arr)
        markup_arr = types.InlineKeyboardMarkup(markup_arr)
        return markup_arr