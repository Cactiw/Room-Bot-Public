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
import traceback

import sys
from multiprocessing import Process

from psycopg2 import ProgrammingError

from work_materials.globals import *
from libs.chat_stats import *
from libs.trigger import *
from libs.guild_reports_stats import  *

from libs.filters.service_filters import *
from libs.filters.todo import *
from libs.filters.playlist import *
from libs.filters.dspam_filters import *
from libs.filters.silent import *
from libs.filters.pin import *
from libs.filters.mute_filters import *
from libs.filters.class_filters import filter_set_class
from libs.filters.guild_filters import filter_guild_list
from libs.filters.chat_wars_filters import filter_hero, filter_report

from bin.pin import *
from bin.silent import *
from bin.trigger import *
from bin.chat_stats import *
from bin.todo import *
from bin.playlist import *
from bin.dspam import *
from bin.guild import *
from bin.mute import *
from bin.class_func import set_class, knight_critical, sentinel_critical
from bin.help import bot_help, dspam_help
from bin.calculate import calculate_pogs
from bin.stickers import create_sticker_set, send_sticker_emoji
from bin.chat_wars import add_hero, add_report
from bin.telethon_script import script_work
from bin.stats_parse_monitor import parse_stats

from bin.test import message_test

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

status = 0
globalstatus = 0


def empty(bot, update): #Пустая функия для объявления очереди
    return 0


# Обработка команд
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Привет, давай пообщаемся?')


def mute(bot, update, args):
    mes = update.message
    if (mes.from_user.id != SUPER_ADMIN_ID) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        return
    if mes.reply_to_message is None:
        return
    if mes.reply_to_message.from_user.id == SUPER_ADMIN_ID:
        bot.send_message(chat_id=update.message.chat_id, text='Банить своего создателя я не буду!')
        return
    if not args:
        return
    current = time.time()
    print(current)
    ban_for = (float(args[0]) * 60)
    current += ban_for
    print(current)
    try:
        bot.restrictChatMember(chat_id=mes.chat_id, user_id = mes.reply_to_message.from_user.id, until_date=current)
    except TelegramError:
        bot.send_message(chat_id=update.message.chat_id, text='Бот не имеет требуемые права, или неправильный формат времени')
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
        message_date = local_tz.localize(update.message.reply_to_message.date).astimezone(tz=pytz.timezone('Europe/Moscow'))
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
            forward_message_date = local_tz.localize(update.message.reply_to_message.forward_date).astimezone(tz=pytz.timezone('Europe/Moscow'))
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
    request = "SELECT * FROM admins WHERE user_id = %s"
    cursor.execute(request, (mes.reply_to_message.from_user.id,))
    row = cursor.fetchone()
    if row:
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка. Админ уже существует')
    else:
        request = "INSERT INTO admins(user_id, user_name) VALUES (%s, %s)"
        cursor.execute(request, (mes.reply_to_message.from_user.id, mes.reply_to_message.from_user.username))
        conn.commit()

        response = 'Админ добавлен'
        bot.send_message(chat_id=update.message.chat_id, text=response)


def profile(bot, update):#Вывод профиля
    mes = update.message
    request = "SELECT * FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
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

        response = 'Профиль отсутствует, пожалуйста, пришлите мне /hero'
        bot.send_message(chat_id=update.message.chat_id, text=response)


def setdr(bot, update):#Задание дня рождения
    mes = update.message #/setdr mm-dd

    request = "SELECT * FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        response = "Пользователь не найден, обновите /hero"
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
        return

    a = mes.text[7:]
    a = '2000-' + a
    request = "UPDATE users SET birthday = %s WHERE telegram_id = %s"
    cursor.execute(request, (a, mes.from_user.id))
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
    current = time.strftime('%Y-%m-%d')
    current_list = current.split("-")
    current_date = datetime.date(int(2000), int(current_list[1]), int(current_list[2]))
    none_date = datetime.date(int(1999), int(current_list[1]), int(current_list[2]))
    users = [Dr_user(None, None)] * num_users
    print(num_users)
    i = 0
    while row:
        a = row[0]
        if a is None:
            delta = none_date - current_date
            print(delta)
        else:
            delta = a - current_date

        users[i] = Dr_user(row[1], delta)

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
            request = "SELECT birthday FROM users WHERE username = %s"
            cursor.execute(request, (users_by_dr[i].username,))
            row = cursor.fetchone()
            date = str(row[0])[5:].split("-")
            response = "Сегодня день рождения никто не празднует, однако ближайший день рождения у <b>{0}</b>, готовим поздравления к <b>{1}</b>\nЭто через <b>{2}</b>".format(users_by_dr[i].username, date[1] + '/' + date[0], users_by_dr[i].delta)
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            return


def battle_history(bot, update):
    mes = update.message
    request = "SELECT user_id FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    request = "SELECT battle_id, date_in, report_attack, report_defense, report_lvl, report_exp, report_gold, report_stock, critical_strike, guardian_angel FROM reports WHERE user_id = %s ORDER BY battle_id"
    cursor.execute(request, (row[0],))
    row = cursor.fetchone()
    response = '' 'История битв по внесённым репортам:'
    while row:
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
    except Exception:
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


def send_trigger_list(bot, update):
    mes = update.message
    request = "SELECT * FROM triggers WHERE chat_id = %s"
    cursor.execute(request, (mes.chat_id,))
    row = cursor.fetchone()
    types = {0: "text", 1: "video", 2: "audio", 3: "photo", 4: "document", 5: "sticker", 6: "voice"}
    response = "<em>Локальные триггеры:</em>\n"
    while row:
        response_new = "<b>" + row[1] + '</b>\ntype = ' + str(types.get(row[2])) + ', created by ' + row[
            5] + ' on ' + str(row[6]) + '\n\n'
        if len(response + response_new) >= 4096:  # Превышение лимита длины сообщения
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()
    response = response + '\n\n<em>Глобальные триггеры:</em>\n'
    request = "SELECT * FROM triggers WHERE chat_id = 0"
    cursor.execute(request)
    row = cursor.fetchone()
    while row:
        response_new = "<b>" + row[1] + '</b>\ntype = ' + str(row[2]) + ' created by ' + row[5] + ' on ' + str(
            row[6]) + '\n\n'
        if len(response + response_new) >= 4096:
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def textMessage(bot, update):
    #Обработка триггеров и всего остального
    global status
    global globalstatus
    if (status):
        globalstatus = 1
    mes = update.message

    if (update.message.text.lower()) == 'статус':
        if (globalstatus):
            bot.send_message(chat_id=update.message.chat_id, text='Бот функционирует, зафиксированы некритичные ошибки ' + '\n' + time.ctime())

        else:
            bot.send_message(chat_id=update.message.chat_id, text='Система функционирует нормально, ошибок не зафиксировано' + '\n' + time.ctime()) #   TODO сделать нормальный статус

    trigger_mes = mes.text.translate({ord(c): None for c in '\''})

    # Обработка специальных триггеров

    if mes.chat_id == DSPAM_CHAT_ID:
        if dspam_text_message(bot, update, trigger_mes) == 0:
            return

    # Поиск и вывод триггеров в сообщении

    if mes.text.lower() in triggers_in:
        request = "SELECT trigger_out, type FROM triggers WHERE (chat_id = %s OR chat_id = 0) AND trigger_in = %s"
        cursor.execute(request, (mes.chat_id, trigger_mes.lower()))
        row = cursor.fetchone()
        if row:
            new = Trigger
            new.send_trigger(new, row[1], row[0], bot, update)

    status = 0

    # Вывод списка триггеров
    if update.message.text.lower() == 'список триггеров':
        send_trigger_list(bot, update)
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
            request = "SELECT report_exp, report_gold, report_stock FROM reports WHERE battle_id > %s AND user_id = %s"
            cursor.execute(request, ((battle_id - 3), i + 1))
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
        #bot.send_message(chat_id = SUPER_ADMIN_ID, text = response, parse_mode = 'Markdown')
        print("YES")


def reports_sent_restore():
    d = datetime.datetime(2018, 5, 27, 9, 0, 0, 0)
    c = datetime.timedelta(hours=8)
    now = datetime.datetime.now(tz = moscow_tz).replace(tzinfo=None)
    a = now - d
    battle_id = 0
    while a > c:
        a = a - c
        battle_id = battle_id + 1
    logging.info("restoring reports with battle_id = {0}".format(battle_id))

    request = "select user_id, report_attack, report_defense, report_lvl, report_exp, report_gold, report_stock, " \
              "date_in from reports where battle_id = %s"
    cursor.execute(request, (battle_id,))
    row = cursor.fetchone()
    while row is not None:
        request = "select telegram_id, user_castle, username, guild from users where user_id = %s"
        cursor_2.execute(request, (row[0],))
        row2 = cursor_2.fetchone()

        if row2 is None:
            row = cursor.fetchone()
            continue
        guild_tag = row2[3]
        logging.debug("guild_tag = {0}".format(guild_tag))
        if guild_tag == 'None':
            row = cursor.fetchone()
            continue

        current_report = Report(row2[0], row2[1], row2[2], row[3], row[4], row[5], row[6], row[1], row[2], row[7])
        guild_reports = reports_count.get(guild_tag)
        if guild_reports is None:
            guild_reports = GuildReports(guild_tag)
        guild_reports.add_report(current_report)
        reports_count.update({guild_tag: guild_reports})
        logging.debug(str(guild_reports.num_reports))

        row = cursor.fetchone()

    logging.info("reports restoring complete")


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


if len(sys.argv) > 1 and sys.argv[1] == '-t':
    message_test()


# Хендлеры
start_command_handler = CommandHandler('start', startCommand)
try:
    attack_command_handler = CommandHandler('⚔', attackCommand, filters=(Filters.user(user_id = 498377101) |Filters.user(user_id = SUPER_ADMIN_ID)))
except ValueError:
    pass
add_pin_command_handler = CommandHandler('add_pin', add_pin, filters=Filters.user(user_id = SUPER_ADMIN_ID))
pin_setup_command_handler = CommandHandler('pin_setup', pin_setup, filters=Filters.user(user_id = SUPER_ADMIN_ID))
pinset_command_handler = MessageHandler(Filters.command & filter_pinset & Filters.user(user_id = SUPER_ADMIN_ID), pinset)
pinpin_command_handler = MessageHandler(Filters.command & filter_pinpin & Filters.user(user_id = SUPER_ADMIN_ID), pinpin)
pinmute_command_handler = MessageHandler(Filters.command & filter_pinmute & Filters.user(user_id = SUPER_ADMIN_ID), pinmute)

add_silent_command_handler = CommandHandler('add_silent', add_silent,filters = Filters.user(user_id = SUPER_ADMIN_ID))
silent_setup_command_handler = CommandHandler('silent_setup', silent_setup,filters = Filters.user(user_id = SUPER_ADMIN_ID), pass_job_queue = True)
silent_start_command_handler = CommandHandler('silent_start', silent_start, filters = Filters.user(user_id = SUPER_ADMIN_ID), pass_job_queue = True)
silent_stop_command_handler = CommandHandler('silent_stop', silent_stop, filters = Filters.user(user_id = SUPER_ADMIN_ID), pass_job_queue = True)

silent_delete_command_handler = MessageHandler(filter_silentdelete, silent_delete_message)
sil_run_command_handler = MessageHandler(filter_sil_run, sil_run)

menu_command_handler = CommandHandler('menu', menuCommand, filters=(Filters.user(user_id = 498377101) | Filters.user(user_id = SUPER_ADMIN_ID)))

info_command_handler = CommandHandler('info', infoCommand)

add_admin_command_handler = CommandHandler('add_admin', add_admin,filters=Filters.user(user_id = SUPER_ADMIN_ID))
add_trigger_handler = CommandHandler('add_trigger', add_trigger)
add_global_trigger_handler = CommandHandler('add_global_trigger', add_global_trigger, filters=(Filters.user(user_id = SUPER_ADMIN_ID) & Filters.chat(chat_id = SUPER_ADMIN_ID)))
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

g_info_handler = CommandHandler('g_info', g_info,filters=Filters.user(user_id = SUPER_ADMIN_ID))
g_all_attack_handler = CommandHandler('g_all_attack', g_all_attack,filters=Filters.user(user_id = SUPER_ADMIN_ID))
g_attack_handler = CommandHandler('g_attack', g_attack,filters=Filters.user(user_id = SUPER_ADMIN_ID))
g_help_handler = CommandHandler('g_help', g_help)


battle_history_handler = CommandHandler('battle_history', battle_history)

text_message_handler = MessageHandler(Filters.text | Filters.command, textMessage)
stats_send_handler = CommandHandler('stats_send', stats_send)

# Добавляем хендлеры в диспетчер
dispatcher.add_handler(start_command_handler)
try:
    dispatcher.add_handler(attack_command_handler)
except NameError:
    pass
dispatcher.add_handler(add_pin_command_handler)
dispatcher.add_handler(pin_setup_command_handler)
dispatcher.add_handler(pinset_command_handler)
dispatcher.add_handler(pinpin_command_handler)
dispatcher.add_handler(pinmute_command_handler)

dispatcher.add_handler(CommandHandler('mute', mute, pass_args=True))
dispatcher.add_handler(CommandHandler('mute_admin', mute_admin, pass_args=True))#, filters=filter_super_admin))
dispatcher.add_handler(CommandHandler('unmute_all_admins', unmute_all_admins))#, filters=filter_super_admin))
dispatcher.add_handler(MessageHandler(Filters.all & filter_delete_admin, delete_admin))

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

dispatcher.add_handler(MessageHandler(filter_set_class, set_class))
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
dispatcher.add_handler(CommandHandler("g_add_attack", g_add_attack, filters=(Filters.user(user_id=SUPER_ADMIN_ID) | Filters.user(user_id = JANE_ID))))
dispatcher.add_handler(CommandHandler("g_del_attack", g_del_attack, filters=(Filters.user(user_id=SUPER_ADMIN_ID) | Filters.user(user_id = JANE_ID))))
dispatcher.add_handler(CommandHandler("g_attacking_list", g_attacking_list, filters=(Filters.user(user_id=SUPER_ADMIN_ID) | Filters.user(user_id = JANE_ID))))
dispatcher.add_handler(CommandHandler("g_add_defense", g_add_defense, filters=(Filters.user(user_id=SUPER_ADMIN_ID) | Filters.user(user_id = JANE_ID))))
dispatcher.add_handler(CommandHandler("g_del_defense", g_del_defense, filters=(Filters.user(user_id=SUPER_ADMIN_ID) | Filters.user(user_id = JANE_ID))))
dispatcher.add_handler(CommandHandler("g_defending_list", g_defending_list, filters=(Filters.user(user_id=SUPER_ADMIN_ID) | Filters.user(user_id = JANE_ID))))

dispatcher.add_handler(MessageHandler(filter_guild_list, notify_guild_attack))
dispatcher.add_handler(CommandHandler('notify_guild_sleeping', notify_guild_to_battle))
dispatcher.add_handler(CommandHandler('notify_guild_not_ready', notify_guild_to_battle))

dispatcher.add_handler(CommandHandler('calculate_pogs', calculate_pogs, pass_args=True))
dispatcher.add_handler(CommandHandler('pogs', calculate_pogs, pass_args=True))

dispatcher.add_handler(battle_history_handler)

dispatcher.add_handler(CommandHandler("sql", sql, pass_user_data = True, filters=Filters.user(user_id=SUPER_ADMIN_ID)))


dispatcher.add_handler(CommandHandler("add_playlist", add_playlist, pass_args=True))
dispatcher.add_handler(CommandHandler("list_playlists", list_playlists))
dispatcher.add_handler(CommandHandler("add_to_playlist", add_to_playlist, pass_args=True))
dispatcher.add_handler(CommandHandler("play_random_from_playlist", play_random_from_playlist, pass_args=True))
dispatcher.add_handler(MessageHandler(Filters.command & filter_play_random_from_playlist, play_random_from_playlist))
dispatcher.add_handler(MessageHandler(Filters.command & filter_view_playlist, view_playlist))
dispatcher.add_handler(MessageHandler(Filters.command & filter_play_song, play_song))
dispatcher.add_handler(MessageHandler(Filters.command & filter_remove_song, remove_song))

dispatcher.add_handler(CommandHandler("stats", battle_stats_send, filters=Filters.user(user_id=SUPER_ADMIN_ID)))

dispatcher.add_handler(CommandHandler("todo", todo, filters=Filters.user(user_id=SUPER_ADMIN_ID)))
dispatcher.add_handler(CommandHandler("todo_list", todo_list, filters=Filters.user(user_id=SUPER_ADMIN_ID)))
dispatcher.add_handler(CommandHandler("todo_list_full", todo_list, filters=Filters.user(user_id=SUPER_ADMIN_ID)))
dispatcher.add_handler(MessageHandler(Filters.command & filter_complete_todo, complete_todo))


dispatcher.add_handler(CommandHandler('create_sticker_set', create_sticker_set, filters=filter_super_admin))
dispatcher.add_handler(CommandHandler('send_sticker_emoji', send_sticker_emoji))


dispatcher.add_handler(MessageHandler(filter_any_message, stats_count), group=1)
dispatcher.add_handler(CommandHandler("chat_stats", chat_stats_send, filters=Filters.user(user_id=SUPER_ADMIN_ID)))
dispatcher.add_handler(CommandHandler("current_chat_stats", current_chat_stats_send, filters=Filters.user(user_id=SUPER_ADMIN_ID)))


dispatcher.add_handler(CommandHandler('help', bot_help))
dispatcher.add_handler(CommandHandler('dspam_help', dspam_help))

dispatcher.add_handler(MessageHandler(Filters.text & filter_hero, add_hero))
dispatcher.add_handler(MessageHandler(Filters.text & filter_report, add_report))

dispatcher.add_handler(text_message_handler)

dispatcher.add_handler(stats_send_handler)


cache_full()
reports_sent_restore()

# Начинаем поиск обновлений
updater.start_polling(clean=False)
telethon_script = Process(target=script_work, args=())
telethon_script.start()
parse_stats = threading.Thread(target=parse_stats, args=())
parse_stats.start()
bot.send_message(chat_id = admin_ids[0], text = "Бот запущен.\nНе забудьте запустить тишину!: /silent_start")
job_silence = job.run_once(empty, 0)

# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
# Загружаем необновлённую статистику в базу данных
update_chat_stats()

castles_stats_queue.put(None)
# Разрываем подключение.
conn.close()
