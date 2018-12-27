from telegram.ext import BaseFilter
from work_materials.globals import *


class Filter_View_Playlist(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'view_playlist_' in message.text
        return 0


filter_view_playlist = Filter_View_Playlist()

class Filter_Play_Song(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'play_song' in message.text
        return 0


filter_play_song = Filter_Play_Song()

class Filter_Remove_Song(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'remove_song' in message.text
        return 0


filter_remove_song = Filter_Remove_Song()

class Filter_Play_Random_From_Playlist(BaseFilter):
    def filter(self, message):
        if message.text:
            return 'play_random_from_playlist' in message.text
        return 0


filter_play_random_from_playlist = Filter_Play_Random_From_Playlist()