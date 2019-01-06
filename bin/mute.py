from telegram import TelegramError
import time, datetime
import logging

from work_materials.globals import *

def mute_admin(bot, update, args):
    mes = update.message
    if mes.from_user.id not in admin_ids:
        bot.send_message(chat_id = mes.chat_id, text = "Ага, щаз!")
        return
    if mes.reply_to_message is None:
        return
    if mes.reply_to_message.from_user.id == 231900398:
        bot.send_message(chat_id=update.message.chat_id, text='Банить своего создателя я не буду!')
        return
    if not args:
        return
    mute_for = datetime.timedelta(minutes = float(args[0]))
    context = [mes.chat_id, mes.reply_to_message.from_user.id]
    user_ids = mute_chats.get(mes.chat_id)
    if user_ids is None:
        user_ids = []
    user_ids.append(mes.reply_to_message.from_user.id)
    mute_chats.update({mes.chat_id : user_ids})
    job.run_once(end_mute, mute_for, context=context)
    bot.send_message(chat_id = mes.chat_id, text = "Выполнено!\nПриятного дня!")

def end_mute(bot, job):
    context = job.context
    user_ids = mute_chats.get(context[0])
    if user_ids is None:
        logging.warning("Can not end mute")
        return
    user_ids.remove(context[1])
    return

def unmute_all_admins(bot, update):
    mes = update.message
    if mes.from_user.id not in admin_ids:
        bot.send_message(chat_id = mes.chat_id, text = "Кыш отсюда")
        return
    mute_chats.clear()
    bot.send_message(chat_id = mes.chat_id, text = "Выполнено!\nПриятного дня!")



def delete_admin(bot, update):
    mes = update.message
    try:
        bot.deleteMessage(chat_id = mes.chat_id, message_id = mes.message_id)
    except TelegramError:
        pass