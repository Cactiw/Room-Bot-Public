from work_materials.globals import cursor


class Player:
    def __init__(self, telegram_id):
        self.telegram_id = telegram_id
        self.user_id, self.castle, self.telegram_username, self.username, self.guild, self.lvl, self.attack, \
            self.defense, self.game_class, self.last_update, self.birthday, self.dspam_user, \
            self.class_skill_lvl = None, None, None, None, None, None, None, None, None, None, None, None, None

    def update_from_database(self):
        request = "select user_id, user_castle, telegram_username, username, guild, user_lvl, user_attack, " \
                  "user_defense, user_class, last_update, birthday, dspam_user, class_skill_lvl from users " \
                  "where telegram_id = %s"
        cursor.execute(request, (self.telegram_id,))
        row = cursor.fetchone()
        if row is None:
            return 1
        self.user_id, self.castle, self.telegram_username, self.username, self.guild, self.lvl, self.attack, \
            self.defense, self.game_class, self.last_update, self.birthday, self.dspam_user, self.class_skill_lvl = row
        return 0

    def __eq__(self, other):
        return self.telegram_id == other.telegram_id
