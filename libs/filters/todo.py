from telegram.ext import BaseFilter
from work_materials.globals import *

class FilterCompleteTODO(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/complete_todo' in message.text and message.from_user.id in admin_ids
        return 0


filter_complete_todo = FilterCompleteTODO()