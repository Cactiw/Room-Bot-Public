from work_materials.globals import cursor, moscow_tz, local_tz, guilds_chat_ids, reports_count, admin_ids
from bin.class_func import knight_critical, sentinel_critical
from libs.guild_reports_stats import GuildReports, Report

from telegram.error import TelegramError
import time, datetime, logging, traceback



def add_hero(bot, update):
    mes = update.message
    request = "SELECT * FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row != None:
        print(row)
    if row is None:  # Добавляем нового игрока
        guild = None
        if mes.text[1] == '[':
            guild = mes.text[1:].split(']')[0][1:]
        username = mes.text[1:].split('\n')[0]
        lvl = int(mes.text[mes.text.find('🏅Уровень:'):].split()[1])
        attack = int(mes.text[mes.text.find('⚔Атака:'):].split()[1])
        defense = int(mes.text[mes.text.find('⚔Атака:'):].split()[3])
        request = "INSERT INTO users(telegram_id, telegram_username, user_castle, username, guild, user_lvl, " \
                  "user_attack, user_defense, last_update) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(request, (mes.from_user.id, mes.from_user.username, mes.text[0], username, guild, lvl, attack,
                                  defense, time.strftime('%Y-%m-%d %H:%M:%S')))
        bot.send_message(chat_id=update.message.chat_id, text='Профиль успешно добавлен')
    else:
        username = mes.text[1:].split('\n')[0]
        lvl = int(mes.text[mes.text.find('🏅Уровень:'):].split()[1])
        guild = None
        if mes.text[1] == '[':
            guild = mes.text[1:].split(']')[0][1:]
        attack = int(mes.text[mes.text.find('⚔Атака:'):].split()[1])
        defense = int(mes.text[mes.text.find('⚔Атака:'):].split()[3])
        request = "UPDATE users SET telegram_id = %s, telegram_username = %s,user_castle = %s, username = %s, " \
                  "guild = %s, user_lvl = %s, user_attack = %s, user_defense = %s, last_update = %s WHERE telegram_id = %s"
        cursor.execute(request, (mes.from_user.id, mes.from_user.username, mes.text[0], username, guild, lvl, attack,
                                 defense, time.strftime('%Y-%m-%d %H:%M:%S'), mes.from_user.id))

        bot.send_message(chat_id=-1001197381190,
                         text='Профиль успешно обновлён для пользователя @' + mes.from_user.username)
        try:
            bot.send_message(chat_id=update.message.from_user.id, text='Профиль успешно обновлён')
        except TelegramError:
            return


def add_report(bot, update):
    mes = update.message
    request = "SELECT * FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        try:
            bot.send_message(chat_id=update.message.from_user.id,
                             text='Профиль не найден в базе данных. Пожалуйста, обновите /hero')
        except TelegramError:
            return
    else:
        d = datetime.datetime(2018, 5, 27, 9, 0, 0, 0)
        c = datetime.timedelta(hours=8)
        try:
            forward_message_date = local_tz.localize(update.message.forward_date).astimezone(
                tz=moscow_tz).replace(tzinfo=None)
        except ValueError:
            print("value error")
            try:
                forward_message_date = update.message.forward_date.astimezone(
                    tz=moscow_tz).replace(
                    tzinfo=None)
            except ValueError:
                forward_message_date = update.message.forward_date
        a = forward_message_date - d
        battle_id = 0
        while a > c:
            a = a - c
            battle_id = battle_id + 1
        if mes.text[1:mes.text.find('⚔') - 1] != row[4]:
            try:
                bot.send_message(chat_id=update.message.from_user.id,
                                 text='Это не ваш репорт. В случае возникновения ошибок обновите профиль')
            except TelegramError:
                return
            return
        attack = int(mes.text[mes.text.find('⚔') + 2:].split()[0].split('(')[0])
        defense = int(mes.text[mes.text.find('🛡') + 2:].split()[0].split('(')[0])
        lvl = int(mes.text[mes.text.find("Lvl") + 4:].split()[0])
        if mes.text.find("🔥Exp:") == -1:
            exp = 0
        else:
            exp = int(mes.text[mes.text.find("🔥Exp:"):].split()[1])
        if mes.text.find("💰Gold") == -1:
            gold = 0
        else:
            gold = int(mes.text[mes.text.find("💰Gold"):].split()[1])
        if mes.text.find("📦Stock") == -1:
            stock = 0
        else:
            stock = int(mes.text[mes.text.find("📦Stock"):].split()[1])
        critical = 0
        guardian = 0
        request = "SELECT * FROM reports WHERE user_id = %s AND battle_id = %s"
        cursor.execute(request, (row[0], battle_id))
        response = cursor.fetchone()
        if response != None:
            bot.send_message(chat_id=update.message.chat_id, text='Репорт за эту битву уже учтён!')
            return
        additional_attack = 0
        additional_defense = 0
        guild_tag = str(mes.text[2:mes.text.find(']')].upper())
        if mes.text.find('⚡Critical strike') != -1:
            critical = 1
            if guild_tag in list(guilds_chat_ids):
                knight_critical(bot, update)
            text = mes.text.partition('🛡')[0]
            try:
                additional_attack = int(text[text.find('+') + 1:text.find(')')])
            except ValueError:
                try:
                    additional_attack = int(text[text.find('-'): text.find(')')])
                except ValueError:
                    logging.error(traceback.format_exc())
                    additional_attack = 0
        elif mes.text.find('⚡Lucky Defender!') != -1:
            critical = 1
            if guild_tag in list(guilds_chat_ids):
                sentinel_critical(bot, update)
            text = mes.text.partition('🛡')[2]
            try:
                additional_defense = int(text[text('+') + 1:text.find(')')])
            except ValueError:
                try:
                    additional_defense = int(text[text.find('-'): text.find(')')])
                except ValueError:
                    logging.error(traceback.format_exc())
                    additional_defense = 0
        elif mes.text.find('🔱Guardian angel') != -1:
            guardian = 1
            if guild_tag in list(guilds_chat_ids):
                sentinel_critical(bot, update)
            text = mes.text.partition('🛡')[2]
            try:
                additional_defense = int(text[text.find('+') + 1:text.find(')')])
            except ValueError:
                try:
                    additional_defense = int(text[text.find('-'): text.find(')')])
                except ValueError:
                    logging.error(traceback.format_exc())
                    additional_defense = 0

        request = "INSERT INTO reports(user_id, battle_id, date_in, report_attack, report_defense," \
                  " report_lvl, report_exp, report_gold, report_stock, critical_strike, guardian_angel," \
                  " additional_attack, additional_defense) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(request, (
        row[0], battle_id, time.strftime('%Y-%m-%d %H:%M:%S'), attack, defense, lvl, exp, gold, stock, critical,
        guardian, additional_attack, additional_defense))

        # bot.send_message(chat_id=-1001197381190, text='Репорт успешно учтён для пользователя @' + mes.from_user.username)
        try:
            bot.send_message(chat_id=update.message.from_user.id, text='Репорт учтён. Спасибо!')
        except TelegramError:
            pass
        now = datetime.datetime.now(tz=moscow_tz).replace(
            tzinfo=None) - datetime.datetime.combine(datetime.datetime.now().date(), datetime.time(hour=0))
        if now < datetime.timedelta(hours=1):
            remaining_time = datetime.timedelta(hours=1) - now
            time_from_battle = datetime.timedelta(hours=8) - remaining_time
        else:
            time_from_battle = now - datetime.timedelta(hours=1)
            while time_from_battle > datetime.timedelta(hours=8):
                time_from_battle -= datetime.timedelta(hours=8)

        time_from_receiving_report = datetime.datetime.now(tz=moscow_tz).replace(
            tzinfo=None) - forward_message_date

        if time_from_receiving_report < time_from_battle:
            #   Репорт с последней битвы
            if mes.text.find("]") > 0:
                guild_tag = str(mes.text[2:mes.text.find(']')].upper())
                guild_reports = reports_count.get(guild_tag)
                if guild_reports is None:
                    guild_reports = GuildReports(guild_tag)
                current_report = Report(mes.from_user.id, mes.text[0], mes.text[1:].partition('⚔')[0], lvl, exp,
                                        gold, stock, attack, defense, datetime.datetime.now(moscow_tz).replace(tzinfo=None))
                guild_reports.add_report(current_report)
                reports_count.update({guild_tag: guild_reports})
                chat_id = guilds_chat_ids.get(guild_tag)
                if chat_id is not None:
                    percent = (guild_reports.num_reports / guild_reports.num_players) * 100
                    response = "Репорт от <b>{0}</b> принят.\nВсего сдало репортов <b>{1}</b> человек, это <b>{2:.2f}</b>% " \
                               "от общего числа\n".format(current_report.nickname, guild_reports.num_reports,
                                                          percent)
                    if guild_reports.num_reports == 1:
                        response += '{0} \n \n 🏅 Первый репорт в гильдии!'.format(response)
                    if percent == 100:
                        response += "Все сдали репорты! Какие вы лапочки!"

                    else:
                        if time_from_battle > datetime.timedelta(hours=1):
                            response += "Всё ещё не сдали репорты:\n"
                            for user in guild_reports.users:
                                if not user.report_sent:
                                    response += "<b>{0}</b>,    ".format(user.username)
                            response = response[:-5]    # Обрезаю последнюю запятую

                        else:
                            return  # В первый час бот не сообщает о репорте в чат
                    try:
                        bot.sync_send_message(chat_id=chat_id, text=response, parse_mode='HTML')
                    except TelegramError:
                        bot.send_message(chat_id=admin_ids[0], text=response, parse_mode='HTML')
