

def bot_help(bot, update):
    response = "Доступные команды помощи:\n"
    response += "Список команд для триггеров: /triggers_help\n"
    response += "Список команд для управления гильдией(только админы бота): /g_help\n"
    response += "Список команд для управления ДСПАМ: /dspam_help\n"
    response += "Список команд для плейлистов: /playlists_help\n"
    bot.send_message(chat_id = update.message.chat_id, text = response)


def dspam_help(bot, update):
    bot.send_message(chat_id = update.message.chat_id, text = 'https://telegra.ph/DSPAM-Bot-Help-10-05')
