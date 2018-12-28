from telegram.ext import BaseFilter
from work_materials.globals import *

class Filter_pr(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'pr_' in message.text
        return 0

filter_pr = Filter_pr()

class Filter_rank(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/rank_' in message.text
        return 0

filter_rank = Filter_rank()

class Filter_edit_rank(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/edit_rank_' in message.text
        return 0

filter_edit_rank = Filter_edit_rank()

class Filter_r_set_name(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/r_set_name' in message.text
        return 0

filter_r_set_name = Filter_r_set_name()

class Filter_r_set_description(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/r_set_description' in message.text
        return 0

filter_r_set_description = Filter_r_set_description()

class Filter_r_set_unique(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/r_set_unique' in message.text
        return 0

filter_r_set_unique = Filter_r_set_unique()


class Filter_del_rank(BaseFilter):
    def filter(self, message):
        if message.text:
            return '/del_rank_' in message.text
        return 0

filter_del_rank = Filter_del_rank()


class Filter_confirm(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'confirm' in message.text
        return 0

filter_confirm = Filter_confirm()


class Filter_reject(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'reject' in message.text
        return 0


filter_reject = Filter_reject()