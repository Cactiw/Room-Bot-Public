from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter


from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
import MySQLdb
import psycopg2



from config import psql_creditals, Production_token, DEV_token


admin_ids = [231900398]



updater = Updater(token=Production_token) # Токен API к Telegram        # Сам бот
#updater = Updater(token=DEV_token) # Токен API к Telegram         # DEV - версия

dispatcher = updater.dispatcher

#Подключаем базу данных, выставляем кодировку
#conn = MySQLdb.connect(MYSQL_creditals['host'], MYSQL_creditals['user'], MYSQL_creditals['pass'], MYSQL_creditals['db'])
conn = psycopg2.connect("dbname={0} user={1} password={2}".format(psql_creditals['dbname'], psql_creditals['user'], psql_creditals['pass']))
cursor = conn.cursor()
"""conn.set_character_set('utf8mb4')
cursor.execute('SET NAMES utf8mb4;')
cursor.execute('SET CHARACTER SET utf8mb4;')
cursor.execute('SET character_set_connection=utf8mb4;')

cursor_2 = conn.cursor()
cursor_2.execute('SET NAMES utf8mb4;')
cursor_2.execute('SET CHARACTER SET utf8mb4;')
cursor_2.execute('SET character_set_connection=utf8mb4;')
"""
cursor_2 = conn.cursor()

stats = {}