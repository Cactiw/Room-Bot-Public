# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter


from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

import logging

import time
import pytz
import datetime
import threading

import sys

from psycopg2 import ProgrammingError

from work_materials.globals import *
from libs.chat_stats import *
from libs.trigger import *
from libs.guild_reports_stats import  *

from libs.filters.todo import *
from libs.filters.playlist import *
from libs.filters.dspam_filters import *
from libs.filters.silent import *
from libs.filters.pin import *

from bin.pin import *
from bin.silent import *
from bin.trigger import *
from bin.chat_stats import *
from bin.todo import *
from bin.playlist import *
from bin.dspam import *
from bin.guild import *

#--------------------------------------------------------------     Выставляем логгирование
console = logging.StreamHandler()
console.setLevel(logging.INFO)

log_file = logging.FileHandler(filename='error.log', mode='a')
log_file.setLevel(logging.ERROR)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO, handlers=[log_file, console])
#--------------------------------------------------------------

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



# Обработка команд
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Привет, давай пообщаемся?')


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



def infoCommand(bot, update):
    mes = update.message
    if update.message.reply_to_message is None:
        return
    response = 'message_id = <b>' + str(update.message.reply_to_message.message_id) + '</b>\n'
    response = response + 'text: ' + str(update.message.reply_to_message.text) + '\n'
    response = response + 'chat_id = <b>' + str(update.message.reply_to_message.chat.id) + '</b>\n'
    response = response + 'message from:\n   username: <b>' + str (update.message.reply_to_message.from_user.username) + \
               '</b>\n   id: <b>' + str(update.message.reply_to_message.from_user.id) + '</b>\n'
    try:
        message_date = local_tz.localize(update.message.reply_to_message.date)
    except ValueError:
        try:
            message_date = update.message.reply_to_message.date.astimezone(tz=pytz.timezone('Europe/Moscow'))
        except ValueError:
            message_date = update.message.reply_to_message.date

    response = response + 'date: <b>' + str(message_date) + ' (Europe/Moscow)</b>\n'
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

    if update.message.reply_to_message.forward_from is not None:
        response = response + 'forward from: <b>' + str(update.message.reply_to_message.forward_from) + '</b>\n'
    try:
        try:
            forward_message_date = local_tz.localize(update.message.reply_to_message.forward_date)
        except ValueError:
            try:
                forward_message_date = update.message.reply_to_message.forward_date.astimezone(tz=pytz.timezone('Europe/Moscow'))
            except ValueError:
                forward_message_date = update.message.reply_to_message.forward_date
        response = response + 'forward date: <b>' + \
                   str(forward_message_date) + ' (Europe/Moscow)</b>\n'
    except AttributeError:
        pass
    #response = response + 'message text: ' + str(update.message.reply_to_message.text) + '\n'
    #response = response + 'date: ' + str(update.message.reply_to_message.date) + '\n'
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode = 'HTML')



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
    row = None
    try:
        row = cursor.fetchone()
    except ProgrammingError:
        bot.send_message(chat_id=mes.chat_id, text="Пустой ответ. Успешная операция, или таких строк не найдено")
        return
    response = ""
    while row:
        for i in range(0, len(row)):
            response += str(row[i]) + " "
        row = cursor.fetchone()
        response += "\n\n"
    if response == "":
        bot.send_message(chat_id=mes.chat_id, text="Не найдено")
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
                d = datetime.datetime(2018, 5, 27, 9, 0, 0, 0)  #   Для нормального времени
                c = datetime.datetime(2018, 5, 27, 1, 0, 0, 0)
                #_________________________________________________________________________________-
                ###d = datetime.datetime(2018, 5, 27, 7, 0, 0, 0) #8 для летнего времени    # Без плясок с временными зонами
                ###c = datetime.datetime(2018, 5, 26, 23, 0, 0, 0)
                c = d - c
                #print(c)
                try:
                    forward_message_date = local_tz.localize(update.message.forward_date).replace(
                            tzinfo=None)
                except ValueError:
                    print("value error")
                    try:
                        forward_message_date = update.message.forward_date.astimezone(
                            tz=pytz.timezone('Europe/Moscow')).replace(
                            tzinfo=None)
                    except ValueError:
                        forward_message_date = update.message.forward_date
                print(forward_message_date)
                a = forward_message_date - d
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

                        bot.send_message(chat_id=-1001197381190, text='Репорт успешно учтён для пользователя @' + mes.from_user.username)
                        try:
                            bot.send_message(chat_id=update.message.from_user.id, text='Репорт учтён. Спасибо!')
                        except TelegramError:
                            pass
                        now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).replace(
                            tzinfo=None) - datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=0))
                        if now < datetime.timedelta(hours=1, minutes=10):
                            remaining_time = datetime.timedelta(hours=1, minutes=10) - now
                            time_from_battle = datetime.timedelta(hours=8) - remaining_time
                            print("interval =", (datetime.timedelta(hours=1, minutes=10) - now))
                        else:
                            time_from_battle = now - datetime.timedelta(hours=1, minutes=10)
                            while time_from_battle > datetime.timedelta(hours=8):
                                time_from_battle -= datetime.timedelta(hours=8)

                        time_from_receiving_report = datetime.datetime.now() - forward_message_date

                        if time_from_receiving_report < time_from_battle:
                            #   Репорт с последней битвы
                            if mes.text.find("]") > 0:
                                guild_tag = str(mes.text[2:mes.text.find(']')].upper())
                                print(guild_tag)
                                guild_reports = reports_count.get(guild_tag)
                                if guild_reports is None:
                                    guild_reports = GuildReports(guild_tag)
                                current_report = Report(mes.from_user.id, mes.text[0], mes.text[1:].partition('⚔')[0], lvl, exp, gold, stock, attack, defense)
                                guild_reports.add_report(current_report)
                                reports_count.update({guild_tag : guild_reports})
                                chat_id = guilds_chat_ids.get(guild_tag)
                                if chat_id is not None:
                                    percent = (guild_reports.num_reports / guild_reports.num_players) * 100
                                    response = "Репорт от <b>{0}</b> принят.\nВсего сдало репортов <b>{1}</b> человек, это <b>{2:.2f}</b>% " \
                                               "от общего числа\n".format(current_report.nickname, guild_reports.num_reports, percent)
                                    if percent == 100:
                                        response += "Все сдали репорты! Какие вы лапочки!"

                                    else:
                                        if time_from_battle > datetime.timedelta(hours = 1):
                                            response += "Всё ещё не сдали репорты:\n"
                                            for user in guild_reports.users:
                                                if not user.report_sent:
                                                    response += "<b>{0}</b>,    ".format(user.username)
                                    try:
                                        bot.sync_send_message(chat_id = chat_id, text = response, parse_mode = 'HTML')
                                    except TelegramError:
                                        bot.send_message(chat_id = admin_ids[0], text = response, parse_mode = 'HTML')

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

silent_delete_command_handler = MessageHandler(filter_silentdelete, silent_delete_message)
sil_run_command_handler = MessageHandler(filter_sil_run, sil_run)

menu_command_handler = CommandHandler('menu', menuCommand, filters=(Filters.user(user_id = 498377101) | Filters.user(user_id = 231900398)))

info_command_handler = CommandHandler('info', infoCommand)

add_admin_command_handler = CommandHandler('add_admin', add_admin,filters=Filters.user(user_id = 231900398))
add_trigger_handler = CommandHandler('add_trigger', add_trigger)
add_global_trigger_handler = CommandHandler('add_global_trigger', add_global_trigger, filters=(Filters.user(user_id = 231900398) & Filters.chat(chat_id = 231900398)))
remove_trigger_handler = CommandHandler('remove_trigger', remove_trigger)



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
bot.send_message(chat_id = admin_ids[0], text = "Бот запущен.\nНе забудьте запустить тишину!: /silent_start")
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
