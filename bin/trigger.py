from work_materials.globals import *
from libs.trigger import *


def add_trigger(bot, update):
    mes = update.message
    request = "SELECT * FROM admins WHERE user_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row == None and update.message.from_user.id not in get_admin_ids(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка. Доступ только у админов')
    else:
        request = "SELECT trigger_out FROM triggers WHERE trigger_in = %s AND (chat_id = %s OR chat_id = 0)"
        cursor.execute(request, (mes.text.lower()[13:], mes.chat_id))
        row = cursor.fetchone()
        print(row)
        if row != None:
            bot.send_message(chat_id=update.message.chat_id, text='Триггер уже существует')
        else:
            if update.message.reply_to_message == None:
                bot.send_message(chat_id=update.message.chat_id, text='Сообщение должно быть ответом на триггер')
            else:
                new = Trigger
                new.add_trigger(new, mes, False)
                bot.send_message(chat_id=update.message.chat_id, text='Триггер успешно добавлен!')


def add_global_trigger(bot, update):
    mes = update.message
    request = "SELECT trigger_out FROM triggers WHERE trigger_in = %s AND chat_id = 0"
    cursor.execute(request, (mes.text.lower()[20:], mes.chat_id))
    row = cursor.fetchone()
    print(row)
    if row != None:
        bot.send_message(chat_id=update.message.chat_id, text='Триггер уже существует')
    else:
        if update.message.reply_to_message == None:
            bot.send_message(chat_id=update.message.chat_id, text='Сообщение должно быть ответом на триггер')
        else:
            new = Trigger
            new.add_trigger(new, mes, True)
            bot.send_message(chat_id=update.message.chat_id, text='Триггер успешно добален!')

def remove_trigger(bot, update):
    mes = update.message
    request = "SELECT * FROM admins WHERE user_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row == None and update.message.from_user.id not in get_admin_ids(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка. Доступ только у админов')
    else:
        request = "SELECT chat_id, type FROM triggers WHERE trigger_in = %s AND (chat_id = %s OR chat_id = 0)"
        cursor.execute(request, (mes.text[16:], mes.chat_id))
        row = cursor.fetchone()
        if row == None:
            response = 'Ошибка. Триггер не найден'
            bot.send_message(chat_id=update.message.chat_id, text=response)
        else:
            if row[0] == 0 and mes.from_user.id != 231900398:
                bot.send_message(chat_id=update.message.chat_id, text='Этот триггер глобальный. Удалить его может только @Cactiw')
                return
            request = "DELETE FROM triggers WHERE trigger_in = %s AND (chat_id = %s OR chat_id = 0)"
            cursor.execute(request, (mes.text[16:], mes.chat_id))
            conn.commit()
            bot.send_message(chat_id=update.message.chat_id, text='Триггер успешно удалён')
            cache_full()
