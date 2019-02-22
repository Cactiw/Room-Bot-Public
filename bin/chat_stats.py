import logging
from work_materials.globals import *

def chat_stats_send(bot, update):
    response = "Топ-10 чатов по сообщениям:\n"
    update_chat_stats()

    request = "SELECT chat_name, message_count, text_messages_count, stickers_messages_count, " \
                  "audio_messages_count, photo_messages_count, video_messages_count, document_messages_count, " \
                  "voice__messages_count from stats order by message_count desc limit 11"
    cursor.execute(request)
    all_chats_row = cursor.fetchone()
    row = cursor.fetchone()
    while row is not None:
        response_new = "<b>{0}</b> -- Всего сообщений: <b>{1}</b>\n Текстовых: {2}\n Стикеров: {3}\n Аудио: {4}\n Фото: {5}\n" \
                    " Видео: {6}\n Войсов: {7}\n Документов: {8}\n\n".format(row[0], row[1], row[2], row[3], row[4], row[5],
                                                                         row[6], row[7], row[8])

        if len(response + response_new) >= 4096:  # Превышение лимита длины сообщения
            bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
            response = ""
        response += response_new
        row = cursor.fetchone()
    response_new = "Итого сообщений: <b>{0}</b>\n Текстовых: {1}\n Стикеров: {2}\n Аудио: {3}\n Фото: {4}\n " \
                "Видео: {5}\n Войсов: {6}\n Документов: {7}\n\n".format(all_chats_row[1], all_chats_row[2],
                                                                        all_chats_row[3], all_chats_row[4],
                                                                        all_chats_row[5], all_chats_row[6],
                                                                        all_chats_row[7], all_chats_row[8])
    if len(response + response_new) >= 4096:  # Превышение лимита длины сообщения
        bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')
        response = ""
    response += response_new
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def current_chat_stats_send(bot, update):
    update_chat_stats()

    request = "SELECT chat_name, message_count, text_messages_count, stickers_messages_count, " \
              "audio_messages_count, photo_messages_count, video_messages_count, document_messages_count, " \
              "voice__messages_count from stats where chat_id = %s"
    cursor.execute(request, (update.message.chat_id,))
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text="Ошибка", parse_mode='HTML')
        return
    response = "<b>{0}</b> -- Всего сообщений: <b>{1}</b>\n Текстовых: {2}\n Стикеров: {3}\n Аудио: {4}\n Фото: {5}\n" \
                   " Видео: {6}\n Войсов: {7}\n Документов: {8}\n\n".format(row[0], row[1], row[2], row[3], row[4],
                                                                            row[5], row[6], row[7], row[8])
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')



def update_chat_stats():
    logging.info("updating chat stats...")
    for chat_stats in stats.values():
        chat_stats.update_to_database()
    logging.info("finished")