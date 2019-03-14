

class User_for_attack:

    def __init__(self, username, attack, g_attacking):
        self.username = username
        self.attack = attack
        self.g_attacking = g_attacking
        self.attack = 0
        self.username = ""
        self.g_attacking = -1


class User:
    def __init__(self, guild_id, username, attack, defense):
        self.id = guild_id
        self.username = username
        self.attack = attack
        self.defense = defense
        self.report_sent = False

    def __eq__(self, other):
        return self.id == other.id
