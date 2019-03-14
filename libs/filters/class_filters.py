from telegram.ext import BaseFilter
from work_materials.globals import *

class FilterSetClass(BaseFilter):
    def filter(self, message):
        if message.text:
            if message.forward_from is None:
                return False
            return 'skills levels' in message.text and message.forward_from.id == chat_wars_id and message.chat_id == message.from_user.id
        return False

filter_set_class = FilterSetClass()
