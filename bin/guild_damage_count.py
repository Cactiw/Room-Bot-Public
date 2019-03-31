from telegram.error import BadRequest, TelegramError
import logging
import traceback

from work_materials.globals import dispatcher, guilds_chat_ids, SQUAD_GUILDS_TAGS, admin_ids
from libs.damage_count_pult import rebuild_pult
from libs.player import Player

pults_statuses = {}

def damage_count_send():
    response = "Распределение урона по замкам:\n"
    reply_markup = rebuild_pult("default", None, None)
    for tag in SQUAD_GUILDS_TAGS:
        chat_id = guilds_chat_ids.get(tag)
        if chat_id is None:
            continue
        message = dispatcher.bot.sync_send_message(chat_id=chat_id, text=response, reply_markup=reply_markup,
                                                   parse_mode='HTML')
        try:
            dispatcher.bot.pin_chat_message(chat_id=message.chat_id, message_id=message.message_id,
                                            disable_notification=True)
        except TelegramError:
            pass


def pult_callback(bot, update, user_data):
    data = update.callback_query.data
    if data.find('pc') == 0:
        pult_castles_callback(bot, update, user_data)
    if data == 'pupdate':
        pult_update(bot, update, user_data)


def pult_castles_callback(bot, update, user_data):
    data = update.callback_query.data
    chat_id = update.callback_query.message.chat_id
    status = pults_statuses.get(guilds_chat_ids.get(chat_id))
    telegram_id = update.callback_query.from_user.id
    if status is None:
        status = {'🍁': [], '☘': [], '🖤': [], '🐢': [], '🦇': [], '🌹': [], '🍆': []}
        pults_statuses.update({update.callback_query.message.chat_id: status})
    player = Player(telegram_id)
    if player.update_from_database() == 1:
        bot.answerCallbackQuery(callback_query_id=update.callback_query.id, text="Ваш профиль не найден в базе данных",
                                show_alert=True)
        return
    tag = None
    for guild_tag, guild_chat_id in list(guilds_chat_ids.items()):
        if guild_chat_id == chat_id:
            tag = guild_tag
            break
    if tag is None:
        logging.warning("Guild tag for damage pult is None")
    else:
        if player.guild != tag:
            bot.answerCallbackQuery(callback_query_id=update.callback_query.id,
                                    text="Вы не в этой гильдии!",
                                    show_alert=True)
            return
    for players_list in list(status.values()):
        if Player in players_list:
            players_list.remove(Player)
    players_list =list(status.values())[int(data[2])]
    players_list.append(player)
    reply_markup, response = rebuild_pult("change castle", context=status, user_data=user_data)
    edit_pult_message(bot, chat_id=chat_id, message_id=update.callback_query.message.message_id,
                      text=response, reply_markup=reply_markup, callback_query_id=update.callback_query.id)


def pult_update(bot, update, user_data):
    data = update.callback_query.data
    chat_id = update.callback_query.message.chat_id
    status = pults_statuses.get(guilds_chat_ids.get(chat_id))
    if status is None:
        status = {'🍁': [], '☘': [], '🖤': [], '🐢': [], '🦇': [], '🌹': [], '🍆': []}
        pults_statuses.update({update.callback_query.message.chat_id: status})

    reply_markup, response = rebuild_pult("update", context=status, user_data=user_data)
    edit_pult_message(bot, chat_id=chat_id, message_id=update.callback_query.message.message_id,
                      text=response, reply_markup=reply_markup, callback_query_id=update.callback_query.id)


def edit_pult_message(bot, chat_id, message_id, text, reply_markup, callback_query_id):
    try:
        bot.editMessageText(chat_id=chat_id, message_id=message_id, text=text, parse_mode='HTML')
        bot.editMessageReplyMarkup(chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    except BadRequest:
        pass
    except TelegramError:
        logging.error(traceback.format_exc())
    finally:
        bot.answerCallbackQuery(callback_query_id=callback_query_id)
