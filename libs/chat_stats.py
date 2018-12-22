from work_materials.globals import cursor, conn
from telegram.ext import BaseFilter

CREATE_ROW_RETURN_CODE = 10


class ChatStats:

    def __init__(self, chat_id, chat_name, message_count, text_messages_count, stickers_messages_count, document_messages_count,
                 audio_messages_count, voice_messages_count, photo_messages_count, video_messages_count):
        self.chat_id = int(chat_id)
        self.chat_name = chat_name
        self.message_count = int(message_count)
        self.text_messages_count = int(text_messages_count)
        self.stickers_messages_count = int(stickers_messages_count)
        self.document_messages_count = int(document_messages_count)
        self.voice_messages_count = int(voice_messages_count)
        self.audio_messages_count = int(audio_messages_count)
        self.photo_messages_count = int(photo_messages_count)
        self.video_messages_count = int(video_messages_count)
        self.messages_without_update = 0

    def process_message(self, message):
        self.message_count += 1
        if message.text:
            self.text_messages_count += 1
        elif message.video:
            self.video_messages_count += 1
        elif message.audio:
            self.audio_messages_count += 1
        elif message.photo:
            self.photo_messages_count += 1
        elif message.document:
            self.document_messages_count += 1
        elif message.sticker:
            self.stickers_messages_count += 1
        elif message.voice:
            self.voice_messages_count += 1

        self.messages_without_update += 1
        if self.messages_without_update >= 20:
            self.update_to_database()

    def update_from_database(self):

        request = "select chat_name, message_count, text_messages_count, stickers_messages_count, " \
                  "audio_messages_count, photo_messages_count, video_messages_count, document_messages_count, " \
                  "voice__messages_count from stats where chat_id = '{0}'".format(self.chat_id)
        cursor.execute(request)
        row = cursor.fetchone()
        if row is None:
            request = "insert into stats(chat_id, chat_name, message_count, text_messages_count, stickers_messages_count, " \
                  "audio_messages_count, photo_messages_count, video_messages_count, document_messages_count, " \
                  "voice__messages_count) values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', " \
                      "'{9}')".format(self.chat_id, self.chat_name, self.message_count, self.text_messages_count,
                                      self.stickers_messages_count, self.audio_messages_count, self.photo_messages_count,
                                      self.video_messages_count, self.document_messages_count, self.voice_messages_count)
            cursor.execute(request)
            conn.commit()
            return CREATE_ROW_RETURN_CODE

        self.chat_name = row[0]
        self.message_count = row[1]
        self.text_messages_count = row[2]
        self.stickers_messages_count = row[3]
        self.audio_messages_count = row[4]
        self.photo_messages_count = row[5]
        self.video_messages_count = row[6]
        self.document_messages_count = row[7]
        self.voice_messages_count = row[8]
        return
    def update_to_database(self):
        request = "update stats set message_count = '{0}', text_messages_count = '{1}', stickers_messages_count = '{2}', " \
                  "audio_messages_count = '{3}', photo_messages_count = '{4}'," \
                  "video_messages_count = '{5}', document_messages_count = '{7}', voice__messages_count = '{8}'" \
                  "  where chat_id = '{6}'".format(self.message_count, self.text_messages_count,
                                                   self.stickers_messages_count, self.audio_messages_count,
                                                   self.photo_messages_count, self.video_messages_count, self.chat_id,
                                                   self.document_messages_count, self.voice_messages_count)
        cursor.execute(request)
        conn.commit()

class FilterAnyMessage(BaseFilter):
    def filter(self, message):
        return True


filter_any_message = FilterAnyMessage()