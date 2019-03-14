from telegram.ext import BaseFilter
from work_materials.globals import *
import work_materials.globals as globals

class FilterDeleteAdmin(BaseFilter):
    def filter(self, message):
        user_ids = globals.mute_chats.get(message.chat_id)
        return user_ids is not None and message.from_user.id in user_ids

filter_delete_admin = FilterDeleteAdmin()
