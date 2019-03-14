from telegram.ext import BaseFilter
from work_materials.globals import chat_wars_id


class FilterReport(BaseFilter):
    def filter(self, message):
        return message.forward_from and message.forward_from.id == chat_wars_id and \
               'Твои результаты в бою:' in message.text


filter_report = FilterReport()


class FilterHero(BaseFilter):
    def filter(self, message):
        return message.forward_from and message.forward_from.id == chat_wars_id and\
               'Уровень:' in message.text and 'Класс: /class' in message.text


filter_hero = FilterHero()
