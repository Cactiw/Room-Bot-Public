from work_materials.globals import *
import time


def add_playlist(bot, update, args):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        return
    if not args:
        bot.send_message(chat_id=update.message.chat_id, text='Неверный синтаксис')
        return
    request = "SELECT * FROM playlists WHERE playlist_name = %s and chat_id = %s"
    cursor.execute(request, (mes.text.partition(' ')[2], mes.chat_id))
    row = cursor.fetchone()
    if row is not None:
        bot.send_message(chat_id=update.message.chat_id, text= 'Данный плейлист уже существует!')
        return
    request = "INSERT INTO playlists(playlist_name, chat_id, created_by, date_created) VALUES (%s, %s, %s, %s)"
    cursor.execute(request, (mes.text.partition(' ')[2].upper(), mes.chat_id, mes.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Плейлист успешно добавлен!')


def list_playlists(bot, update):
    mes = update.message
    if (mes.from_user.id != 231900398) and (mes.from_user.id not in get_admin_ids(bot, chat_id=mes.chat_id)):
        bot.send_message(chat_id=update.message.chat_id, text= 'Только админы. Хватит засорять чаты')
        return
    response = "Список плейлистов:\n"
    request = "SELECT * from playlists WHERE chat_id = %s"
    cursor.execute(request, (mes.chat_id,))
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
    request = "SELECT song_id, title, performer, duration FROM songs WHERE playlist_id = %s"
    cursor.execute(request, (mes.text.partition('@')[0].partition('_')[2].partition('_')[2],))
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
    request = "SELECT * FROM songs WHERE file_id = %s AND playlist_id = %s"
    cursor.execute(request, (mes.reply_to_message.audio.file_id, mes.text.partition(' ')[2],))
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
    request = "INSERT INTO songs(file_id, playlist_id, performer, title, duration) VALUES (%s, %s, %s, %s, %s)"
    ###trigger_mes = mes.text.translate({ord(c): None for c in '\''})
    try:
        cursor.execute(request, (mes.reply_to_message.audio.file_id, mes.text.partition(' ')[2],
                                      performer,
                                      title,
                                      mes.reply_to_message.audio.duration))
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
        request = "SELECT file_id FROM songs WHERE playlist_id = %s ORDER BY RANDOM() LIMIT 1"
        cursor.execute(request, (arg,))
        row = cursor.fetchone()
        if row is None:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Песня не найдена. Проверьте корректность ввода id плейлиста. Возможно, что он пуст.')
            return
        bot.send_audio(chat_id=mes.chat_id, audio=row[0])
        return
    request = "SELECT file_id FROM songs WHERE playlist_id = %s ORDER BY RANDOM() LIMIT 1"
    cursor.execute(request, (args[0],))
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
    request = "SELECT file_id FROM songs WHERE song_id = %s"
    cursor.execute(request, (mes.text.partition('@')[0].partition('_')[2].partition('_')[2]))
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
    request = "SELECT file_id FROM songs WHERE song_id = %s"
    cursor.execute(request, (mes.text.partition('@')[0].partition('_')[2].partition('_')[2],))
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text='Песня не найдена. Проверьте корректность ввода id песни.')
        return
    request = "DELETE FROM songs WHERE song_id = %s"
    try:
        cursor.execute(request, (mes.text.partition('@')[0].partition('_')[2].partition('_')[2],))
    except:
        bot.send_message(chat_id=update.message.chat_id, text='Ошибка', parse_mode='HTML')
        return
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено', parse_mode='HTML')
