from libs.guild import User
from work_materials.globals import conn

class Report:
    def __init__(self, report_id, castle, nickname, lvl, exp, gold, stock, attack, defense, date_sent):
        self.id = report_id
        self.castle = castle
        self.nickname = nickname
        self.lvl = int(lvl)
        self.exp = int(exp)
        self.gold = int(gold)
        self.stock = int(stock)
        self.attack = attack
        self.defense = defense
        self.date_sent = date_sent


class GuildReports:

    def __init__(self, guild_tag):
        self.guild_tag = guild_tag
        self.num_reports = 0
        self.gold = 0
        self.stock = 0
        self.attack = 0
        self.defense = 0
        self.reports = []
        request = "select telegram_id, telegram_username, user_attack, user_defense from users where guild = %s"
        cursor = conn.cursor()
        cursor.execute(request, (guild_tag,))
        row = cursor.fetchone()
        self.users = []
        self.num_players = 0
        while row:
            self.num_players += 1
            user = User(row[0], row[1], row[2], row[3])
            self.users.append(user)

            row = cursor.fetchone()
        cursor.close()


    def add_report(self, report):
        self.reports.append(report)
        self.num_reports += 1
        self.gold += report.gold
        self.stock += report.stock
        self.attack += report.attack
        self.defense += report.defense
        for user in self.users:
            if user.id == report.id:
                user.report_sent = True
                break
