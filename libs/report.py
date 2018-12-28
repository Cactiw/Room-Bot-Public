

class Report:
    def __init__(self, castle, nickname, exp, gold, stock):
        self.castle = castle
        self.nickname = nickname
        self.exp = int(exp)
        self.gold = int(gold)
        self.stock = int(stock)