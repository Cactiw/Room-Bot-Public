from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter


from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
import MySQLdb
import psycopg2


from mwt import MWT     # Для кэширования
from config import psql_creditals, Production_token, DEV_token
from libs.bot_async_messaging import AsyncBot
from libs.updater_async import AsyncUpdater


admin_ids = [231900398]

castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']
ranks_specials = ['','🎗','🎖']


bot = AsyncBot(token=Production_token)
updater = AsyncUpdater(bot = bot)

dispatcher = updater.dispatcher
job = updater.job_queue


#Подключаем базу данных, выставляем кодировку
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'], psql_creditals['pass']))
cursor = conn.cursor()

cursor_2 = conn.cursor()

stats = {}
triggers_in = []

g_added_attack = 0
g_added_defense = 0
g_attacking_users = []
g_defending_users = []
reports_count = {}

guilds_chat_ids = { "KYS" : -1001377426029, "СКИ" : -1001315600160}

status = 0
globalstatus = 0
silent_running = 0
silent_delete = 0
silent_chats = [int] * 100


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


@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


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
