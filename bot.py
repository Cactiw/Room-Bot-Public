# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter


from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

import time
import datetime

import MySQLdb

import threading

import sys

from mwt import MWT     # Для кэширования
from work_materials.globals import *
from libs.chat_stats import *

from libs.filters.todo import *

from bin.chat_stats import *
from bin.todo import *


status = 0
globalstatus = 0
silent_running = 0
silent_delete = 0
silent_chats = [int] * 10


g_added_attack = 0
g_added_defense = 0
g_attacking_users = []
g_defending_users = []

castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']
ranks_specials = ['','🎗','🎖']

triggers_in = []

all_chats_stats = ChatStats(0, "all", 0, 0, 0, 0, 0, 0, 0, 0)
all_chats_stats.update_from_database()

stats.update({0 : all_chats_stats})


######### a.read().split() - выдаёт массив строк, из файла . которые были разделены пробелом или(может быть) \n

def empty(bot, update): #Пустая функия для объявления очереди
    return 0

class Battles:
    def __init__(self, castle, number):
        self.castle = castle
        self.number = int(number)

    def __lt__(self, other):
        return self.number < other.number

class Report:
    def __init__(self, castle, nickname, exp, gold, stock):
        self.castle = castle
        self.nickname = nickname
        self.exp = int(exp)
        self.gold = int(gold)
        self.stock = int(stock)


class Trigger:
    def __init__(self, type, text):
        self.type = type
        self.text = text

        #Типы триггеров - 0 - текст, 1 - видео, 2 - аудио, 3 - фото, 4 - документ, 5 - стикер, 6 - войс


    def add_trigger(self, incoming, global_trigger):
        if incoming.reply_to_message.text:
            self.type = 0
            self.text = incoming.reply_to_message.text.translate({ord(c): None for c in {'\''}})#, '<', '>'}})
        elif incoming.reply_to_message.video:
            self.type = 1
            self.text = incoming.reply_to_message.video.file_id
        elif incoming.reply_to_message.audio:
            self.type = 2
            self.text = incoming.reply_to_message.audio.file_id
        elif incoming.reply_to_message.photo:
            self.type = 3
            self.text = incoming.reply_to_message.photo[-1].file_id
        elif incoming.reply_to_message.document:
            self.type = 4
            self.text = incoming.reply_to_message.document.file_id
        elif incoming.reply_to_message.sticker:
            self.type = 5
            self.text = incoming.reply_to_message.sticker.file_id
        elif incoming.reply_to_message.voice:
            self.type = 6
            self.text = incoming.reply_to_message.voice.file_id
        if global_trigger:
            request = "INSERT INTO triggers(trigger_in, trigger_out, type, chat_id, creator, date_created) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(incoming.text.lower()[20:], str(self.text), self.type, 0, incoming.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            request = "INSERT INTO triggers(trigger_in, trigger_out, type, chat_id, creator, date_created) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(incoming.text.lower()[13:], str(self.text), self.type, incoming.chat_id, incoming.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(request)
        conn.commit()
        row = cursor.fetchone()
        if row != None:
            print(row)
        cache_full()


    def send_trigger (self, type, trigger_out, bot, update):
        current = Trigger(type, trigger_out)
        #current.process(response)
        if current.type == 0:
            bot.send_message(chat_id=update.message.chat_id, text=trigger_out, parse_mode = 'HTML')
        elif current.type == 1:
            bot.send_video(chat_id=update.message.chat_id, video=current.text)
        elif current.type == 2:
            bot.send_audio(chat_id=update.message.chat_id, audio=current.text)
        elif current.type == 3:
            bot.send_photo(chat_id=update.message.chat_id, photo=current.text)
        elif current.type == 4:
            bot.send_document(chat_id=update.message.chat_id, document=current.text)
        elif current.type == 5:
            bot.send_sticker(chat_id=update.message.chat_id, sticker=current.text)
        elif current.type == 6:
            bot.send_voice(chat_id=update.message.chat_id, voice=current.text)



# Обработка команд
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Привет, давай пообщаемся?')

def attackCommand(bot, update):
    response = update.message.text[1:len(update.message.text)]
    stats = "Рассылка пинов началась в {0}\n\n".format(time.ctime())

    request = "SELECT chat_id, enabled, pin, disable_notification FROM pins"
    cursor.execute(request)
    row = cursor.fetchone()
    chats_count = 0
    while row:
        if row[1]:
            mes_current = bot.send_message(chat_id = row[0], text = response)#Отправка в текущий чат
            chats_count += 1
            if row[2]:
                bot.pinChatMessage(chat_id = row[0], message_id = mes_current.message_id, disable_notification = row[3])
        row = cursor.fetchone()
    stats += "Выполнено в {0}, отправлено в {1} чатов".format(time.ctime(), chats_count)
    bot.send_message(chat_id=update.message.chat_id, text=stats)


@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def add_pin(bot, update):
    mes = update.message
    request = "SELECT pin_id FROM pins WHERE chat_id = '{0}'".format(mes.chat_id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is not None:
        bot.send_message(chat_id=update.message.chat_id, text='Беседа уже подключена к рассылке')
        return
    request = "INSERT INTO pins(chat_id, chat_name) VALUES('{0}', '{1}')".format(mes.chat_id, mes.chat.title)
    cursor.execute(request)
    conn.commit()
    row = cursor.fetchone()
    if row != None:
        print(row)
    bot.send_message(chat_id=update.message.chat_id, text='Беседа успешо подключена к рассылке')



def pin_setup(bot, update):
    request = "SELECT * FROM pins"
    cursor.execute(request)
    row = cursor.fetchone()
    response = "Текущие рассылки пинов:\n"
    while row:
        response = response + '\n' + str(row[0]) + ': ' + row[2] + ', chat_id = ' + str(row[1]) + '\npin = ' + str(row[4]) + '\ndisabled_notification = ' + str(row[5]) + '\nenabled = ' + str(row[3])
        response = response + '\n'
        if row[3]:
            response = response + 'disable /pinset_{0}_0'.format(row[0]) + '\n'
        else:
            response = response + 'enable /pinset_{0}_1'.format(row[0]) + '\n'

        if row[4]:
            response = response + 'disable_pin /pinpin_{0}_0'.format(row[0]) + '\n'
        else:
            response = response + 'enable_pin /pinpin_{0}_1'.format(row[0]) + '\n'

        if row[5]:
            response = response + 'enable_notification /pinmute_{0}_1'.format(row[0]) + '\n'
        else:
            response = response + 'disable_notification /pinmute_{0}_0'.format(row[0]) + '\n'


        row = cursor.fetchone()
    bot.send_message(chat_id=update.message.chat_id, text=response, reply_markup=ReplyKeyboardRemove())


def pinset(bot, update):
    mes = update.message
    mes1 = mes.text.split("_")
    request = "UPDATE pins SET enabled = '{0}' WHERE pin_id = '{1}'".format(mes1[2], mes1[1])
    cursor.execute(request)
    conn.commit()
    row = cursor.fetchone()
    if row != None:
        print(row)
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')


def pinpin(bot, update):
    mes = update.message
    mes1 = mes.text.split("_")
    #print(mes1[0], mes1[1], mes1[2])
    request = "UPDATE pins SET pin = '{0}' WHERE pin_id = '{1}'".format(mes1[2], mes1[1])
    cursor.execute(request)
    conn.commit()
    row = cursor.fetchone()
    if row != None:
        print(row)
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')

def pinmute(bot, update):
    mes = update.message
    mes1 = mes.text.split("_")
    request = "UPDATE pins SET disable_notification = '{0}' WHERE pin_id = '{1}'".format(mes1[2], mes1[1])
    cursor.execute(request)
    conn.commit()
    row = cursor.fetchone()
    if row != None:
        print(row)
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')


def battle_stats_send(bot, update = None):
    if update is not None:
        chat_id = update.message.chat_id
    else:
        chat_id = -1001381505036
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
        request = "SELECT user_castle, username FROM users WHERE user_id = '{0}'".format(row[0])
        cursor_2.execute(request)
        user = cursor_2.fetchone()
        if user is None:
            row = cursor.fetchone()
            continue
        response_new = "<b>" + str(i) + "</b>. " + user[0] + "<b>" + user[1] + "</b>\n🏅:" + str(row[3]) + ' ⚔:' + str(row[1])
        if row[7]:
            response_new += "(+{0})".format(row[9])
        response_new +=' 🛡:'
        if row[8]:
            response_new += "(+{0})".format(row[10])
        response_new += str(row[2])  + '\n' + ' 🔥:' + str(row[4]) + ' 💰:' + str(row[5]) + ' 📦:' + str(row[6]) + '\n'
        total_attack += row[1]
        total_defense += row[2]

        if row[7]:
            response_new += '<b>⚡️Critical strike</b>\n'
            critical_strikes += 1
            additional_attack += row[9]
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
        response_new += "🛡Защиты получено с ангела: <b>" + str(additional_defense) + "</b>\n"


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
    row = cursor.fetchone()
    if row != None:
        print(row)
    bot.send_message(chat_id=update.message.chat_id, text='Беседа успешо добавлена к тишине')


def silent_clear(bot, job_queue):
    global silent_delete
    global silent_chats
    global job_silence
    request = "SELECT COUNT(1) FROM silent where enabled = 1"
    cursor.execute(request)
    row = cursor.fetchone()
    print(row[0])
    silent_chats = [int] * row[0]
    print("started successful")
    request = "SELECT chat_id FROM silent WHERE enabled = 1"
    cursor.execute(request)
    row = cursor.fetchone()
    i = 0
    while row:
        bot.send_message(chat_id = row[0], text = "Через 2 минуты будет активирован режим тишины. Все сообщения, кроме приказов и админов, будут удаляться автоматически.")
        print(silent_chats)
        print(row)
        silent_chats[i] = row[0]
        row = cursor.fetchone()
        i = i + 1
    time.sleep(120)
    silent_delete = 1
    time.sleep(60) #Вернуть на 60
    silent_delete = 0
    for i in silent_chats:
        if i != None:
            print("i =", i)
            try:
                bot.send_message(chat_id = i, text="Режим тишины отменён.")
            except TypeError:
                pass
            try:
                bot.unpinChatMessage(chat_id = -1001381505036)  # Убираем пин в GH
            except TelegramError:
                pass
    try:
        bot.unpinChatMessage(chat_id = -1001381505036)  # Убираем пин в GH
    except TelegramError:
        pass

    d = datetime.datetime(2018, 5, 27, 8, 57, 0, 0)
    c = datetime.datetime(2018, 5, 27, 1, 0, 0, 0)  # Разница в 7 часов 57 минут
    c = d - c
    job_silence = job.run_once(silent_clear_start, c)
    print("Silence is running in", c)
    global g_defending_users
    global g_defending_users
    global g_added_attack
    global g_added_defense
    g_attacking_users.clear()
    g_defending_users.clear()
    g_added_attack = 0
    g_added_defense = 0
    battle_stats_send(bot)

def silent_clear_start(bot, job_queue):
    threading.Thread(target = silent_clear(bot, job)).start()


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
    b = datetime.time(0, 0, 0, 0)  # Вернуть на 00 (01-1)
    #summer = datetime.timedelta(0, 0, 0, 1) # Д:Ч:М:С
    #####b = datetime.time(21, 28, 0, 0)
    summer_a = datetime.datetime(2018, 5, 27, 2, 0, 0, 0)
    summer_b = datetime.datetime(2018, 5, 27, 0, 0, 0, 0)
    hour = datetime.datetime(2018, 5, 27, 1, 0, 0, 0) - summer_b
    summer = summer_a - summer_b
    b = datetime.datetime.combine(datetime.date.today(), b)
    a = datetime.datetime.now()
    print(a)
    print(b)
    print(summer)
    # summer - разница времени сервера / мск
    a = a - b + summer
    # a - Просто текущее время

    #print(a)
    d = datetime.datetime(2018, 5, 27, 9, 0, 0, 0)
    c = datetime.datetime(2018, 5, 27, 1, 0, 0, 0)  # Разница в 8 часов
    e = datetime.datetime(2018, 5, 27, 8, 57, 0, 0) # Летом 8 57 0 0 # Теперь всегда, хватит говнокода
    e = d - e
    # e - время, за которое должна начинаться    тишина перед битвой
    c = d - c
    print(a)
    zero = c - c
    if (a < hour):
        a = hour - a
    else:
        a -= hour
        print(c)
        print("e =", e)
        while not(a <= c):
            a = a - c
        if (a < zero):
            print("ERROR", a)
            return 1
        print(a)
        a = c - a##########
    print(a)
    a = a - e# Чтобы тишина началась в 57 минут, а не ровно
    print(a)
    if (a < zero):
        print("ERROR", a)
        bot.send_message(chat_id=update.message.chat_id, text="Отрицательное время, прерываю. Получено {0}".format(a))
        return 1
    job_silence = job.run_once(silent_clear_start, a)
    silent_running = 1
    print("OK")
    bot.send_message(chat_id=update.message.chat_id, text="Режим тишины активирован, осталось {0}".format(a))


def silent_delete_message(bot, update):
    mes = update.message
    if update.message.from_user.id not in get_admin_ids(bot, update.message.chat_id):
        bot.deleteMessage(chat_id = mes.chat_id, message_id = mes.message_id)


def silent_stop(bot, update, job_queue):
    global silent_running
    global job_silence
    job_silence = job_silence.schedule_removal()
    silent_running = 0
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
    row = cursor.fetchone()
    if row != None:
        print(row)
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')


def mute(bot, update, args):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        return
    if mes.reply_to_message is None:
        return
    if mes.reply_to_message.from_user.id == 231900398:
        bot.send_message(chat_id=update.message.chat_id, text='Банить своего создателя я не буду!')
        return
    if not args:
        return
    current = time.time()
    print(current)
    ban_for = (int(args[0]) * 60)
    current += ban_for
    print(current)
    try:
        bot.restrictChatMember(chat_id=mes.chat_id, user_id = mes.reply_to_message.from_user.id, until_date=current)
    except TelegramError:
        bot.send_message(chat_id=update.message.chat_id, text='Бот не имеет требуемые права, неправильный формат времени, чат не является супергруппой или другая ошибка')
        return
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено!')
    return


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def infoCommand(bot, update):
    mes = update.message
    if update.message.reply_to_message is None:
        return
    response = 'message_id = ' + str(update.message.reply_to_message.message_id) + '\n'
    response = response + 'text: ' + str(update.message.reply_to_message.text) + '\n'
    response = response + 'chat_id = ' + str(update.message.reply_to_message.chat.id) + '\n'
    response = response + 'message from:\n   username: ' + str (update.message.reply_to_message.from_user.username) + '\n   id: ' + str(update.message.reply_to_message.from_user.id) + '\n'
    response = response + 'date: ' + str(update.message.reply_to_message.date) + '\n'
    #response = response + 'photo_id: ' + str(update.message.reply_to_message.photo) + '\n'
    if update.message.reply_to_message.video:
        response = response + 'video_id: ' + str(update.message.reply_to_message.video.file_id) + '\n'
    elif update.message.reply_to_message.audio:
        response = response + 'audio_id: ' + str(update.message.reply_to_message.audio.file_id) + '\n'
        response += "title: " + str(mes.reply_to_message.audio.title) + "\n"
        response += "performer:" + str(mes.reply_to_message.audio.performer) + "\n"
    elif update.message.reply_to_message.photo:
        response = response + 'photo_id: ' + str(update.message.reply_to_message.photo[-1].file_id) + '\n'
    elif update.message.reply_to_message.document:
        response = response + 'document_id: ' + str(update.message.reply_to_message.document.file_id) + '\n'
    elif update.message.reply_to_message.sticker:
        response = response + 'sticker_id: ' + str(update.message.reply_to_message.sticker.file_id) + '\n'
    elif update.message.reply_to_message.voice:
        response = response + 'voice_id: ' + str(update.message.reply_to_message.voice.file_id) + '\n'


    #response = response + 'animation_id: ' + str(update.message.reply_to_message.animation.file_id) + '\n'



    response = response + 'forward from: ' + str(update.message.reply_to_message.forward_from) + '\n'
    response = response + 'forward date: ' + str(update.message.reply_to_message.forward_date) + '\n'
    #response = response + 'message text: ' + str(update.message.reply_to_message.text) + '\n'
    #response = response + 'date: ' + str(update.message.reply_to_message.date) + '\n'
    bot.send_message(chat_id=update.message.chat_id, text=response)




def menuCommand(bot, update):
    button_list = [
    KeyboardButton("/⚔ 🍁"),
    KeyboardButton("/⚔ ☘"),
    KeyboardButton("/⚔ 🖤"),
    KeyboardButton("/⚔ 🐢"),
    KeyboardButton("/⚔ 🦇"),
    KeyboardButton("/⚔ 🌹"),
    KeyboardButton("/⚔ 🍆"),
    ]
    reply_markup = ReplyKeyboardMarkup(build_menu(button_list, n_cols=3))
    bot.send_message(chat_id=update.message.chat_id, text = 'Select castle', reply_markup=reply_markup)


def add_trigger(bot, update):
    mes = update.message
    request = "SELECT * FROM admins WHERE user_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row == None and update.message.from_user.id not in get_admin_ids(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка. Доступ только у админов')
    else:
        request = "SELECT trigger_out FROM triggers WHERE trigger_in = '{0}' AND (chat_id = '{1}' OR chat_id = 0)".format(mes.text.lower()[13:], mes.chat_id)
        cursor.execute(request)
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
    request = "SELECT trigger_out FROM triggers WHERE trigger_in = '{0}' AND chat_id = 0".format(mes.text.lower()[20:], mes.chat_id)
    cursor.execute(request)
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
    request = "SELECT * FROM admins WHERE user_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row == None and update.message.from_user.id not in get_admin_ids(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка. Доступ только у админов')
    else:
        request = "SELECT chat_id, type FROM triggers WHERE trigger_in = '{0}' AND (chat_id = '{1}' OR chat_id = 0)".format(mes.text[16:], mes.chat_id)
        cursor.execute(request)
        row = cursor.fetchone()
        if row == None:
            response = 'Ошибка. Триггер не найден'
            bot.send_message(chat_id=update.message.chat_id, text=response)
        else:
            if row[0] == 0 and mes.from_user.id != 231900398:
                bot.send_message(chat_id=update.message.chat_id, text='Этот триггер глобальный. Удалить его может только @Cactiw')
                return
            request = "DELETE FROM triggers WHERE trigger_in = '{0}' AND (chat_id = '{1}' OR chat_id = 0)".format(mes.text[16:], mes.chat_id)
            cursor.execute(request)
            conn.commit()
            row = cursor.fetchone()
            if row:
                print(row)
            bot.send_message(chat_id=update.message.chat_id, text='Триггер успешно удалён')
            cache_full()

def add_admin(bot, update):
    mes = update.message
    request = "SELECT * FROM admins WHERE user_id = '{0}'".format(mes.reply_to_message.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row:
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка. Админ уже существует')
    else:
        request = "INSERT INTO admins(user_id, user_name) VALUES ('{0}', '{1}')".format(mes.reply_to_message.from_user.id, mes.reply_to_message.from_user.username)
        cursor.execute(request)
        conn.commit()
        row = cursor.fetchone()
        if row != None:
            print(row)

        response = 'Админ добавлен'
        bot.send_message(chat_id=update.message.chat_id, text=response)

def profile(bot, update):#Вывод профиля
    mes = update.message
    request = "SELECT * FROM users WHERE telegram_id = %s" % mes.from_user.id
    cursor.execute(request)
    row = cursor.fetchone()
    if row != None:
        response = row[1] + "<b>" + row[4] + '</b>\nБоец замка ' + row[1] + '\n'
        if int(row[12]):
            request = "SELECT * FROM dspam_users WHERE user_id = '{0}'".format(row[0])
            cursor.execute(request)
            dspam_row = cursor.fetchone()
            if row is not None:
                response += "\nПозывной: <b>" + str(dspam_row[3]) + "</b>\n"
                request = "SELECT rank_name, rank_unique FROM ranks WHERE rank_id = '{0}'".format(dspam_row[4])
                cursor_2.execute(request)
                rank = cursor_2.fetchone()
                response += "Звание: <b>"
                if rank[1]:
                    response += ranks_specials[rank[1]]
                response += rank[0] + "</b>\nОписание звания: /rank_{0}\n".format(str(dspam_row[4]))
                #response += "Ваши достижения: " + str(dspam_row[5]) + " *now in development*\n"
                response += "\n"
        #response = response + 'Номер профиля: ' + str(row[0]) + '\n'
        if row[1] == '🔒':
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            return
        response = response + 'Гильдия: <b>' + str(row[5]) + '</b>\n'
        response = response + '🏅Уровень: ' + str(row[6]) + '\n'
        response = response + '⚔Атака: ' + str(row[7]) + '\n'
        response = response + '🛡Защита: ' + str(row[8]) + '\n'
        response = response + 'Последнее обновление профиля: ' + str(row[10]) + '\n'
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
    else:
        request = "SELECT * FROM dspam_users WHERE telegram_id = %s" % mes.from_user.id
        cursor.execute(request)
        dspam_row = cursor.fetchone()
        if row is not None:
            response = "Позывной: <b>" + str(dspam_row[3]) + "</b>\n"
            response += "Звание: <b>" + str(dspam_row[4]) + "</b>\n"
            # response += "Ваши достижения: " + str(dspam_row[5]) + " *now in development*\n"
            response += "\n"
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            return

        response = 'Профиль отсутствует, пожалуйста, пришлите мне /hero'
        bot.send_message(chat_id=update.message.chat_id, text=response)

def pr(bot, update):
    mes = update.message
    #if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id = -1001330929174)):
        #return

    request = "SELECT * FROM users WHERE user_id = '{0}'".format(mes.text.split('_')[1])
    cursor.execute(request)
    row = cursor.fetchone()
    if row != None:
        response = row[1] + "<b>" + row[4] + '</b>\nБоец замка ' + row[1] + '\n'
        if int(row[12]):
            request = "SELECT * FROM dspam_users WHERE user_id = '{0}'".format(row[0])
            cursor.execute(request)
            dspam_row = cursor.fetchone()
            if row is not None:
                response += "\nПозывной: <b>" + str(dspam_row[3]) + "</b>\n"
                request = "SELECT rank_name, rank_unique FROM ranks WHERE rank_id = '{0}'".format(dspam_row[4])
                cursor_2.execute(request)
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
        request = "SELECT * FROM dspam_users WHERE telegram_id = %s" % mes.from_user.id
        cursor.execute(request)
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
    request = "SELECT * FROM ranks WHERE rank_unique = '{0}'".format(arg)
    cursor.execute(request)
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
    request = "SELECT * FROM ranks WHERE rank_id = '{0}'".format(mes.text.split("_")[1])
    cursor.execute(request)
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
    request = "SELECT rank_name FROM ranks WHERE rank_id = '{0}'".format(args[1])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не найдено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "SELECT * FROM dspam_users WHERE user_id = '{0}'".format(args[0])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Профиль не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE dspam_users SET rank = '{0}' WHERE user_id = '{1}'".format(args[1], args[0])
    cursor.execute(request)
    conn.commit()

    response = 'Звание успешно изменено!'
    bot.send_message(chat_id=update.message.chat_id, text=response)
    response_to_id = row[1]
    request = "SELECT username FROM dspam_users WHERE telegram_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    username = row[0]
    request = "SELECT rank_name FROM ranks WHERE rank_id = '{0}'".format(args[1])
    cursor.execute(request)
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
    request = "SELECT * FROM ranks WHERE rank_id = '{0}'".format(mes.text.split("_")[2])
    cursor.execute(request)
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
    request = "SELECT rank_id FROM ranks WHERE rank_id = '{0}'".format(mes.text.split("_")[2])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE dspam_users SET rank = 3 WHERE rank = '{0}'".format(mes.text.split("_")[2])
    cursor.execute(request)
    conn.commit()
    request = "DELETE FROM ranks WHERE rank_id = '{0}'".format(mes.text.split("_")[2])
    cursor.execute(request)
    conn.commit()
    response = 'Звание успешно удалено\nВсе пользователи, имевшие это звание, получили стандартное.'
    bot.send_message(chat_id=update.message.chat_id, text=response)




def r_set_name(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT rank_id FROM ranks WHERE rank_id = '{0}'".format(mes.text.split(" ")[1])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    offset = mes.text.find(" ") + 1
    from_position = mes.text[offset:].find(" ")
    request = "UPDATE ranks SET rank_name = '{0}' WHERE rank_id = '{1}'".format(mes.text[from_position + offset + 1:], mes.text.split(" ")[1])
    cursor.execute(request)
    conn.commit()
    response = 'Успешно изменено'
    bot.send_message(chat_id=update.message.chat_id, text=response)


def r_set_description(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT rank_id FROM ranks WHERE rank_id = '{0}'".format(mes.text.split(" ")[1])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    offset = mes.text.find(" ") + 1
    from_position = mes.text[offset:].find(" ")
    request = "UPDATE ranks SET rank_data = '{0}' WHERE rank_id = '{1}'".format(mes.text[from_position + offset + 1:], mes.text.split(" ")[1])
    cursor.execute(request)
    conn.commit()
    response = 'Успешно изменено'
    bot.send_message(chat_id=update.message.chat_id, text=response)

def r_set_unique(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=-1001330929174)):
        return
    request = "SELECT rank_id FROM ranks WHERE rank_id = '{0}'".format(mes.text.split("_")[3])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Звание не обнаружено'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE ranks SET rank_unique = '{0}' WHERE rank_id = '{1}'".format(mes.text.split("_")[4], mes.text.split("_")[3])
    cursor.execute(request)
    conn.commit()
    response = 'Успешно изменено'
    bot.send_message(chat_id=update.message.chat_id, text=response)



def reg(bot, update):
    mes = update.message
    request = "SELECT * FROM users WHERE telegram_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None: #Добавляем челика не из чв
        #response = 'Профиль отсутствует, пожалуйста, пришлите мне /hero'
        #bot.send_message(chat_id=update.message.chat_id, text=response)
        #return
        request = "INSERT INTO users(user_castle, telegram_id, telegram_username, username, last_update, dspam_user) VALUES ('🔒', '{0}', '{1}', '{2}', '{3}', '1')".format(mes.from_user.id, mes.from_user.username, mes.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(request)
        conn.commit()
        request = "SELECT user_id FROM users WHERE telegram_id = '{0}'".format(mes.from_user.id)
        cursor.execute(request)
        row = cursor.fetchone()
        request = "INSERT INTO dspam_users(user_id, telegram_id, username) VALUES ('{0}', '{1}', '{2}')".format(int(row[0]), mes.from_user.id, mes.from_user.username)
        cursor.execute(request)
        conn.commit()
        response = 'Регистрация успешна'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    if int(row[12]) == 1:
        response = 'Вы уже зарегистрированы'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "UPDATE users SET dspam_user = '1' where telegram_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
    conn.commit()
    request = "INSERT INTO dspam_users(user_id, telegram_id, username) VALUES ('{0}', '{1}', '{2}')".format(int(row[0]), mes.from_user.id, row[4])
    cursor.execute(request)
    conn.commit()
    response = 'Регистрация успешна'
    bot.send_message(chat_id=update.message.chat_id, text=response)


def set_call_sign(bot, update, args):
    mes = update.message
    if not args:
        response = 'Неверный синтаксис'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    request = "SELECT * FROM dspam_users WHERE telegram_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Профиль не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return

    request = "INSERT INTO requests(request_type, user_id, data) VALUES ('1', '{0}', '{1}')".format(int(row[0]), mes.text[15:])
    cursor.execute(request)
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
    request = "SELECT * FROM dspam_users WHERE user_id = '{0}'".format(args[0])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Профиль не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    from_position = mes.text[17:].find(" ") + 17 + 1
    request = "UPDATE dspam_users SET call_sign = '{0}' WHERE user_id = '{1}'".format(mes.text[from_position:].upper(), row[0])
    cursor.execute(request)
    conn.commit()

    response = 'Позывной успешно изменён!'
    bot.send_message(chat_id=update.message.chat_id, text=response)
    response_to_id = row[1]
    request = "SELECT call_sign, username FROM dspam_users WHERE telegram_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
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
            request = "SELECT telegram_username, username FROM users WHERE user_id = '{0}'".format(row[2])
            cursor_2.execute(request)
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
    request = "SELECT * FROM requests WHERE request_id = '{0}'".format(request_id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Запрос не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    if row[1] == 1:
        request = "UPDATE dspam_users SET call_sign = '{0}' WHERE user_id = '{1}'".format(row[3].upper(), row[2])
        cursor.execute(request)
        conn.commit()
        request = "DELETE FROM requests WHERE request_id = '{0}'".format(request_id)
        cursor.execute(request)
        conn.commit()
        response = 'Запрос успешно принят. Хорошего дня!\nПросмотреть остальные запросы: /requests'
        bot.send_message(chat_id = update.message.chat_id, text=response)
        request = "SELECT telegram_id FROM users WHERE user_id = '{0}'".format(row[2])
        cursor.execute(request)
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
    request = "SELECT * FROM requests WHERE request_id = '{0}'".format(request_id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        response = 'Запрос не найден'
        bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    if row[1] == 1:
        request = "DELETE FROM requests WHERE request_id = '{0}'".format(request_id)
        cursor.execute(request)
        conn.commit()
        response = 'Запрос отклонён. Хорошего дня!\nПросмотреть остальные запросы: /requests'
        bot.send_message(chat_id=update.message.chat_id, text=response)

        request = "SELECT telegram_id FROM users WHERE user_id = '{0}'".format(row[2])
        cursor.execute(request)
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
        request = "SELECT telegram_username, username FROM users WHERE user_id = '{0}'".format(row[0])
        cursor_2.execute(request)
        names = cursor_2.fetchone()
        response_new = ""
        response_new += "\n<b>" + names[1] + "</b>"

        if names[0]:
            response_new += " @" + names[0]
        response_new += "\nПодробнее: /pr_" + str(row[0]) + "\n"
        request = "SELECT rank_name, rank_unique FROM ranks WHERE rank_id = '{0}'".format(row[4])
        cursor_2.execute(request)
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


def setdr(bot, update):#Задание дня рождения
    mes = update.message #/setdr mm-dd

    request = "SELECT * FROM users WHERE telegram_id = '{0}'".format(mes.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row == None:
        response = "Пользователь не найден, обновите /hero"
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
        return

    a = mes.text[7:]
    a = '2000-' + a
    request = "UPDATE users SET birthday = '{0}' WHERE room_bot.users.telegram_id = '{1}'".format(a, mes.from_user.id)
    cursor.execute(request)
    conn.commit()
    row = cursor.fetchone()
    if row != None:
        print(row)
    bot.send_message(chat_id=update.message.chat_id, text='День рождения обновлён')

class Dr_user:
    def __init__(self, username, delta):
        self.username = username
        self.delta = delta

def dr(bot, update):    #   TODO починить дни рождения
    mes = update.message
    request = "SELECT count(1) FROM users"
    cursor.execute(request)
    num_users = int(cursor.fetchone()[0])
    request = "SELECT birthday, username FROM users"
    cursor.execute(request)
    row = cursor.fetchone()
    #print(row)
    current = time.strftime('%Y-%m-%d')
    current_list = current.split("-")
    current_date = datetime.date(int(2000), int(current_list[1]), int(current_list[2]))
    none_date = datetime.date(int(1999), int(current_list[1]), int(current_list[2]))
    users = [Dr_user(None, None)] * num_users
    print(num_users)
    i = 0
    while row:
        a = row[0]
        if a == None:
            delta = none_date - current_date
            print(delta)
        else:
            delta = a - current_date

        users[i] = Dr_user(row[1], delta)

        #print(users[i])
        print(users[i].username, users[i].delta)

        row = cursor.fetchone()
    users_by_dr = [Dr_user] * num_users



    users_by_dr = sorted(users, key=lambda Dr_user: Dr_user.delta, reverse=False)
    print(users_by_dr[0].username, users_by_dr[0].delta)
    print(users_by_dr[1].username, users_by_dr[1].delta)
    print(users_by_dr[2].username, users_by_dr[2].delta)
    print(users_by_dr[3].username, users_by_dr[3].delta)

    zero = current_date - current_date
    for i in range (0, num_users):
        print('i =', i)
        print(users_by_dr[i].username, users_by_dr[i].delta)
        if users_by_dr[i].delta >= zero:
            if users_by_dr[i].delta == zero:
                response = "Вот это да! Сегодня у <b>'{0}'</b> день рождения! Поздравляем! Накидываем нюдесы в лс!".format(users_by_dr[i].username)
                bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode = 'HTML')
                return
            else:
                request = "SELECT birthday FROM users WHERE username = '{0}'".format(users_by_dr[i].username)
                cursor.execute(request)
                row = cursor.fetchone()
                date = str(row[0])[5:].split("-")
                response = "Сегодня день рождения никто не празднует, однако ближайший день рождения у <b>{0}</b>, готовим поздравления к <b>{1}</b>\nЭто через <b>{2}</b>".format(users_by_dr[i].username, date[1] + '/' + date[0], users_by_dr[i].delta)
                bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
                return

def g_info(bot, update):
    mes = update.message
    request = "SELECT username, user_lvl, user_attack, user_defense FROM users WHERE guild = '{0}' ORDER BY user_lvl DESC".format(mes.text.split(' ')[1])
    cursor.execute(request)
    row = cursor.fetchone()

    response = "Статистика по гильдии <b>" + mes.text.split(' ')[1] + "</b>:\n"

    total_attack = 0
    total_defense = 0
    max_lvl = 0
    max_lvl_user = ""


    while row:
        response = response + '\n' + "<b>" + row[0] + "</b>" + "\n🏅" + str(row[1]) + " ⚔" + str(row[2]) + " 🛡" + str(row[3]) + '\n'
        total_attack += row[2]
        total_defense += row[3]
        if row[1] > max_lvl:
            max_lvl = row[1]
            max_lvl_user = row[0]

        row = cursor.fetchone()
    response += "\n\n" + "Всего атаки: ⚔" + str(total_attack) + ", всего защиты: 🛡" + str(total_defense)
    response += "\n" + "Максимальный уровень у <b>" + max_lvl_user + "</b>, 🏅" + str(max_lvl)
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


class User_for_attack:
    attack = 0
    username = ""
    g_attacking = -1
    def __init__(self, username, attack, g_attacking):
        self.username = username
        self.attack = attack
        self.g_attacking = g_attacking


class User:
    def __init__(self, id, username, attack, defense):
        self.id = id
        self.username = username
        self.attack = attack
        self.defense = defense


def g_attack(bot, update):
    mes = update.message
    num_users = 0
    total_attack = 0
    users = []
    num_guilds = int(mes.text.split(' ')[1])
    for i in g_attacking_users:
        num_users += 1
        total_attack += i.attack
        users.append(User_for_attack(i.username, i.attack, -1))



    ratio = mes.text.split(' ')[2]
    ratios = ratio.split(':')
    sum_ratio = 0
    for i in range(0, num_guilds):
        sum_ratio += int(ratios[i])
    # print(ratios)
    attacks = [int] * num_guilds
    for i in range(0, num_guilds):
        attacks[i] = int(ratios[i]) / sum_ratio * total_attack
    # print("sum_attack = ", total_attack, attacks)
    #       Здесь кончается верный кусок кода
    for i in range(0, num_users):
        # print("i = ", i, "username = ", users[i].username)
        min_remain = 100000000  # Перестанет работать, если вдруг суммарная атака достигнет этой величины
        min_number = 0
        flag = 0
        for j in range(0, num_guilds):
            # print("attacks[", j, "] =", attacks[j])
            remain = attacks[j] - users[i].attack
            # print("remain =", remain)
            if remain < min_remain and remain >= 0:
                min_remain = remain
                min_number = j
                flag = 1
                # print("YES")
        if flag:  # Есть свободное место под этого атакующего
            users[i].g_attacking = min_number
            attacks[min_number] = min_remain
        else:
            min_remain = -100000000
            for j in range(0, num_guilds):
                remain = attacks[j] - users[i].attack
                # print(remain, min_remain, min_number)
                if remain > min_remain:
                    min_remain = remain
                    min_number = j
                    attacks[j] = remain
            users[i].g_attacking = min_number
    response = "Рассчёт распределения урона подготовлен:"
    for i in range(0, num_guilds):
        response += "\n" + str(i) + " гильдия:\n"
        guild_attack = 0
        for j in range(0, num_users):
            if users[j].g_attacking == i:
                response += "<b>" + users[j].username + "</b> ⚔" + str(users[j].attack) + "\n"
                guild_attack += users[j].attack
        response += "Total attack: ⚔" + str(guild_attack) + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def g_all_attack(bot, update):
    mes = update.message
    num_attacking_guilds = int(mes.text.split(' ')[1])
    request = "SELECT COUNT(1) FROM users WHERE guild = '{0}'".format(mes.text.split(' ')[2])
    request2 = "SELECT username, user_attack FROM users WHERE guild = '{0}'".format(mes.text.split(' ')[2])
    for i in range (1, num_attacking_guilds):
        request += " OR guild = '{0}'".format(mes.text.split(' ')[i + 2])
        request2 += " OR guild = '{0}'".format(mes.text.split(' ')[i + 2])

    request2 += " ORDER BY user_attack DESC"
    #print(request)
    #print(request2)
    num_guilds = int(mes.text.split(' ')[num_attacking_guilds + 2])
    cursor.execute(request)
    row = cursor.fetchone()

    num_users = int(row[0])

    users = []

    cursor.execute(request2)
    row = cursor.fetchone()
    total_attack = 0
    i = 0
    #print(num_users)
    while row:
        #print(row)
        total_attack += int(row[1])
        #users[i].attack = int(row[1])
        #users[i].username = row[0]
        users.append(User_for_attack(row[0], int(row[1]), -1))
        #print("i = ", i, "username = ", users[i].username)
        #print("username[0] = ", users[0].username)
        i += 1
        row = cursor.fetchone()

    #print(i)

    ratio = mes.text.split(' ')[num_attacking_guilds + 3]
    ratios = ratio.split(':')
    sum_ratio = 0
    for i in range (0, num_guilds):
        sum_ratio += int(ratios[i])
    #print(ratios)
    attacks = [int] * num_guilds
    for i in range (0, num_guilds):
        attacks[i] = int(ratios[i]) / sum_ratio * total_attack
    #print("sum_attack = ", total_attack, attacks)
    #       Здесь кончается верный кусок кода
    for i in range (0, num_users):
        #print("i = ", i, "username = ", users[i].username)
        min_remain = 100000000    #Перестанет работать, если вдруг суммарная атака достигнет этой величины
        min_number = 0
        flag = 0
        for j in range (0, num_guilds):
            #print("attacks[", j, "] =", attacks[j])
            remain = attacks[j] - users[i].attack
            #print("remain =", remain)
            if remain < min_remain and remain >= 0:
                min_remain = remain
                min_number = j
                flag = 1
                #print("YES")
        if flag: #  Есть свободное место под этого атакующего
            users[i].g_attacking = min_number
            attacks[min_number] = min_remain
        else:
            min_remain = -100000000
            for j in range(0, num_guilds):
                remain = attacks[j] - users[i].attack
                #print(remain, min_remain, min_number)
                if remain > min_remain:
                    min_remain = remain
                    min_number = j
                    attacks[j] = remain
            users[i].g_attacking = min_number
    response = "Рассчёт распределения урона подготовлен:"
    for i in range (0, num_guilds):
        response += "\n" + str(i) + " гильдия:\n"
        guild_attack = 0
        for j in range (0, num_users):
            if users[j].g_attacking == i:
                response += "<b>" + users[j].username + "</b> ⚔" + str(users[j].attack) + "\n"
                guild_attack += users[j].attack
        response += "Total attack: ⚔" + str(guild_attack) + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def g_add_attack(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_attack
    global g_attacking_users
    request = "SELECT user_attack, username FROM users WHERE telegram_id = '{0}'".format(mes.reply_to_message.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text="Пользователь не найден в базе данных")
        return
    current = User(id, row[1], row[0], 0)
    for i in g_attacking_users:
        if i.id == id:
            bot.send_message(chat_id=update.message.chat_id, text="Игрок уже атакует")
            return
    g_added_attack += row[0]
    g_attacking_users.append(current)
    response = "Пользователь добавлен. Всего атаки на цель: ⚔<b>{0}</b>\n".format(g_added_attack)
    response += "Атакующие игроки:\n"
    g_attacking_users.sort(key = lambda curr:curr.attack, reverse = True)
    for i in g_attacking_users:
        response += "<b>{0}</b> ⚔<b>{1}</b>\n".format(i.username, i.attack)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def g_del_attack(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_attack
    global g_attacking_users
    for i in g_attacking_users:
        if i.id == id:
            g_added_attack -= i.attack
            g_attacking_users.remove(i)
            bot.send_message(chat_id=update.message.chat_id, text="Игрок успешно удалён")
            return
    bot.send_message(chat_id=update.message.chat_id, text="Игрок не найден в списке для атаки")


def g_attacking_list(bot, update):
    response = "Атакующие игроки:\n"
    g_attacking_users.sort(key=lambda curr: curr.attack, reverse=True)
    for i in g_attacking_users:
        response += "<b>{0}</b> ⚔<b>{1}</b>\n".format(i.username, i.attack)
    response += "\n\nВсего атаки: ⚔<b>{0}</b>".format(g_added_attack)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def g_add_defense(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_defense
    global g_defending_users
    request = "SELECT user_defense, username FROM users WHERE telegram_id = '{0}'".format(mes.reply_to_message.from_user.id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text="Пользователь не найден в базе данных")
        return
    current = User(mes.reply_to_message.from_user.id, row[1], 0, row[0])
    for i in g_defending_users:
        if i.id == id:
            bot.send_message(chat_id=update.message.chat_id, text="Игрок уже защищает")
            return
    g_added_defense += row[0]
    g_defending_users.append(current)
    response = "Пользователь добавлен. Всего защиты: 🛡<b>{0}</b>\n".format(g_added_defense)
    response += "Атакующие игроки:\n"
    g_defending_users.sort(key = lambda curr:curr.defense, reverse = True)
    for i in g_defending_users:
        response += "<b>{0}</b> 🛡<b>{1}</b>\n".format(i.username, i.defense)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def g_del_defense(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_defense
    global g_defending_users
    for i in g_defending_users:
        if i.id == id:
            g_added_defense -= i.defense
            g_defending_users.remove(i)
            bot.send_message(chat_id=update.message.chat_id, text="Игрок успешно удалён")
            return
    bot.send_message(chat_id=update.message.chat_id, text="Игрок не найден в списке для защиты")

def g_defending_list(bot, update):
    response = "Защищающие игроки:\n"
    g_defending_users.sort(key=lambda curr: curr.defense, reverse=True)
    for i in g_defending_users:
        response += "<b>{0}</b> 🛡<b>{1}</b>\n".format(i.username, i.defense)
    response += "\n\nВсего защиты: 🛡<b>{0}</b>".format(g_added_defense)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')



def g_help(bot, update):
    bot.send_message(chat_id = update.message.chat_id, text = "Список команд для работы с гильдиями:\nhttps://orderbot.page.link/nM9x") # https://telegra.ph/Komandy-dlya-raboty-s-gildiyami-10-16
    return



def add_battle(bot, update):
    global Battles_OSA
    global Battles_MTR
    global split_OSA
    global split_MTR
    global number_battles
    global castles
    Battles_OSA.seek(0)
    Battles_MTR.seek(0)
    OSA = Battles_OSA.readlines()
    MTR = Battles_MTR.readlines()
    mes = update.message.text[12:len(update.message.text)]
    #castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']
    #print(mes)
    alliance = 0
    split = 0
    for i in range (0, len(mes)):
        if mes[i] == ' ':
            alliance = 1
            split = 0
        else:
            for j in range (0, 7):
                if mes[i] == castles[j]:
                    if split == 0:
                        if alliance == 0:
                            OSA[j] = str(int(OSA[j].split()[0]) + 1) + ' ' + OSA[j].split()[1] + '\n'
                        else:
                            MTR[j] = str(int(MTR[j].split()[0]) + 1) + ' ' + MTR[j].split()[1] + '\n'
                        split = 1
                    else:
                        if alliance == 0:
                            OSA[j] = OSA[j].split()[0] + ' ' + str(int(OSA[j].split()[1]) + 1) + '\n'
                            split_OSA = split_OSA + 1
                        else:
                            MTR[j] = MTR[j].split()[0] + ' ' + str(int(MTR[j].split()[1]) + 1) + '\n'
                            split_MTR = split_MTR +  1

    #print(OSA)
    Battles_OSA.close()
    Battles_OSA = open('Battles_OSA.txt', 'w')
    Battles_OSA.writelines(OSA)
    Battles_OSA.close()
    Battles_OSA = open('Battles_OSA.txt', 'r')

    #print(MTR)
    Battles_MTR.close()
    Battles_MTR = open('Battles_MTR.txt', 'w')
    Battles_MTR.writelines(MTR)
    Battles_MTR.close()
    Battles_MTR = open('Battles_MTR.txt', 'r')

    number_battles = number_battles + 1
    bot.send_message(chat_id=update.message.chat_id, text='Битва добавлена.\nВсего битв учтено: ' + str(number_battles))

def battles_stats(bot, update):
    global castles
    global number_battles
    global split_OSA
    global split_MTR
    global Battles_OSA
    global Battles_MTR
    Battles_OSA.seek(0)
    Battles_MTR.seek(0)
    OSA = Battles_OSA.readlines()
    MTR = Battles_MTR.readlines()
    Stats_battles_OSA = [None] * 7
    Stats_split_OSA = [None] * 7
    Stats_battles_MTR = [None] * 7
    Stats_split_MTR = [None] * 7
    for i in range (0, 7):
        #print(OSA[i].split())
        Stats_battles_OSA[i] = Battles(castles[i], OSA[i].split()[0])
        Stats_split_OSA[i] = Battles(castles[i], OSA[i].split()[1])
        Stats_battles_MTR[i] = Battles(castles[i], MTR[i].split()[0])
        Stats_split_MTR[i] = Battles(castles[i], MTR[i].split()[1])
    Stats_battles_OSA.sort(reverse = True)
    Stats_split_OSA.sort(reverse = True)
    Stats_battles_MTR.sort(reverse = True)
    Stats_split_MTR.sort(reverse = True)
    #for i in range (0, 7):
        #print(Stats_battles_OSA[i].castle, Stats_battles_OSA[i].number, Stats_battles_MTR[i].castle, Stats_battles_MTR[i].number)
    response = 'Статистика Битв. Альянс ОСА, заблаговременные пины:\n'
    for i in range (0, 7):
        response = response + Stats_battles_OSA[i].castle + ' ' + str(Stats_battles_OSA[i].number) + '(' + str(int(Stats_battles_OSA[i].number) / number_battles * 100) + '%)\n'
    response = response + '\nАльянс ОСА, сплиты / развороты:\n'
    for i in range (0, 7):
        response = response + Stats_split_OSA[i].castle + ' ' + str(Stats_split_OSA[i].number) + '(' + str(int(Stats_split_OSA[i].number) / split_OSA * 100) + '%)\n'
    response = response + 'Всего сплитов у ОСА учтено:' + str(split_OSA) + '\n\nАльянс МТР, заблаговременные пины:\n'
    for i in range (0, 7):
        response = response + Stats_battles_MTR[i].castle + ' ' + str(Stats_battles_MTR[i].number) + '(' + str(int(Stats_battles_MTR[i].number) / number_battles * 100) + '%)\n'
    response = response + '\nАльянс МТР, сплиты / развороты:\n'
    for i in range (0, 7):
        response = response + Stats_split_MTR[i].castle + ' ' + str(Stats_split_MTR[i].number) + '(' + str(int(Stats_split_MTR[i].number) / split_MTR * 100) + '%)\n'
    response = response + 'Всего сплитов у МТР учтено:' + str(split_MTR) + '\n\nВсего битв учтено в статистике : ' + str(number_battles)

    response += "\n<b>Предупреждение: в связи с выходом Амбера из ОСА данная статистика более не актуальна и не обновляется.</b>\n"
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def add_playlist(bot, update, args):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        return
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text='Неверный синтаксис')
        return
    request = "SELECT * FROM playlists WHERE playlist_name = '{0}' and chat_id = '{1}'".format(mes.text.partition(' ')[2], mes.chat_id)
    cursor.execute(request)
    row = cursor.fetchone()
    if row is not None:
        bot.send_message(chat_id=update.message.chat_id, text= 'Данный плейлист уже существует!')
        return
    request = "INSERT INTO playlists(playlist_name, chat_id, created_by, date_created) VALUES ('{0}', '{1}', '{2}', '{3}')".format(mes.text.partition(' ')[2].upper(), mes.chat_id, mes.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S'))
    cursor.execute(request)
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Плейлист успешно добавлен!')


def list_playlists(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        bot.send_message(chat_id=update.message.chat_id, text= 'Только админы. Хватит засорять чаты')
        return
    response = "Список плейлистов:\n"
    request = "SELECT * from playlists WHERE chat_id = '{0}'".format(mes.chat_id)
    cursor.execute(request)
    row = cursor.fetchone()
    while row:
        response_new = '\n<b>' + row[1] + '</b>\n' + "id: {0}, Created by:{1}, date_created : {2}\nView: /view_playlist_{0}\nPlay random :/play_random_from_playlist_{0}".format(row[0], row[3], row[4]) +'\n\n'
        if len(response + response_new) >= 4096:
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def view_playlist(bot, update):
    mes = update.message
    #if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        #bot.send_message(chat_id=update.message.chat_id, text= 'Только админы. Хватит засорять чаты')
        #return
    request = "SELECT song_id, title, performer, duration FROM songs WHERE playlist_id = '{0}'".format(mes.text.partition('@')[0].partition('_')[2].partition('_')[2])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text='Плейлист пуст. Добавьте песни!')
        return
    response = "Список песен в плейлисте:\n"
    while row:
        response_new = "\n<b> {0}</b>,\nid : {1}, performer: <b>{2}</b>\nduration: {3}\nplay: /play_song_{1}\nremove: /remove_song_{1}".format(row[1], row[0], row[2], row[3])
        if len(response + response_new) >= 4096:
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()
    #print(response)
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')



def add_to_playlist(bot, update, args):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        bot.send_message(chat_id=update.message.chat_id, text= 'Только админы. <b>ТОЛЬКО!!!</b>', parse_mode='HTML')
        return
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text='Неверный синтаксис')
        return
    if mes.reply_to_message is None:
        bot.send_message(chat_id=update.message.chat_id, text='Сообщение должно быть ответом на песню', parse_mode='HTML')
        return
    if mes.reply_to_message.audio.file_id is None:
        bot.send_message(chat_id=update.message.chat_id, text='Сообщение должно быть ответом на песню',
                         parse_mode='HTML')
        return
    request = "SELECT * FROM songs WHERE file_id = '{0}' AND playlist_id = '{1}'".format(mes.reply_to_message.audio.file_id, mes.text.partition(' ')[2])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is not None:
        bot.send_message(chat_id=update.message.chat_id, text='Песня уже находится в этом плейлисте')
        return
    if mes.reply_to_message.audio.performer:
        performer = mes.reply_to_message.audio.performer.translate({ord(c): None for c in {'\'', '<', '>'}})
    else:
        performer = None
    if mes.reply_to_message.audio.title:
        title = mes.reply_to_message.audio.title.translate({ord(c): None for c in {'\'', '<', '>'}})
    else:
        title = None
    request = "INSERT INTO songs(file_id, playlist_id, performer, title, duration) VALUES ('{0}', '{1}', '{2}'," \
              " '{3}', '{4}')".format(mes.reply_to_message.audio.file_id, mes.text.partition(' ')[2],
                                      performer,
                                      title,
                                      mes.reply_to_message.audio.duration)
    ###trigger_mes = mes.text.translate({ord(c): None for c in '\''})
    try:
        cursor.execute(request)
    except:
        bot.send_message(chat_id=update.message.chat_id, text='Что-то пошло не так, проверьте правильность id плейлиста')
        return
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Песня успешно добавлена!')


def play_random_from_playlist(bot, update, args = None):
    mes = update.message
    #if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        #bot.send_message(chat_id=update.message.chat_id, text= 'Только админы. <b>ТОЛЬКО!!!</b>', parse_mode='HTML')
        #return
    if not args:
        try:
            arg = int(mes.text.partition('@')[0].partition('_')[2].partition('_')[2].partition('_')[2].partition('_')[2])
        except ValueError:
            bot.send_message(chat_id=update.message.chat_id, text='Неверный синтаксис')
            return
        request = "SELECT file_id FROM songs WHERE playlist_id = '{0}' ORDER BY RAND() LIMIT 1".format(arg)
        cursor.execute(request)
        row = cursor.fetchone()
        if row is None:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Песня не найдена. Проверьте корректность ввода id плейлиста. Возможно, что он пуст.')
            return
        bot.send_audio(chat_id=mes.chat_id, audio=row[0])
        return
    request = "SELECT file_id FROM songs WHERE playlist_id = '{0}' ORDER BY RAND() LIMIT 1".format(args[0])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text='Песня не найдена. Проверьте корректность ввода id плейлиста. Возможно, что он пуст.')
        return
    bot.send_audio(chat_id = mes.chat_id, audio = row[0])


def play_song(bot, update):
    mes = update.message
    #if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        #bot.send_message(chat_id=update.message.chat_id, text= 'Только админы. <b>ТОЛЬКО!!!</b>', parse_mode='HTML')
        #return
    request = "SELECT file_id FROM songs WHERE song_id = '{0}'".format(mes.text.partition('@')[0].partition('_')[2].partition('_')[2])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text='Песня не найдена. Проверьте корректность ввода id песни.')
        return
    bot.send_audio(chat_id = mes.chat_id, audio = row[0])

def remove_song(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        bot.send_message(chat_id=update.message.chat_id, text= 'Только админы. <b>ТОЛЬКО!!!</b>', parse_mode='HTML')
        return
    request = "SELECT file_id FROM songs WHERE song_id = '{0}'".format(mes.text.partition('@')[0].partition('_')[2].partition('_')[2])
    cursor.execute(request)
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Песня не найдена. Проверьте корректность ввода id песни.')
        return
    request = "DELETE FROM songs WHERE song_id = '{0}'".format(mes.text.partition('@')[0].partition('_')[2].partition('_')[2])
    try:
        cursor.execute(request)
    except:
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка', parse_mode='HTML')
        return
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено', parse_mode='HTML')


def battle_history(bot, update):
    mes = update.message
    request = "SELECT user_id FROM users WHERE telegram_id = %s" % mes.from_user.id
    cursor.execute(request)
    row = cursor.fetchone()
    request = "SELECT battle_id, date_in, report_attack, report_defense, report_lvl, report_exp, report_gold, report_stock, critical_strike, guardian_angel FROM reports WHERE user_id = %s ORDER BY battle_id" % row
    cursor.execute(request)
    row = cursor.fetchone()
    #print(row)
    response = '' 'История битв по внесённым репортам:'
    while row:
        #print(row)
        response_new ='\n\n🏅:' + str(row[4]) + ' ⚔:' + str(row[2]) + ' 🛡:' + str(row[3]) + ' 🔥:' + str(row[5]) + ' 💰:' + str(row[6]) + ' 📦:' + str(row[7])
        if row[8]:
            response_new += '<b>\n⚡️Critical strike</b>'
        if row[9]:
            response_new += '<b>\n🔱Guardian angel</b>'
        response_new += '\nbattle_id: ' + str(row[0]) + ', date_in: ' + str(row[1])
        if len(response + response_new) >= 4096:  # Превышение лимита длины сообщения
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new

        row = cursor.fetchone()
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def sql(bot, update, user_data):
    mes = update.message
    request = mes.text.partition(" ")[2]
    try:
        cursor.execute(request)
    except:
        error = sys.exc_info()
        response = ""
        for i in range(0, len(error)):
            response += str(sys.exc_info()[i]) + '\n'
        bot.send_message(chat_id=mes.chat_id, text=response)
        return
    conn.commit()
    row = cursor.fetchone()
    response = ""
    while row:
        for i in range(0, len(row)):
            response += str(row[i]) + " "
        row = cursor.fetchone()
        response += "\n\n"
    if response is None:
        bot.send_message(chat_id=mes.chat_id, text="Пустой ответ. Успешная операция, или таких строк не найдено")
        return
    bot.send_message(chat_id=mes.chat_id, text=response)


def textMessage(bot, update):
    #Обработка триггеров и всего остального
    global status
    global globalstatus
    if (status):
        globalstatus = 1
    global Triggers_in
    global Triggers_out
    global Smart_triggers_out
    global Triggers_count
    mes = update.message

    if (update.message.text.lower()) == 'статус':
        if (globalstatus):
            bot.send_message(chat_id=update.message.chat_id, text='Бот функционирует, зафиксированы некритичные ошибки ' + '\n' + time.ctime())

        else:
            bot.send_message(chat_id=update.message.chat_id, text='Система функционирует нормально, ошибок не зафиксировано' + '\n' + time.ctime()) #   TODO сделать нормальный статус
    #print (Triggers_count)

    trigger_mes = mes.text.translate({ord(c): None for c in '\''})
    #Обработка специальных триггеров

    if mes.chat_id == -1001330929174: # ДСПАМ  -1001197381190

        if mes.text.find ('+') == 0 or mes.text.find ('-') == 0:  # Репутация
            if mes.reply_to_message:
                if mes.from_user.id != mes.reply_to_message.from_user.id:

                    request = "SELECT user_id, call_sign, reputation FROM dspam_users WHERE telegram_id = '{0}'".format(mes.reply_to_message.from_user.id)
                    cursor.execute(request)
                    row = cursor.fetchone()
                    if mes.text.find ('+') == 0:
                        reputation_change = 1
                    else:
                        reputation_change = -1
                    reputation = row[2] + reputation_change
                    request = "UPDATE dspam_users SET reputation = '{0}' WHERE user_id = '{1}'".format(reputation, row[0])
                    cursor.execute(request)
                    conn.commit()

                    request = "SELECT call_sign, reputation FROM dspam_users WHERE telegram_id = '{0}'".format(mes.from_user.id)
                    cursor.execute(request)
                    user_from = cursor.fetchone()
                    response = ""
                    if user_from:
                        response += "<b>" + user_from[0] + "</b> изменил репутацию <b>" + row[1] + "</b> на <b>" + str(reputation_change) + "</b>\n"
                        response += "Текущая репутация:<b>" + str(reputation) + "</b>"
                    else:
                        response += "Репутация <b>" + row[1] + "</b> была изменена на <b>" + str(reputation_change) + "</b> пользователем, которого я не знаю.\n"
                        response += "Пришли мне /hero из @chatwarsbot (предпочтительней), и/или нажми /reg\n"
                        response += "Текущая репутация: <b>" + str(reputation) + "</b>"

                    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
                    return

        if mes.text.lower().find ("доброе утро") > -1 or mes.text.lower().find ("утречка") > -1 or mes.text.lower().find ("доброго утра") > -1:
            response = ""
            request = "SELECT call_sign, reputation FROM dspam_users WHERE telegram_id = '{0}'".format(mes.from_user.id)
            cursor.execute(request)
            row = cursor.fetchone()
            if row is not None:
                if mes.from_user.id in get_admin_ids(bot, chat_id=-1001330929174):
                    response += "Как хороший и заботящиийся о своём чатике админ, <b>" + row[0] + "</b> пожелал всем в этом уютном чате доброго утра"
                    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML', reply_to_message_id = mes.message_id)
                    return
                request = "SELECT telegram_id FROM dspam_users ORDER BY reputation DESC LIMIT 5"
                cursor.execute(request)
                top_id = cursor.fetchone()
                if top_id[0] == mes.from_user.id:
                    response += "Человек, пользующийся практически неограниченным уважением считает своим долгом пожелать всему чату доброго утра.\nДоброе!"
                    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML', reply_to_message_id = mes.message_id)
                    return 
                else:
                    top_id = cursor.fetchone()
                    while top_id:
                        if top_id[0] == mes.from_user.id:
                            response += "\"Доброе утро!\" - медленно и с чувством произнёс <b>" + row[0] + "</b>. Его тут уважают, и он это знал"
                            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML', reply_to_message_id=mes.message_id)
                            return
                        top_id = cursor.fetchone()
                response += "Доброе утро, <b>" + row[0] + "</b>! Самое время совершать подвиги!\n"
                response += "Ваша репутация:" + str(row[1])
                bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML', reply_to_message_id=mes.message_id)

        request = "SELECT user_id, call_sign FROM dspam_users WHERE call_sign = '{0}'".format(trigger_mes.upper())
        cursor.execute(request)
        row = cursor.fetchone()
        if row:
            request = "SELECT call_sign FROM dspam_users WHERE telegram_id = '{0}'".format(mes.from_user.id)
            cursor.execute(request)
            username = cursor.fetchone()[0]
            request = "SELECT telegram_username FROM users WHERE user_id = '{0}'".format(row[0])
            cursor.execute(request)
            telegram_username = cursor.fetchone()[0]

            request = "SELECT telegram_id FROM dspam_users ORDER BY reputation DESC LIMIT 5"
            cursor.execute(request)
            top_id = cursor.fetchone()
            flag = 0
            response = ""
            if username == row[1]:
                response = "<b>" + username + "</b> пинганул сам себя. Несмотря на обыденность такого действия, было в нём что-то такое..."
                bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
                return
            if top_id[0] == mes.from_user.id:
                response += "Будучи самым уважаемым человеком на районе, <b>" + username + "</b> тихо и спокойно позвал <b>" + row[1] + "</b>.\nОн был абсолютно уверен, что его услышат\n"
                flag = 1
            else:
                top_id = cursor.fetchone()
                while top_id:
                    if top_id[0] == mes.from_user.id:
                        response += "<b>" + username + "</b> оглушительно проорал <b>" + row[1] + "</b>.\nВпрочем, его репутация была достаточно велика, чтобы он мог творить всё, что угодно\n"
                        flag = 1
                    top_id = cursor.fetchone()

            if flag == 0:
                if mes.from_user.id in get_admin_ids(bot, chat_id = -1001330929174):
                    response += "<b>" + username + "</b> весьма недвусмысленно позвал <b>" + row[1] + "</b>, намекая на то ли на свою админку, то ли на способ её получения...\n"
                else:
                    response += "<b>" + username + "</b> пинганул <b>" + row[1] + "</b>\n"
            if telegram_username:
                response += "@" + telegram_username
            else:
                response += "Но я не знаю его юзерку (и что с этим делать пока тоже)\nОбратись к @Cactiw"
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            return

    #Поиск и вывод триггеров в сообщении

    if mes.text.lower() in triggers_in:
        request = "SELECT trigger_out, type FROM triggers WHERE (chat_id = '{0}' OR chat_id = 0) AND trigger_in = '{1}'".format(mes.chat_id, trigger_mes.lower())
        cursor.execute(request)
        row = cursor.fetchone()
        if row:
            new = Trigger
            new.send_trigger(new, row[1], row[0], bot, update)

    status = 0

    # Вывод списка триггеров
    if (update.message.text.lower()) == 'список триггеров':
        mes = update.message
        request = "SELECT * FROM triggers WHERE chat_id = '{0}'".format(mes.chat_id)
        cursor.execute(request)
        row = cursor.fetchone()
        response = "<em>Локальные триггеры:</em>\n"
        while row:
            response_new = "<b>" + row[1] + '</b>\ntype = ' + str(row[2]) + ' created by ' + row[5] + ' on ' + str(row[6]) + '\n\n'
            if len(response + response_new) >= 4096:    #   Превышение лимита длины сообщения
                bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
                response = ""
            response += response_new
            row = cursor.fetchone()
        response = response + '\n\n<em>Глобальные триггеры:</em>\n'
        request = "SELECT * FROM triggers WHERE chat_id = 0"
        cursor.execute(request)
        row = cursor.fetchone()
        while row:
            response_new = "<b>" + row[1] + '</b>\ntype = ' + str(row[2]) + ' created by ' + row[5] + ' on ' + str(row[6]) + '\n\n'
            if len(response + response_new) >= 4096:
                bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
                response = ""
            response += response_new
            row = cursor.fetchone()
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


    #Статистика по пину
    #attack = update.message.text.find("⚔")
    attack = -1 # Функция вывода статистики отключена
    if attack != -1:
        global castles
        global number_battles
        global split_OSA
        global split_MTR
        global Battles_OSA
        global Battles_MTR
        Battles_OSA.seek(0)
        Battles_MTR.seek(0)
        OSA = Battles_OSA.readlines()
        MTR = Battles_MTR.readlines()
        Stats_battles_OSA = [None] * 7
        Stats_split_OSA = [None] * 7
        Stats_battles_MTR = [None] * 7
        Stats_split_MTR = [None] * 7
        for i in range (0, 7):
            Stats_battles_OSA[i] = Battles(castles[i], OSA[i].split()[0])
            Stats_split_OSA[i] = Battles(castles[i], OSA[i].split()[1])
            Stats_battles_MTR[i] = Battles(castles[i], MTR[i].split()[0])
            Stats_split_MTR[i] = Battles(castles[i], MTR[i].split()[1])
        mes = update.message.text
        first = None
        two = False
        global first_OSA
        global fisrt_MTR
        global second_OSA
        global second_MTR
        first_OSA = False
        first_MTR = False
        second_OSA = False
        second_MTR = False
        #print(mes)
        #out = mes [attack + 1] + '\n' + mes [attack + 2]
        #print(out)
        for i in range(0, 7):
            if mes[attack + 1] == castles[i]:
                first = mes[attack + 1]
                print (i)
                if i >= 3:
                    first_OSA = True
                if (i < 3) or (i == 6):
                    first_MTR = True
            if attack + 2 < len(mes):
                if mes[attack + 2] == castles[i]:
                    second = mes[attack + 2]
                    two = True
                    if i >= 3:
                        second_OSA = True
                    if (i < 3) or (i == 6):
                        second_MTR = True
        #print(first_OSA, first_MTR, second_OSA, second_MTR)

        for i in range (0, 7):
            if first_OSA:
                if first == Stats_battles_OSA[i].castle:
                    response = 'ОСА ходили в ' + first + ' ' + str(Stats_battles_OSA[i].number) + ' раз, это ' + str(int(Stats_battles_OSA[i].number) / number_battles * 100) + '% от общего количества битв,\n'
                    response = response + 'А сплитовали ОСА в ' + first + ' ' + str(Stats_split_OSA[i].number) + ' раз, что равно ' + str(int(Stats_split_OSA[i].number) / split_OSA * 100) + '% от общего количества сплитов\n'
                    bot.send_message(chat_id=update.message.chat_id, text=response)
            if first_MTR:
                if first == Stats_battles_MTR[i].castle:
                    response = 'МТР ходили в ' + first + ' ' + str(Stats_battles_MTR[i].number) + ' раз, это ' + str(int(Stats_battles_MTR[i].number) / number_battles * 100) + '% от общего количества битв,\n'
                    response = response + 'А сплитовали МТР в ' + first + ' ' + str(Stats_split_MTR[i].number) + ' раз, что равно ' + str(int(Stats_split_MTR[i].number) / split_MTR * 100) + '% от общего количества сплитов\n'
                    bot.send_message(chat_id=update.message.chat_id, text=response)
        if two:
            for i in range (0, 7):
                if second_OSA:
                   if second == Stats_battles_OSA[i].castle:
                        response = 'ОСА ходили в ' + second + ' ' + str(Stats_battles_OSA[i].number) + ' раз, это ' + str(int(Stats_battles_OSA[i].number) / number_battles * 100) + '% от общего количества битв,\n'
                        response = response + 'А сплитовали ОСА в ' + second + ' ' + str(Stats_split_OSA[i].number) + ' раз, что равно ' + str(int(Stats_split_OSA[i].number) / split_OSA * 100) + '% от общего количества сплитов\n'
                        bot.send_message(chat_id=update.message.chat_id, text=response)
                if second_MTR:
                    if second == Stats_battles_MTR[i].castle:
                        response = 'МТР ходили в ' + second + ' ' + str(Stats_battles_MTR[i].number) + ' раз, это ' + str(int(Stats_battles_MTR[i].number) / number_battles * 100) + '% от общего количества битв,\n'
                        response = response + 'А сплитовали МТР в ' + second + ' ' + str(Stats_split_MTR[i].number) + ' раз, что равно ' + str(int(Stats_split_MTR[i].number) / split_MTR * 100) + '% от общего количества сплитов\n'
                        bot.send_message(chat_id=update.message.chat_id, text=response)


    #Приём профилей
    #print(update.message.forward_from.id, update.message.chat_id)
    if (update.message.forward_from) and update.message.forward_from.id == 265204902: #and (update.message.chat_id == -1001330929174 or update.message.chat_id == 231900398  or update.message.chat_id == -1001209754716):
        #print('yes')
        mes = update.message
        is_hero = False
        if mes.text.find('Уровень:') != -1 and mes.text.find('Класс: /class') != -1:
            is_hero = True
        if is_hero:
            request = "SELECT * FROM users WHERE telegram_id = %s" % mes.from_user.id
            cursor.execute(request)
            row = cursor.fetchone()
            if row != None:
                print(row)
            if row == None: #Добавляем нового игрока
                #print(mes.text[1:].split('\n'))
                guild = None
                if mes.text[1] == '[':
                    guild = mes.text[1:].split(']')[0][1:]
                    print("yes, guild = ", guild)
                username = mes.text[1:].split('\n')[0]
                lvl = int(mes.text[mes.text.find('🏅Уровень:'):].split()[1])
                #print(mes.text.find('⚔Атака'))
                #print(mes.text[mes.text.find('⚔️Атака:'):])
                attack = int(mes.text[mes.text.find('⚔Атака:'):].split()[1])
                defense = int(mes.text[mes.text.find('⚔Атака:'):].split()[3])
                request = "INSERT INTO users(telegram_id, telegram_username, user_castle, username, guild, user_lvl, user_attack, user_defense, last_update) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')".format(mes.from_user.id, mes.from_user.username, mes.text[0], username, guild, lvl, attack, defense, time.strftime('%Y-%m-%d %H:%M:%S'))
                cursor.execute(request)
                conn.commit()
                row = cursor.fetchone()
                if row != None:
                    print(row)
                bot.send_message(chat_id=update.message.chat_id, text='Профиль успешно добавлен')
            else:
                username = mes.text[1:].split('\n')[0]
                lvl = int(mes.text[mes.text.find('🏅Уровень:'):].split()[1])
                guild = None
                if mes.text[1] == '[':
                    guild = mes.text[1:].split(']')[0][1:]
                #print(mes.text.find('⚔Атака'))
                #print(mes.text[mes.text.find('⚔️Атака:'):])
                attack = int(mes.text[mes.text.find('⚔Атака:'):].split()[1])
                defense = int(mes.text[mes.text.find('⚔Атака:'):].split()[3])
                print(mes.from_user.id, mes.text[0], username, lvl, attack, defense)
                request = "UPDATE users SET telegram_id='{0}', telegram_username = '{1}',user_castle='{2}', username='{3}', guild = '{4}', user_lvl='{5}', user_attack='{6}', user_defense='{7}', last_update='{8}' WHERE telegram_id = '{9}'".format(mes.from_user.id, mes.from_user.username,mes.text[0], username, guild, lvl, attack, defense, time.strftime('%Y-%m-%d %H:%M:%S'), mes.from_user.id)
                cursor.execute(request)
                conn.commit()
                row = cursor.fetchone()
                if row != None:
                    print(row)

                bot.send_message(chat_id=-1001197381190, text='Профиль успешно обновлён для пользователя @' + mes.from_user.username)
                try:
                    bot.send_message(chat_id=update.message.from_user.id, text='Профиль успешно обновлён')
                except TelegramError:
                    pass



    #Приём репортов
    if (update.message.forward_from) and update.message.forward_from.id == 265204902:# and (update.message.chat_id == -1001330929174 or update.message.chat_id == 231900398 or update.message.chat_id == -1001209754716): #Только для беседы ДСПАМ и чата отряда
        mes = update.message
        is_report = False
        if mes.text.find('Твои результаты в бою:') != -1:
            is_report = True
        if is_report:
            request = "SELECT * FROM users WHERE telegram_id = %s" % mes.from_user.id
            cursor.execute(request)
            row = cursor.fetchone()
            if row == None:
                try:
                    bot.send_message(chat_id=update.message.from_user.id, text='Профиль не найден в базе данных. Пожалуйста, обновите /hero')
                except TelegramError:
                    return
            else:
                #Эээээээээксперименты
                #d = datetime.datetime(2018, 5, 27, 9, 0, 0, 0)     Для нормального времени
                #c = datetime.datetime(2018, 5, 27, 1, 0, 0, 0)
                #_________________________________________________________________________________-
                d = datetime.datetime(2018, 5, 27, 7, 0, 0, 0) #8 для летнего времени
                c = datetime.datetime(2018, 5, 26, 23, 0, 0, 0)
                c = d - c
                #print(c)
                a = update.message.forward_date
                a = a - d
                battle_id = 0
                while a > c:
                    a = a - c
                    battle_id = battle_id + 1
                #print(a)
                print(battle_id)
                if mes.text[1:mes.text.find('⚔') - 1] == row[4]:
                    attack = int(mes.text[mes.text.find('⚔') + 2:].split()[0].split('(')[0])
                    defense = int(mes.text[mes.text.find('🛡') + 2:].split()[0].split('(')[0])
                    lvl = int(mes.text[mes.text.find("Lvl") + 4:].split()[0])
                    if mes.text.find("🔥Exp:") == -1:
                        exp = 0
                    else:
                        exp = int(mes.text[mes.text.find("🔥Exp:"):].split()[1])
                    if mes.text.find("💰Gold") == -1:
                        gold = 0
                    else:
                        gold = int(mes.text[mes.text.find("💰Gold"):].split()[1])
                    if mes.text.find("📦Stock") == -1:
                        stock = 0
                    else:
                        stock = int(mes.text[mes.text.find("📦Stock"):].split()[1])
                    critical = 0
                    guardian = 0
                    request = "SELECT * FROM reports WHERE user_id = '{0}' AND battle_id = '{1}'".format(row[0], battle_id)
                    cursor.execute(request)
                    response = cursor.fetchone()
                    if response != None:
                        bot.send_message(chat_id=update.message.chat_id, text='Репорт за эту битву уже учтён!')
                    else:
                        #print(mes.text)
                        #print (mes.text.find('⚡Critical strike'))
                        additional_attack = 0
                        additional_defense = 0
                        if mes.text.find('⚡Critical strike') != -1:
                            critical = 1
                            additional_attack = int(mes.text[mes.text.find('+') + 1:mes.text.find(')')])
                        elif mes.text.find('🔱Guardian angel') != -1:
                            guardian = 1
                            additional_defense = int(mes.text[mes.text.find('+') + 1:mes.text.find(')')])

                        request = "INSERT INTO reports(user_id, battle_id, date_in, report_attack, report_defense," \
                                  " report_lvl, report_exp, report_gold, report_stock, critical_strike, guardian_angel," \
                                  " additional_attack, additional_defense) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}'," \
                                  " '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}')".format(row[0], battle_id, time.strftime('%Y-%m-%d %H:%M:%S'), attack, defense, lvl, exp, gold, stock, critical, guardian, additional_attack, additional_defense)
                        cursor.execute(request)
                        conn.commit()
                        row = cursor.fetchone()

                        bot.send_message(chat_id=-1001197381190, text='Репорт успешно учтён для пользователя @' + mes.from_user.username)
                        try:
                            bot.send_message(chat_id=update.message.from_user.id, text='Репорт учтён. Спасибо!')
                        except TelegramError:
                            pass
                        if row != None:
                            print(row)
                else:
                    try:
                        bot.send_message(chat_id=update.message.from_user.id, text='Это не ваш репорт. В случае возникновения ошибок обновите профиль')
                    except TelegramError:
                        return


class user_stats:
    def __init__(self, username, exp, gold, stock):
        self.username = username
        self.gold = gold
        self.exp = exp
        self.stock = stock


def stats_send(bot, update):
    b = datetime.time(16, 0, 0, 0)  #Вернуть на 17 (18-1) #16 зимой
    b = datetime.datetime.combine(datetime.date.today(), b)
    a = datetime.datetime.now()

    a = a - b
            #print(a)
    d = datetime.datetime(2018, 5, 27, 9, 0, 0, 0)
    c = datetime.datetime(2018, 5, 27, 7, 0, 0, 0)# Разница в 1 час (2 зимой)
    c = d - c
    print(a)
    print(c)
    zero = c - c
    if a <= c and a > zero:
        #Обработка статистики
        d = datetime.datetime(2018, 5, 27, 9, 0, 0, 0)
        c = datetime.datetime(2018, 5, 27, 1, 0, 0, 0)
        c = d - c
                #print(c)
        a = datetime.datetime.now()
        a = a - d
        battle_id = 0
        while a > c:
            a = a - c
            battle_id = battle_id + 1
        print(battle_id)
        request = 'SELECT COUNT(1) FROM users'
        cursor.execute(request)
        num_users = cursor.fetchone()[0]
        request = 'SELECT username FROM users'
        cursor.execute(request)
        rows = cursor.fetchall()
        users = [None] * num_users
        for i in range (0, num_users):
            request = "SELECT report_exp, report_gold, report_stock FROM reports WHERE battle_id > '{0}' AND user_id = '{1}'".format((battle_id - 3), i + 1)
            cursor.execute(request)
            response = cursor.fetchone()
            users[i] = user_stats(rows[i][0], 0, 0, 0)
            while response:
                users[i].exp = users[i].exp + response[0]
                users[i].gold = users[i].gold + response[1]
                users[i].stock = users[i].stock + response[2]
                response = cursor.fetchone()
        users_by_gold = sorted(users, key = lambda user_stats : user_stats.gold, reverse = True)
        users_by_exp = sorted(users, key = lambda user_stats : user_stats.exp, reverse = True)
        users_by_stock = sorted(users, key = lambda user_stats : user_stats.stock, reverse = True)
        #print(users_by_gold[0])
        response = 'Топ пользователей за сутки:\n\n'
        response_gold = '\n\nПо добытому золоту:'
        response_exp = '\n\nПо опыту в битвах:'
        response_stock = '\n\nПо украденному стоку:'
        for i in range (0, num_users):
            response_gold = response_gold + '\n' + str(i + 1) + ': ' + '*' + str(users_by_gold[i].username) + '*' + ' ' + str(users_by_gold[i].gold) + '💰'
            response_exp = response_exp + '\n' + str(i + 1) + ': ' + '*' + str(users_by_exp[i].username) + '*' + ' ' + str(users_by_exp[i].exp) + '🔥'
            response_stock = response_stock + '\n' + str(i + 1) + ': ' + '*' + str(users_by_stock[i].username) + '*' + ' ' + str(users_by_stock[i].stock) + '📦'
        response = response + response_gold + response_exp + response_stock
        #bot.send_message(chat_id = -1001330929174, text = response, parse_mode = 'Markdown')
        #bot.send_message(chat_id = 231900398, text = response, parse_mode = 'Markdown')
        print("YES")



def stats_count(bot, update):
    data = stats.get(update.message.chat_id)
    if data is None:
        title = update.message.chat.title
        if title is None:
            title = update.message.chat.username
        data = ChatStats(update.message.chat_id, title, 0, 0, 0, 0, 0, 0, 0, 0)
        data.update_from_database()
        stats.update({update.message.chat_id : data})
    data.process_message(update.message)
    data = stats.get(0)
    data.process_message(update.message)


def cache_full():
    triggers_in.clear()
    __request = "select trigger_in from triggers"
    cursor.execute(__request)
    row = cursor.fetchone()
    while row:
        triggers_in.append(row[0])

        row = cursor.fetchone()
    #print(triggers_in)
    return



# Открываем файлы
Battles_OSA = open('Battles_OSA.txt', 'r')
Battles_MTR = open('Battles_MTR.txt', 'r')
OSA = Battles_OSA.readlines()
MTR = Battles_MTR.readlines()
global number_battles
global split_OSA
global split_MTR
number_battles = 0
split_OSA = 0
split_MTR = 0
for i in range (0, 7):
    number_battles = number_battles + int(OSA[i].split()[0])
    split_OSA = split_OSA + int(OSA[i].split()[1])
    split_MTR = split_MTR + int(MTR[i].split()[1])
print ('Количество битв в статистике', number_battles)
print ('Количество сплитов у ОСА', split_OSA, '\nКоличество сплитов у МТР', split_MTR)


class Filter_pinset(BaseFilter):
    def filter(self, message):
        return 'pinset' in message.text

filter_pinset = Filter_pinset()

class Filter_pinpin(BaseFilter):
    def filter(self, message):
        return 'pinpin' in message.text

filter_pinpin = Filter_pinpin()


class Filter_pinmute(BaseFilter):
    def filter(self, message):
        return 'pinmute' in message.text

filter_pinmute = Filter_pinmute()


# Хендлеры
start_command_handler = CommandHandler('start', startCommand)

attack_command_handler = CommandHandler('⚔', attackCommand, filters=(Filters.user(user_id = 498377101) |Filters.user(user_id = 231900398)))
add_pin_command_handler = CommandHandler('add_pin', add_pin, filters=Filters.user(user_id = 231900398))
pin_setup_command_handler = CommandHandler('pin_setup', pin_setup, filters=Filters.user(user_id = 231900398))
pinset_command_handler = MessageHandler(Filters.command & filter_pinset & Filters.user(user_id = 231900398), pinset)
pinpin_command_handler = MessageHandler(Filters.command & filter_pinpin & Filters.user(user_id = 231900398), pinpin)
pinmute_command_handler = MessageHandler(Filters.command & filter_pinmute & Filters.user(user_id = 231900398), pinmute)

add_silent_command_handler = CommandHandler('add_silent', add_silent,filters = Filters.user(user_id = 231900398))
silent_setup_command_handler = CommandHandler('silent_setup', silent_setup,filters = Filters.user(user_id = 231900398), pass_job_queue = True)
silent_start_command_handler = CommandHandler('silent_start', silent_start, filters = Filters.user(user_id = 231900398), pass_job_queue = True)
silent_stop_command_handler = CommandHandler('silent_stop', silent_stop, filters = Filters.user(user_id = 231900398), pass_job_queue = True)

class Filter_silentdelete(BaseFilter):
    def filter(self, message):
        return silent_delete and message.chat_id in silent_chats

filter_silentdelete = Filter_silentdelete()


class Filter_sil_run(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'sil_run' in message.text
        return 0

filter_sil_run = Filter_sil_run()

silent_delete_command_handler = MessageHandler(filter_silentdelete, silent_delete_message)
sil_run_command_handler = MessageHandler(filter_sil_run, sil_run)

menu_command_handler = CommandHandler('menu', menuCommand, filters=(Filters.user(user_id = 498377101) | Filters.user(user_id = 231900398)))

info_command_handler = CommandHandler('info', infoCommand)

add_admin_command_handler = CommandHandler('add_admin', add_admin,filters=Filters.user(user_id = 231900398))
add_trigger_handler = CommandHandler('add_trigger', add_trigger)
add_global_trigger_handler = CommandHandler('add_global_trigger', add_global_trigger, filters=(Filters.user(user_id = 231900398) & Filters.chat(chat_id = 231900398)))
remove_trigger_handler = CommandHandler('remove_trigger', remove_trigger)

class Filter_pr(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'pr_' in message.text
        return 0

filter_pr = Filter_pr()

class Filter_rank(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/rank_' in message.text
        return 0

filter_rank = Filter_rank()

class Filter_edit_rank(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/edit_rank_' in message.text
        return 0

filter_edit_rank = Filter_edit_rank()

class Filter_r_set_name(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/r_set_name' in message.text
        return 0

filter_r_set_name = Filter_r_set_name()

class Filter_r_set_description(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/r_set_description' in message.text
        return 0

filter_r_set_description = Filter_r_set_description()

class Filter_r_set_unique(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/r_set_unique' in message.text
        return 0

filter_r_set_unique = Filter_r_set_unique()


class Filter_del_rank(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/del_rank_' in message.text
        return 0

filter_del_rank = Filter_del_rank()

profile_handler = CommandHandler('profile', profile)

pr_handler = MessageHandler(Filters.command & filter_pr, pr)
rank_list_handler = CommandHandler('rank_list', rank_list, pass_args=True)
rank_handler = MessageHandler(Filters.command & filter_rank, rank)
set_rank_handler = CommandHandler('set_rank', set_rank, pass_args=True)
edit_rank_handler = MessageHandler(Filters.command & filter_edit_rank, edit_rank)
del_rank_handler = MessageHandler(Filters.command & filter_del_rank, del_rank)
add_rank_handler = CommandHandler('add_rank', add_rank)

r_set_name_handler = MessageHandler(Filters.command & filter_r_set_name, r_set_name)
r_set_description_handler = MessageHandler(Filters.command & filter_r_set_description, r_set_description)
r_set_unique_handler = MessageHandler(Filters.command & filter_r_set_unique, r_set_unique)


reg_handler = CommandHandler('reg', reg , filters = Filters.chat(chat_id = -1001330929174))
set_call_sign_handler = CommandHandler('set_call_sign', set_call_sign, pass_args=True)
force_call_sign_handler = CommandHandler('force_call_sign', force_call_sign, pass_args=True)

dspam_list_handler = CommandHandler('dspam_list', dspam_list)


class Filter_confirm(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'confirm' in message.text
        return 0

filter_confirm = Filter_confirm()


class Filter_reject(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'reject' in message.text
        return 0


filter_reject = Filter_reject()

requests_handler = CommandHandler('requests', requests)

confirm_handler = MessageHandler(Filters.command & filter_confirm, confirm)
reject_handler = MessageHandler(Filters.command & filter_reject, reject)



setdr_handler = CommandHandler('setdr', setdr)
dr_handler = CommandHandler('dr', dr)

g_info_handler = CommandHandler('g_info', g_info,filters=Filters.user(user_id = 231900398))
g_all_attack_handler = CommandHandler('g_all_attack', g_all_attack,filters=Filters.user(user_id = 231900398))
g_attack_handler = CommandHandler('g_attack', g_attack,filters=Filters.user(user_id = 231900398))
g_help_handler = CommandHandler('g_help', g_help)


battle_history_handler = CommandHandler('battle_history', battle_history)
add_battle_handler = CommandHandler('add_battle', add_battle,filters=Filters.user(user_id = 231900398))
battles_stats_handler = CommandHandler('battles_stats', battles_stats)

text_message_handler = MessageHandler(Filters.text, textMessage)
stats_send_handler = CommandHandler('stats_send', stats_send)
# Добавляем хендлеры в диспетчер
dispatcher.add_handler(start_command_handler)

dispatcher.add_handler(attack_command_handler)
dispatcher.add_handler(add_pin_command_handler)
dispatcher.add_handler(pin_setup_command_handler)
dispatcher.add_handler(pinset_command_handler)
dispatcher.add_handler(pinpin_command_handler)
dispatcher.add_handler(pinmute_command_handler)

dispatcher.add_handler(CommandHandler('mute', mute, pass_args=True))

dispatcher.add_handler(silent_setup_command_handler)
dispatcher.add_handler(add_silent_command_handler)
dispatcher.add_handler(silent_start_command_handler)
dispatcher.add_handler(silent_stop_command_handler)

dispatcher.add_handler(silent_delete_command_handler)
dispatcher.add_handler(sil_run_command_handler)


dispatcher.add_handler(menu_command_handler)

dispatcher.add_handler(info_command_handler)

dispatcher.add_handler(add_admin_command_handler)
dispatcher.add_handler(add_trigger_handler)
dispatcher.add_handler(add_global_trigger_handler)
dispatcher.add_handler(remove_trigger_handler)


dispatcher.add_handler(profile_handler)
dispatcher.add_handler(pr_handler)
dispatcher.add_handler(rank_list_handler)
dispatcher.add_handler(rank_handler)
dispatcher.add_handler(set_rank_handler)
dispatcher.add_handler(edit_rank_handler)
dispatcher.add_handler(add_rank_handler)
dispatcher.add_handler(del_rank_handler)


dispatcher.add_handler(r_set_name_handler)
dispatcher.add_handler(r_set_description_handler)
dispatcher.add_handler(r_set_unique_handler)



dispatcher.add_handler(reg_handler)
dispatcher.add_handler(set_call_sign_handler)
dispatcher.add_handler(force_call_sign_handler)

dispatcher.add_handler(dspam_list_handler)



dispatcher.add_handler(requests_handler)
dispatcher.add_handler(confirm_handler)
dispatcher.add_handler(reject_handler)



dispatcher.add_handler(setdr_handler)
dispatcher.add_handler(dr_handler)

dispatcher.add_handler(g_info_handler)
dispatcher.add_handler(g_attack_handler)
dispatcher.add_handler(g_all_attack_handler)
dispatcher.add_handler(g_help_handler)
dispatcher.add_handler(CommandHandler("g_add_attack", g_add_attack, filters=(Filters.user(user_id=231900398)  | Filters.user(user_id = 116028074))))  #116028074
dispatcher.add_handler(CommandHandler("g_del_attack", g_del_attack, filters=(Filters.user(user_id=231900398)  | Filters.user(user_id = 116028074))))
dispatcher.add_handler(CommandHandler("g_attacking_list", g_attacking_list, filters=(Filters.user(user_id=231900398)  | Filters.user(user_id = 116028074))))
dispatcher.add_handler(CommandHandler("g_add_defense", g_add_defense, filters=(Filters.user(user_id=231900398)  | Filters.user(user_id = 116028074))))
dispatcher.add_handler(CommandHandler("g_del_defense", g_del_defense, filters=(Filters.user(user_id=231900398)  | Filters.user(user_id = 116028074))))
dispatcher.add_handler(CommandHandler("g_defending_list", g_defending_list, filters=(Filters.user(user_id=231900398)  | Filters.user(user_id = 116028074))))



dispatcher.add_handler(battle_history_handler)
dispatcher.add_handler(add_battle_handler)
dispatcher.add_handler(battles_stats_handler)

dispatcher.add_handler(CommandHandler("sql", sql, pass_user_data = True, filters=Filters.user(user_id=231900398)))

class Filter_View_Playlist(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'view_playlist_' in message.text
        return 0


filter_view_playlist = Filter_View_Playlist()

class Filter_Play_Song(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'play_song' in message.text
        return 0


filter_play_song = Filter_Play_Song()

class Filter_Remove_Song(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'remove_song' in message.text
        return 0


filter_remove_song = Filter_Remove_Song()

class Filter_Play_Random_From_Playlist(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'play_random_from_playlist' in message.text
        return 0


filter_play_random_from_playlist = Filter_Play_Random_From_Playlist()

dispatcher.add_handler(CommandHandler("add_playlist", add_playlist, pass_args=True))
dispatcher.add_handler(CommandHandler("list_playlists", list_playlists))
dispatcher.add_handler(CommandHandler("add_to_playlist", add_to_playlist, pass_args=True))
dispatcher.add_handler(CommandHandler("play_random_from_playlist", play_random_from_playlist, pass_args=True))
dispatcher.add_handler(MessageHandler(Filters.command & filter_play_random_from_playlist, play_random_from_playlist))
dispatcher.add_handler(MessageHandler(Filters.command & filter_view_playlist, view_playlist))
dispatcher.add_handler(MessageHandler(Filters.command & filter_play_song, play_song))
dispatcher.add_handler(MessageHandler(Filters.command & filter_remove_song, remove_song))

dispatcher.add_handler(CommandHandler("stats", battle_stats_send, filters=Filters.user(user_id=231900398)))

dispatcher.add_handler(CommandHandler("todo", todo, filters=Filters.user(user_id=231900398)))
dispatcher.add_handler(CommandHandler("todo_list", todo_list, filters=Filters.user(user_id=231900398)))
dispatcher.add_handler(MessageHandler(Filters.command & filter_complete_todo, complete_todo))







dispatcher.add_handler(MessageHandler(filter_any_message, stats_count), group=1)
dispatcher.add_handler(CommandHandler("chat_stats", chat_stats_send, filters=Filters.user(user_id=231900398)))
dispatcher.add_handler(CommandHandler("current_chat_stats", current_chat_stats_send, filters=Filters.user(user_id=231900398)))



dispatcher.add_handler(text_message_handler)

dispatcher.add_handler(stats_send_handler)


cache_full()


# Начинаем поиск обновлений
updater.start_polling(clean=False)
job = updater.job_queue
#job_stats = job.run_repeating(stats_send, interval=(1*60*60), first=0) #Рассылка статистики - отключена на текущий момент //TODO починить статистику
#global silent_running = 1
job_silence = job.run_once(empty, 0)
#threading.Thread(target=stats_send).start()

# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
# Загружаем необновлённую статистику в базу данных
update_chat_stats()

# Разрываем подключение.
conn.close()
#print("COMPLETED, FEEL SAFE TO CLOSE THE BOT")
