"""
Файл содержит фильтры для функций в bin/chat_wars.py
"""

from telegram.ext import BaseFilter
from work_materials.globals import chat_wars_id


# Сообщение - репорт и форвард из чв3
class FilterReport(BaseFilter):
    def filter(self, message):
        return message.forward_from and message.forward_from.id == chat_wars_id and \
               'Твои результаты в бою:' in message.text


filter_report = FilterReport()


# Сообщение - хиро и форвард из чв3
class FilterHero(BaseFilter):
    def filter(self, message):
        return message.forward_from and message.forward_from.id == chat_wars_id and\
               'Уровень:' in message.text and 'Класс: /class' in message.text


filter_hero = FilterHero()


# Сообщение - форвард /g_stock_rec из чв3 и в личке
class FilterGuildStockRecipes(BaseFilter):
    def filter(self, message):
        return message.forward_from and message.forward_from.id == chat_wars_id and\
               message.chat_id == message.from_user.id and\
               message.text.find("Guild Warehouse:") == 0 and "recipe" in message.text


filter_guild_stock_recipes = FilterGuildStockRecipes()


# Сообщение - форвард /g_stock_parts из чв3 и в личке
class FilterGuildStockParts(BaseFilter):
    def filter(self, message):
        return message.forward_from and message.forward_from.id == chat_wars_id and \
               message.chat_id == message.from_user.id and \
               message.text.find("Guild Warehouse:") == 0 and "part" in message.text


filter_guild_stock_parts = FilterGuildStockParts()
