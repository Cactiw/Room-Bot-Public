from work_materials.globals import castles as castles_const, build_menu
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def __build_pult(castles):
    __pult_buttons = [
        [
            InlineKeyboardButton(castles[0], callback_data="pc0"),
            InlineKeyboardButton(castles[1], callback_data="pc1"),
            InlineKeyboardButton(castles[2], callback_data="pc2"),
            InlineKeyboardButton(castles[3], callback_data="pc3"),
        ],
        [
            InlineKeyboardButton(castles[4], callback_data="pc4"),
            InlineKeyboardButton(castles[5], callback_data="pc5"),
            InlineKeyboardButton(castles[6], callback_data="pc6"),
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data="pupdate"),
        ],
    ]
    PultMarkup = InlineKeyboardMarkup(__pult_buttons)
    return PultMarkup


def rebuild_pult(action, context, user_data):
    if action == "default":
        castles = castles_const
        new_markup = __build_pult(castles)
        return new_markup
    if action == "change castle" or action == "update":
        new_response = "Распределение урона по замкам:\n"
        status = context
        status_list = sorted(list(status.items()), key=lambda players_list: len(players_list[1]), reverse=True)
        for castle, players_list in status_list:
            if not players_list:
                new_response += "{}: ----, ".format(castle)
            else:
                total_attack = 0
                total_defense = 0
                total_players = 0
                for player in players_list:
                    if player.castle == castle:
                        total_defense += player.defense
                    else:
                        total_attack += player.attack
                    total_players += 1
                new_response += "{}{}: {}{} 👥: <b>{}</b>\n".format(
                    "\n" if new_response != "" and new_response[-1] != '\n' else "",
                    castle, "⚔: <b>{}</b>".format(total_attack) if total_attack > 0 else "",
                    "🛡: <b>{}</b>".format(total_defense) if total_defense > 0 else "", total_players)
        new_markup = __build_pult(castles_const)
        return new_markup, new_response
