from work_materials.globals import *
import datetime
import time
import logging
import work_materials.globals as globals

from bin.class_func import rangers_notify_start



def battle_stats_send(bot, update = None):
    if update is not None:
        chat_id = update.message.chat_id
    else:
        chat_id = -372516164
    d = datetime.datetime(2018, 5, 27, 7, 0, 0, 0)  # 8 для летнего времени
    c = datetime.datetime(2018, 5, 26, 23, 0, 0, 0)
    c = d - c
    a = datetime.datetime.now()
    a = a - d
    battle_id = -1 # За предыдущую битву
    while a > c:
        a = a - c
        battle_id = battle_id + 1
    print(battle_id)
    request = "SELECT user_id, report_attack, report_defense, report_lvl, report_exp, " \
              "report_gold, report_stock, critical_strike, guardian_angel, additional_attack, additional_defense " \
              "FROM reports WHERE battle_id = '{0}' ORDER BY report_lvl DESC".format(battle_id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id = chat_id, text = "Я не нашёл репорты за прошедшую битву. Вы их кидали? Возможно, на сервере сбилось время")  # GH: -1001381505036 #Test: -1001468891144
        return
    response = "Отчёт по отряду за битву, прошедшую 8 часов назад:\n\n"
    total_attack = 0
    additional_attack = 0
    additional_defense = 0
    total_defense = 0
    critical_strikes = 0
    guardian_angels = 0
    i = 1
    while row:
        request = "SELECT user_castle, username FROM users WHERE user_id = '{0}' and (guild = 'KYS' or guild = 'СКИ')".format(row[0])
        cursor_2.execute(request)
        user = cursor_2.fetchone()
        if user is None:
            row = cursor.fetchone()
            continue
        response_new = "<b>" + str(i) + "</b>. " + user[0] + "<b>" + user[1] + "</b>\n🏅:" + str(row[3]) + ' ⚔:' + str(row[1])
        if row[7] and row[9] > 0:
            response_new += "(+{0})".format(row[9])
        response_new +=' 🛡:'
        response_add = ""
        if row[8] or (row[7] and row[10] > 0):
            response_add += "(+{0})".format(row[10])
        response_new += str(row[2])  + response_add + '\n' + ' 🔥:' + str(row[4]) + ' 💰:' + str(row[5]) + ' 📦:' + str(row[6]) + '\n'
        total_attack += row[1]
        total_defense += row[2]

        if row[7] and row[9] > 0:
            response_new += '<b>⚡️Critical strike</b>\n'
            critical_strikes += 1
            additional_attack += row[9]
        elif row[7] and row[10] > 0:
            response_new += '<b>⚡️️Lucky Defender!</b>\n'
            critical_strikes += 1
            additional_defense += row[10]
        if row[8]:
            response_new += '<b>🔱Guardian angel</b>\n'
            guardian_angels += 1
            additional_defense += row[10]
        response_new += "\n\n"
        if len(response + response_new) >= 4096:  # Превышение лимита длины сообщения
            bot.send_message(chat_id=chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()
        i += 1

    response_new = "\n\n👁‍🗨Total people counted: <b>" + str(i - 1) + "</b>\n"
    response_new += "⚔Total attack: <b>" + str(total_attack) + "</b>\n"
    response_new += "🛡Total defense: <b>" + str(total_defense) + "</b>\n"
    if critical_strikes > 0:
        response_new += "⚡️Critical strikes: <b>" + str(critical_strikes) + "</b>\n"
        response_new += "🗡Атаки получено с критов: <b>" + str(additional_attack) + "</b>\n"
    if guardian_angels > 0:
        response_new += "🔱Guardian angels: <b>" + str(guardian_angels) + "</b>\n"
    if additional_defense > 0:
        response_new += "🛡Защиты получено с ангела или критов: <b>" + str(additional_defense) + "</b>\n"


    if len(response + response_new) >= 4096:  # Превышение лимита длины сообщения
        bot.send_message(chat_id=chat_id, text=response, parse_mode='HTML')
        response = ""
    response += response_new
    bot.send_message(chat_id=chat_id, text=response, parse_mode='HTML')


    #🏅:' + str(row[4]) + ' ⚔:' + str(row[2]) + ' 🛡:' + str(row[3]) + ' 🔥:' + str(row[5]) + ' 💰:' + str(row[6]) + ' 📦:' + str(row[7])
    #if row[8]:
    #    response_new += '<b>\n⚡️Critical strike</b>'
    #if row[9]:
    #    response_new += '<b>\n🔱Guardian angel</b>'

    pass



def add_silent(bot, update):
    mes = update.message
    request = "INSERT INTO silent(chat_id, chat_name) VALUES('{0}', '{1}')".format(mes.chat_id, mes.chat.title)
    cursor.execute(request)
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Беседа успешо добавлена к тишине')


def silent_end(bot, job_queue):
    globals.silent_delete = False
    logging.info("ending silent in chats".format(globals.silent_chats))
    for chat_id in globals.silent_chats:
        try:
            bot.send_message(chat_id = chat_id, text = "Режим тишины отменён!")
        except TelegramError:
            pass
    silent_start(bot, admin_ids[0], None)
    g_attacking_users.clear()
    g_defending_users.clear()
    reports_count.clear()
    globals.g_added_attack = 0
    globals.g_added_defense = 0
    battle_stats_send(bot)

def silent_clear_start(bot, job_queue):
    request = "SELECT COUNT(1) FROM silent where enabled = 1"
    cursor.execute(request)
    row = cursor.fetchone()
    print(row[0])
    print("started successful")
    request = "SELECT chat_id FROM silent WHERE enabled = 1"
    cursor.execute(request)
    row = cursor.fetchone()
    globals.silent_chats.clear()
    while row:
        bot.send_message(chat_id=row[0],
                         text="Через 2 минуты будет активирован режим тишины. Все сообщения, кроме приказов и админов, будут удаляться автоматически.")
        globals.silent_chats.append(row[0])
        row = cursor.fetchone()
    time_to_start = datetime.timedelta(minutes = 2)
    #--------------------------------------------------------------------------------       # TEST ONLY

    #time_to_start = datetime.timedelta(seconds = 1)

    #--------------------------------------------------------------------------------
    job.run_once(silent_start_delete, time_to_start)


def silent_start_delete(bot, job_queue):
    globals.silent_delete = True
    minute = datetime.timedelta(minutes = 1)
    job.run_once(silent_end, minute)
    logging.info("running silent in chats {0}".format(globals.silent_chats))


def silent_setup(bot, update, job_queue):
    global silent_running
    request = "SELECT * FROM silent"
    cursor.execute(request)
    row = cursor.fetchone()
    response = "Currently silent status: " + str(silent_running)
    if silent_running:
        response = response + "\ndisable: /silent_stop"
    else:
        response = response + "\nenable: /silent_start"
    response = response + "\nCurrently existing silent chats:\n"
    while row:
        response = response + '\n' + str(row[0]) + ': ' + row[2] + ', chat_id = ' + str(row[1]) + ', enabled = ' + str(row[3])
        if row[3]:
            response = response + "\ndisable - /sil_run_{0}_0".format(row[0])
        else:
            response = response + "\nenable - /sil_run_{0}_1".format(row[0])
        row = cursor.fetchone()
    bot.send_message(chat_id=update.message.chat_id, text=response)

def silent_start(bot, update, job_queue):
    global job_silence
    global silent_running
    print("Starting...")
    try:
        chat_id = update.message.chat_id
    except AttributeError:
        try:
            chat_id = int(update)
        except TypeError:
            return
    zero = datetime.timedelta(hours = 0)

    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).replace(
        tzinfo=None) - datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=0))
    if now < datetime.timedelta(hours=1):
        remaining_time = datetime.timedelta(hours=1) - now
    else:
        time_from_battle = now - datetime.timedelta(hours=1)
        while time_from_battle > datetime.timedelta(hours=8):
            time_from_battle -= datetime.timedelta(hours=8)
        remaining_time = datetime.timedelta(hours=8) - time_from_battle


    a = remaining_time - datetime.timedelta(minutes=3)# Чтобы тишина началась в 57 минут, а не ровно
    print(a)
    if (a < zero):
        print("ERROR", a)
        bot.send_message(chat_id=chat_id, text="Отрицательное время, прерываю. Получено {0}".format(a))
        return 1

    #----------------------------------------------------------------------------------------------     TEST ONLY

    #a = datetime.timedelta(seconds = 10)

    #______________________________________________________________________________________________

    job_silence = job.run_once(silent_clear_start, a)
    silent_running = 1
    print("OK")
    bot.send_message(chat_id=chat_id, text="Режим тишины активирован, осталось {0}".format(a))
    rangers_notify_start(bot, update, remaining_time)


def silent_delete_message(bot, update):
    mes = update.message
    if update.message.from_user.id not in get_admin_ids(bot, update.message.chat_id):
        try:
            bot.deleteMessage(chat_id = mes.chat_id, message_id = mes.message_id)
        except TelegramError:
            pass


def silent_stop(bot, update, job_queue):
    global job_silence
    job_silence.schedule_removal()
    globals.silent_running = False
    globals.silent_delete = False
    bot.send_message(chat_id=update.message.chat_id, text='Тишина отменена')


def sil_run(bot, update):
    mes = update.message
    mes1 = mes.text.split("_")
    request = "SELECT * FROM silent WHERE silent_id = '{0}'".format(mes1[2])
    cursor.execute(request)
    row = cursor.fetchone()
    if row == None:
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка. Такого чата не найдено')
        return
    request = "UPDATE silent SET enabled = '{0}' WHERE silent_id = '{1}'".format(mes1[3], mes1[2])
    cursor.execute(request)
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')