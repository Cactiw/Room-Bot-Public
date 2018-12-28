

class User_for_attack:
    attack = 0
    username = ""
    g_attacking = -1
    def __init__(self, username, attack, g_attacking):
        self.username = username
        self.attack = attack
        self.g_attacking = g_attacking


class User:
    def __init__(self, id, username, attack, defense):
        self.id = id
        self.username = username
        self.attack = attack
        self.defense = defense