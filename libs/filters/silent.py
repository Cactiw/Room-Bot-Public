from telegram.ext import BaseFilter
from work_materials.globals import *
import work_materials.globals as globals

class Filter_silentdelete(BaseFilter):
    def filter(self, message):
        return globals.silent_delete and message.chat_id in globals.silent_chats

filter_silentdelete = Filter_silentdelete()


class Filter_sil_run(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'sil_run' in message.text
        return 0

filter_sil_run = Filter_sil_run()