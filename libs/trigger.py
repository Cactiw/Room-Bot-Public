from work_materials.globals import *

class Trigger:
    def __init__(self, type, text):
        self.type = type
        self.text = text

        #Типы триггеров - 0 - текст, 1 - видео, 2 - аудио, 3 - фото, 4 - документ, 5 - стикер, 6 - войс


    def add_trigger(self, incoming, global_trigger):
        if incoming.reply_to_message.text:
            self.type = 0
            self.text = incoming.reply_to_message.text.translate({ord(c): None for c in {'\''}})#, '<', '>'}})
        elif incoming.reply_to_message.video:
            self.type = 1
            self.text = incoming.reply_to_message.video.file_id
        elif incoming.reply_to_message.audio:
            self.type = 2
            self.text = incoming.reply_to_message.audio.file_id
        elif incoming.reply_to_message.photo:
            self.type = 3
            self.text = incoming.reply_to_message.photo[-1].file_id
        elif incoming.reply_to_message.document:
            self.type = 4
            self.text = incoming.reply_to_message.document.file_id
        elif incoming.reply_to_message.sticker:
            self.type = 5
            self.text = incoming.reply_to_message.sticker.file_id
        elif incoming.reply_to_message.voice:
            self.type = 6
            self.text = incoming.reply_to_message.voice.file_id
        if global_trigger:
            request = "INSERT INTO triggers(trigger_in, trigger_out, type, chat_id, creator, date_created) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(incoming.text.lower()[20:], str(self.text), self.type, 0, incoming.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            request = "INSERT INTO triggers(trigger_in, trigger_out, type, chat_id, creator, date_created) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(incoming.text.lower()[13:], str(self.text), self.type, incoming.chat_id, incoming.from_user.username, time.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(request)
        conn.commit()
        cache_full()


    def send_trigger (self, type, trigger_out, bot, update):
        current = Trigger(type, trigger_out)
        #current.process(response)
        if current.type == 0:
            bot.send_message(chat_id=update.message.chat_id, text=trigger_out, parse_mode = 'HTML')
        elif current.type == 1:
            bot.send_video(chat_id=update.message.chat_id, video=current.text)
        elif current.type == 2:
            bot.send_audio(chat_id=update.message.chat_id, audio=current.text)
        elif current.type == 3:
            bot.send_photo(chat_id=update.message.chat_id, photo=current.text)
        elif current.type == 4:
            bot.send_document(chat_id=update.message.chat_id, document=current.text)
        elif current.type == 5:
            bot.send_sticker(chat_id=update.message.chat_id, sticker=current.text)
        elif current.type == 6:
            bot.send_voice(chat_id=update.message.chat_id, voice=current.text)