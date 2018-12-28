from work_materials.globals import *
import time


def attackCommand(bot, update):
    response = update.message.text[1:len(update.message.text)]
    stats = "Рассылка пинов началась в {0}\n\n".format(time.ctime())

    request = "SELECT chat_id, enabled, pin, disable_notification FROM pins"
    cursor.execute(request)
    row = cursor.fetchone()
    chats_count = 0
    while row:
        if row[1]:
            mes_current = bot.sync_send_message(chat_id = row[0], text = response)#Отправка в текущий чат
            chats_count += 1
            if row[2]:
                bot.pinChatMessage(chat_id = row[0], message_id = mes_current.message_id, disable_notification = row[3])
        row = cursor.fetchone()
    stats += "Выполнено в {0}, отправлено в {1} чатов".format(time.ctime(), chats_count)
    bot.send_message(chat_id=update.message.chat_id, text=stats)


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
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')


def pinpin(bot, update):
    mes = update.message
    mes1 = mes.text.split("_")
    #print(mes1[0], mes1[1], mes1[2])
    request = "UPDATE pins SET pin = '{0}' WHERE pin_id = '{1}'".format(mes1[2], mes1[1])
    cursor.execute(request)
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')

def pinmute(bot, update):
    mes = update.message
    mes1 = mes.text.split("_")
    request = "UPDATE pins SET disable_notification = '{0}' WHERE pin_id = '{1}'".format(mes1[2], mes1[1])
    cursor.execute(request)
    conn.commit()
    bot.send_message(chat_id=update.message.chat_id, text='Выполнено')