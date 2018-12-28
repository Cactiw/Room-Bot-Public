class Report:
    def __init__(self, castle, nickname, lvl, exp, gold, stock, attack, defense):
        self.castle = castle
        self.nickname = nickname
        self.lvl = int(lvl)
        self.exp = int(exp)
        self.gold = int(gold)
        self.stock = int(stock)
        self.attack = attack
        self.defense = defense


class GuildReports:

    def __init__(self, guild_tag, num_players):
        self.guild_tag = guild_tag
        self.num_players = num_players
        self.num_reports = 0
        self.gold = 0
        self.stock = 0
        self.attack = 0
        self.defense = 0
        self.reports = []

    def add_report(self, report):
        self.reports.append(report)
        self.num_reports += 1
        self.gold += report.gold
        self.stock += report.stock
        self.attack += report.attack
        self.defense += report.defense
