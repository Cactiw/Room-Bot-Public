import time
from work_materials.globals import *
from psycopg2 import ProgrammingError

def todo(bot, update):
    if update.message.reply_to_message is None:
        return
    if update.message.reply_to_message.text is None:
        return
    priority = 5
    data = update.message.reply_to_message.text
    request = "insert into todo(priority, data, date_created) values ('{0}', '{1}', '{2}') returning id".format(priority, data, time.strftime('%Y-%m-%d %H:%M:%S'))
    cursor.execute(request)
    conn.commit()
    try:
        row = cursor.fetchone()
    except ProgrammingError:
        pass
    bot.send_message(chat_id = update.message.chat_id, text = "Успешно добавлено.\nИзменить приоритет: /todo_change_priority_{0}".format(row[0]))

def todo_list(bot, update):
    mes = update.message
    response = "Список дел, которые нужно сделать:\n\n"
    request = "select id, priority, data, date_created, completed, date_completed from todo"
    request += " where completed = '0'" if mes.text.partition("@")[0].find("full") == -1 else ""
    cursor.execute(request)
    row = cursor.fetchone()
    while row is not None:
        response_new = "{0}\n    Создано: {1}\n".format(row[2], row[3])
        response_new += "<b>    Выполнено:</b> {0}\n\n".format(row[5]) if row[4] else "<b>  Не выполнено:</b> /complete_todo_{0}\n\n".format(row[0])


        if len(response + response_new) >= 4096:  # Превышение лимита длины сообщения
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def complete_todo(bot, update):
    id = update.message.text.split("_")[2].partition("@")[0]
    request = "select id from todo where id = '{0}'".format(id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text="Не найдено. Проверьте синтаксис")
        return
    request = "update todo set completed = 1, date_completed = '{0}' where id = '{1}'".format(time.strftime('%Y-%m-%d %H:%M:%S'), id)
    cursor.execute(request)
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text="Успешно выполнено. Поздравляем!", parse_mode='HTML')
