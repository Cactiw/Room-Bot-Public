from work_materials.globals import castles_stats_queue, SQUAD_GUILDS_TAGS, STATS_SEND_CHAT_ID, dispatcher, admin_ids
import re


def parse_stats():
    data = castles_stats_queue.get()
    while data:
        response = ""
        for castle_results_string in data.split("\n\n"):
            for tag in SQUAD_GUILDS_TAGS:
                if tag in castle_results_string:
                    try:
                        attacked_castle = re.search('[🍁☘🖤🐢🦇🌹🍆]', castle_results_string).group(0)
                    except TypeError:
                        attacked_castle = "???"
                    nicknames_list = re.findall(".\[{}[^🍁☘🖤🐢🦇🌹🍆]+".format(tag), castle_results_string)
                    print(nicknames_list)
                    for nickname in nicknames_list:
                        if response == "":
                            response = "Игроки, попавшие в топ:\n"
                        response += "{}{} <b>{}</b>\n".format("🛡️" if nickname[0] == attacked_castle else"⚔️",
                                                              attacked_castle, nickname[:-1])
        if response != "":
            dispatcher.bot.send_message(chat_id=STATS_SEND_CHAT_ID, text=response, parse_mode='HTML')
        data = castles_stats_queue.get()
