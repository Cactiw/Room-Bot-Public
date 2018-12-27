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


bot = AsyncBot(token=Production_token)
updater = AsyncUpdater(bot = bot)

dispatcher = updater.dispatcher

#Подключаем базу данных, выставляем кодировку
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'], psql_creditals['pass']))
cursor = conn.cursor()

cursor_2 = conn.cursor()

stats = {}


@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]