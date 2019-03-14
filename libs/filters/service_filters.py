from telegram.ext import BaseFilter
from work_materials.globals import *

class FilterSuperAdmin(BaseFilter):
    def filter(self, message):
        return message.from_user.id in admin_ids

filter_super_admin = FilterSuperAdmin()
