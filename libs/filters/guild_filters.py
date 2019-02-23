from telegram.ext import BaseFilter
from work_materials.globals import cursor, castles, chat_wars_id
import datetime

class FilterGuildList(BaseFilter):
    def filter(self, message):
        try:
            first_line = message.text.splitlines()[1]
        except Exception:
            return False
        return message.text[0] in castles and message.forward_from and message.forward_from.id == chat_wars_id and \
            first_line.find("#1") == 0 and "[" in first_line

filter_guild_list = FilterGuildList()