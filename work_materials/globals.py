from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter


from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
import psycopg2
import pytz
import tzlocal


from mwt import MWT     # Для кэширования
from config import psql_creditals, Production_token, DEV_token
from libs.bot_async_messaging import AsyncBot
from libs.updater_async import AsyncUpdater

try:
    from config import request_kwargs
except ImportError:
    request_kwargs = None

admin_ids = [231900398]
chat_wars_id = 265204902

classes_list = ['Alchemist', 'Blacksmith', 'Collector', 'Ranger', 'Knight', 'Sentinel']
ranger_aiming_minutes = [0, 180, 165, 150, 135, 120, 105, 95, 85, 75, 65, 60, 55, 50, 45, 40, 35]

castles = ['🍁', '☘', '🖤', '🐢', '🦇', '🌹', '🍆']
ranks_specials = ['','🎗','🎖']

moscow_tz = pytz.timezone('Europe/Moscow')
try:
    local_tz = tzlocal.get_localzone()
except pytz.UnknownTimeZoneError:
    local_tz = pytz.timezone('Europe/Andorra')

bot = AsyncBot(token=Production_token, workers=8, request_kwargs=request_kwargs)
updater = AsyncUpdater(bot = bot)

dispatcher = updater.dispatcher
job = updater.job_queue


#Подключаем базу данных, выставляем кодировку
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'], psql_creditals['pass']))
conn.set_session(autocommit = True)
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
silent_running = False
silent_delete = False
silent_chats = []

mute_chats = {}


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
