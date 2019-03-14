from work_materials.globals import *
import time

def pr(bot, update):
    mes = update.message
    #if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id = -1001330929174)):
        #return

    request = "SELECT * FROM users WHERE user_id = %s"
    cursor.execute(request, (mes.text.split('_')[1],))
    row = cursor.fetchone()
    if row != None:
        response = row[1] + "<b>" + row[4] + '</b>\nБоец замка ' + row[1] + '\n'
        if int(row[12]):
            request = "SELECT * FROM dspam_users WHERE user_id = %s"
            cursor.execute(request, (row[0],))
            dspam_row = cursor.fetchone()
            if row is not None:
                response += "\nПозывной: <b>" + str(dspam_row[3]) + "</b>\n"
                request = "SELECT rank_name, rank_unique FROM ranks WHERE rank_id = %s"
                cursor_2.execute(request, (dspam_row[4],))
                rank = cursor_2.fetchone()
                response += "Звание: <b>"
                if rank[1]:
                    response += ranks_specials[rank[1]]
                response += rank[0] + "</b>\nОписание звания: /rank_{0}\n".format(str(dspam_row[4]))
                if (mes.from_user.id == 231900398) or (mes.from_user.id in get_admin_ids(bot, chat_id=-1001330929174)):
                    response += "Сменить звание: /set_rank {0}".format(dspam_row[0]) + " {номер звания}\n"
                response += "Репутация: <b>" + str(dspam_row[6]) + "</b>\n"
                # response += "Ваши достижения: " + str(dspam_row[5]) + " *now in development*\n"
                response += "\n"
        # response = response + 'Номер профиля: ' + str(row[0]) + '\n'
        #if row[1] == '🔒':
            #bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            #return
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
    else:
        request = "SELECT * FROM dspam_users WHERE telegram_id = %s"
        cursor.execute(request, (mes.from_user.id,))
        dspam_row = cursor.fetchone()
        if row is not None:
            response = "Позывной: <b>" + str(dspam_row[3]) + "</b>\n"
            response += "Звание: <b>" + str(dspam_row[4]) + "</b>\n"
            # response += "Ваши достижения: " + str(dspam_row[5]) + " *now in development*\n"
            response += "\n"
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            return

        response = 'Профиль отсутствует'
        bot.send_message(chat_id=update.message.chat_id, text=response)


def rank_list(bot, update, args):
    mes = update.message
    if not args:
        arg = 0
    else:
        arg = args[0]
    request = "SELECT * FROM ranks WHERE rank_unique = %s"
    cursor.execute(request, (arg,))
    row = cursor.fetchone()
    if row is None:
        response = 'Званий ещё нет. Добавьте!'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    response = "Список званий:"
    while row:
        response_new = "\n"
        if row[3] == 1:
            response_new += "🎗"
        elif row[3] == 2:
            response_new += "🎖"
        response_new += "<b>" + row[1] + "</b>"
        response_new += "\nПодробнее: /rank_" + str(row[0]) + "\n______________________________\n"
        if len(response + response_new) >= 4096:
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()

    if (mes.from_user.id == 231900398) or (mes.from_user.id in get_admin_ids(bot, chat_id=-1001330929174)):
        response += "\nДобавить звание: /add_rank"


    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def add_rank(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "INSERT INTO ranks(rank_name, rank_data) VALUES('Новое звание', '')"
    cursor.execute(request)
    conn.commit()

    request = "SELECT rank_id FROM ranks ORDER BY rank_id DESC LIMIT 1"
    cursor.execute(request)
    row = cursor.fetchone()
    response = "Звание успешно добавлено:\nНажмите, чтобы настроить: /edit_rank_{0}".format(row[0])
    bot.send_message(chat_id=update.message.chat_id, text=response)



def rank(bot, update):
    mes = update.message
    request = "SELECT * FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split("_")[1],))
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    response = "<b>"
    if row[3]:
        response += ranks_specials[row[3]]
    response += row[1] + "</b>:\n"
    response += row[2] + "\n"
    if row[3] == 1:
        response += "<b>\n🎗Уникальное звание" + "</b>\n"
    if row[3] == 2:
        response += "<b>\n🎖Наградное звание" + "</b>\n"
    if (mes.from_user.id == 231900398) or (mes.from_user.id in get_admin_ids(bot, chat_id=-1001330929174)):
        response += "\nРедактировать звание: /edit_rank_{0}".format(mes.text.split("_")[1])
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def set_rank(bot, update, args):
    mes = update.message
    if mes.from_user.id != 231900398 and mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174):
        return
    if not args:
        response = 'Неверный синтаксис'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "SELECT rank_name FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (args[1],))
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не найдено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "SELECT * FROM dspam_users WHERE user_id = %s"
    cursor.execute(request, (args[0],))
    row = cursor.fetchone()
    if row is None:
        response = 'Профиль не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE dspam_users SET rank = %s WHERE user_id = %s"
    cursor.execute(request, (args[1], args[0]))
    conn.commit()

    response = 'Звание успешно изменено!'
    bot.send_message(chat_id=update.message.chat_id, text=response)
    response_to_id = row[1]
    request = "SELECT username FROM dspam_users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    username = row[0]
    request = "SELECT rank_name FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (args[1],))
    row = cursor.fetchone()
    rank = row[0]
    try:
        bot.send_message(chat_id=response_to_id, text="Ваше звание изменено <b>{0}</b> на <b>{1}</b>.\nСмотрите изменения в /profile".format(username, rank), parse_mode='HTML')
    except TelegramError:
        bot.send_message(chat_id=-1001197381190, text="Оповещение '{0}' не удалось".format(row[3]))


def edit_rank(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT * FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split("_")[2],))
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    rank_id = row[0]
    response = "Редактирование звания <b>{0}</b>:\n".format(row[1])
    response += "Изменить название: /r_set_name {0} ".format(rank_id) + "{новое имя}\n"
    response += "Изменить описание: /r_set_description {0} ".format(rank_id) + "{новое описание}\n"
    if row[3] == 1:
        response += "\n🎗Отменить уникальность: /r_set_unique_{0}_".format(rank_id) + "0\n"
        response += "🎖Сделать наградным: /r_set_unique_{0}_".format(rank_id) + "2\n"
    elif row[3] == 2:
        response += "\n🎖Сделать звание обычным: /r_set_unique_{0}_".format(rank_id) + "0\n"
        response += "🎗Сделать уникальным: /r_set_unique_{0}_".format(rank_id) + "1\n"
    else:
        response += "\n🎗Сделать уникальным: /r_set_unique_{0}_".format(rank_id) + "1\n"
        response += "🎖Сделать наградным: /r_set_unique_{0}_".format(rank_id) + "2\n"

    response += "\n\nУдалить звание: /del_rank_{0}".format(rank_id)
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def del_rank(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT rank_id FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split("_")[2],))
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE dspam_users SET rank = 3 WHERE rank = %s"
    cursor.execute(request, (mes.text.split("_")[2],))
    conn.commit()
    request = "DELETE FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split("_")[2],))
    conn.commit()
    response = 'Звание успешно удалено\nВсе пользователи, имевшие это звание, получили стандартное.'
    bot.send_message(chat_id=update.message.chat_id, text=response)




def r_set_name(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT rank_id FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split(" ")[1],))
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    offset = mes.text.find(" ") + 1
    from_position = mes.text[offset:].find(" ")
    request = "UPDATE ranks SET rank_name = %s WHERE rank_id = %s"
    cursor.execute(request, (mes.text[from_position + offset + 1:], mes.text.split(" ")[1]))
    conn.commit()
    response = 'Успешно изменено'
    bot.send_message(chat_id=update.message.chat_id, text=response)


def r_set_description(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT rank_id FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split(" ")[1],))
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    offset = mes.text.find(" ") + 1
    from_position = mes.text[offset:].find(" ")
    request = "UPDATE ranks SET rank_data = %s WHERE rank_id = %s"
    cursor.execute(request, (mes.text[from_position + offset + 1:], mes.text.split(" ")[1]))
    conn.commit()
    response = 'Успешно изменено'
    bot.send_message(chat_id=update.message.chat_id, text=response)

def r_set_unique(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT rank_id FROM ranks WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split("_")[3],))
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE ranks SET rank_unique = %s WHERE rank_id = %s"
    cursor.execute(request, (mes.text.split("_")[4], mes.text.split("_")[3]))
    conn.commit()
    response = 'Успешно изменено'
    bot.send_message(chat_id=update.message.chat_id, text=response)



def reg(bot, update):
    mes = update.message
    request = "SELECT * FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row is None: #Добавляем челика не из чв
        #response = 'Профиль отсутствует, пожалуйста, пришлите мне /hero'
        #bot.send_message(chat_id=update.message.chat_id, text=response)
        #return
        request = "INSERT INTO users(user_castle, telegram_id, telegram_username, username, last_update, dspam_user) VALUES ('🔒', %s, %s, %s, %s, '1')"
        cursor.execute(request, (mes.from_user.id, mes.from_user.username, mes.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S'),))
        conn.commit()
        request = "SELECT user_id FROM users WHERE telegram_id = %s"
        cursor.execute(request, (mes.from_user.id,))
        row = cursor.fetchone()
        request = "INSERT INTO dspam_users(user_id, telegram_id, username) VALUES (%s, %s, %s)"
        cursor.execute(request, (int(row[0]), mes.from_user.id, mes.from_user.username))
        conn.commit()
        response = 'Регистрация успешна'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    if int(row[12]) == 1:
        response = 'Вы уже зарегистрированы'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE users SET dspam_user = '1' where telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    conn.commit()
    request = "INSERT INTO dspam_users(user_id, telegram_id, username) VALUES (%s, %s, %s)"
    cursor.execute(request, (int(row[0]), mes.from_user.id, row[4]))
    conn.commit()
    response = 'Регистрация успешна'
    bot.send_message(chat_id=update.message.chat_id, text=response)


def set_call_sign(bot, update, args):
    mes = update.message
    if not args:
        response = 'Неверный синтаксис'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "SELECT * FROM dspam_users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        response = 'Профиль не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return

    request = "INSERT INTO requests(request_type, user_id, data) VALUES ('1', %s, %s)"
    cursor.execute(request, (int(row[0]), mes.text[15:]))
    conn.commit()
    response = 'Запрос на изменение позывного опубликован'
    bot.send_message(chat_id=update.message.chat_id, text=response)
    response = "Входящий запрос от <b>" + row[2] + "</b>.\nПодробнее: /requests"
    #update.message.from_user.id not in get_admin_ids(bot, update.message.chat_id)
    bot.send_message(chat_id=231900398, text=response, parse_mode='HTML')
    for id in get_admin_ids(bot, -1001330929174):
        try:
            bot.send_message(chat_id = id, text = response, parse_mode = 'HTML')
        except TelegramError:
            pass

def force_call_sign(bot, update, args):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id = -1001330929174)):
        return
    if not args:
        response = 'Неверный синтаксис'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "SELECT * FROM dspam_users WHERE user_id = %s"
    cursor.execute(request, (args[0],))
    row = cursor.fetchone()
    if row is None:
        response = 'Профиль не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    from_position = mes.text[17:].find(" ") + 17 + 1
    request = "UPDATE dspam_users SET call_sign = %s WHERE user_id = %s"
    cursor.execute(request, (mes.text[from_position:].upper(), row[0]))
    conn.commit()

    response = 'Позывной успешно изменён!'
    bot.send_message(chat_id=update.message.chat_id, text=response)
    response_to_id = row[1]
    request = "SELECT call_sign, username FROM dspam_users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    sign = row[0]
    if row[0] == "Тебя никто не знает (установи позывной)":
        sign = row[1]
    try:
        bot.send_message(chat_id=response_to_id, text="Ваш позывной изменён <b>{0}</b> на <b>{1}</b>.\nСмотрите изменения в /profile".format(sign, mes.text[from_position:]), parse_mode='HTML')
    except TelegramError:
        bot.send_message(chat_id=-1001197381190, text="Оповещение '{0}' не удалось".format(row[3]))



def requests(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id = -1001330929174)):
        return
    request = "SELECT * FROM requests"
    cursor.execute(request)
    row = cursor.fetchone()
    response = ""
    while row:
        if int(row[1]) == 1:
            request = "SELECT telegram_username, username FROM users WHERE user_id = %s"
            cursor_2.execute(request, (row[2],))
            names = cursor_2.fetchone()
            response_new = ""
            response_new += "\nЗапрос на изменение позывного от <b>" + names[1] + "</b>"
            if names[0]:
                response_new += " @" + names[0] + ":\n"
            else:
                response_new += ":\n"
            response_new += "<b>" + row[3].upper() + "</b>\n"
            response_new += "Подтвердить изменение: /confirm_" + str(row[0]) + "\nОтклонить: /reject_" + str(row[0]) + "\n"
            response_new += "Подробнее о профиле: /pr_" + str(row[2]) + "\n______________________________\n"
            if len(response + response_new) >= 4096:
                bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
                response = ""
            response += response_new
        row = cursor.fetchone()
    if response == "":
        response = "Запросов нет. Хорошая работа!"
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def confirm(bot, update):
    mes = update.message
    if mes.from_user.id != 231900398 and mes.from_user.id not in get_admin_ids(bot, chat_id = -1001330929174):
        return
    request_id = int(mes.text.split('_')[1])
    request = "SELECT * FROM requests WHERE request_id = %s"
    cursor.execute(request, (request_id,))
    row = cursor.fetchone()
    if row is None:
        response = 'Запрос не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    if row[1] == 1:
        request = "UPDATE dspam_users SET call_sign = %s WHERE user_id = %s"
        cursor.execute(request, (row[3].upper(), row[2]))
        conn.commit()
        request = "DELETE FROM requests WHERE request_id = %s"
        cursor.execute(request, (request_id,))
        conn.commit()
        response = 'Запрос успешно принят. Хорошего дня!\nПросмотреть остальные запросы: /requests'
        bot.send_message(chat_id = update.message.chat_id, text=response)
        request = "SELECT telegram_id FROM users WHERE user_id = %s"
        cursor.execute(request, (row[2],))
        response_to_id = cursor.fetchone()
        try:
            bot.send_message(chat_id = response_to_id[0], text = "Ваш запрос на изменение позывного на <b>{0}</b> одобрен.\nСмотрите изменения в /profile".format(row[3]), parse_mode='HTML')
        except TelegramError:
            bot.send_message(chat_id = -1001197381190, text = "Оповещение '{0}' не удалось".format(row[3]))

def reject(bot, update):
    mes = update.message
    if mes.from_user.id != 231900398 and mes.from_user.id not in get_admin_ids(bot, chat_id = -1001330929174):
        return
    request_id = int(mes.text.split('_')[1])
    request = "SELECT * FROM requests WHERE request_id = %s"
    cursor.execute(request, (request_id,))
    row = cursor.fetchone()
    if row is None:
        response = 'Запрос не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    if row[1] == 1:
        request = "DELETE FROM requests WHERE request_id = %s"
        cursor.execute(request, (request_id,))
        conn.commit()
        response = 'Запрос отклонён. Хорошего дня!\nПросмотреть остальные запросы: /requests'
        bot.send_message(chat_id=update.message.chat_id, text=response)

        request = "SELECT telegram_id FROM users WHERE user_id = %s"
        cursor.execute(request, (row[2],))
        response_to_id = cursor.fetchone()
        try:
            bot.send_message(chat_id=response_to_id[0], text="Ваш запрос на изменение позывного на <b>{0}</b> отклонён.\nУзнайте, почему у @Cactiw!".format(row[3]), parse_mode='HTML')
        except TelegramError:
            bot.send_message(chat_id=-1001197381190, text="Оповещение '{0}' не удалось".format(row[3]))

# TODO сделать логирование реквестов


def dspam_list(bot, update):
    mes = update.message
    #if mes.from_user.id != 231900398 and mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174):
        #return
    request = "SELECT * FROM dspam_users"
    cursor.execute(request)
    row = cursor.fetchone()
    response = "Список зарегистрированных пользователей ДСПАМ:\n"
    while row:
        request = "SELECT telegram_username, username FROM users WHERE user_id = %s"
        cursor_2.execute(request, (row[0],))
        names = cursor_2.fetchone()
        response_new = ""
        response_new += "\n<b>" + names[1] + "</b>"

        if names[0]:
            response_new += " @" + names[0]
        response_new += "\nПодробнее: /pr_" + str(row[0]) + "\n"
        request = "SELECT rank_name, rank_unique FROM ranks WHERE rank_id = %s"
        cursor_2.execute(request, (row[4],))
        rank = cursor_2.fetchone()
        response_new += "<b>"
        if rank[1]:
            response_new += ranks_specials[rank[1]]
        response_new += rank[0] + "</b>\n"
        response_new += "Репутация: <b>" + str(row[6]) + "</b>\n"
        response_new += "\n______________________________\n"
        if len(response + response_new) >= 4096:
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')