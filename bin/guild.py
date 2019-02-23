from work_materials.globals import cursor, guilds_name_to_tag
from libs.guild import User_for_attack, User
from bin.service_functions import get_time_remaining_to_battle
import datetime

ping_by_chat_id = {}


def g_info(bot, update):
    mes = update.message
    request = "SELECT username, user_lvl, user_attack, user_defense FROM users WHERE guild = %s ORDER BY user_lvl DESC"
    cursor.execute(request, (mes.text.split(' ')[1],))
    row = cursor.fetchone()

    response = "Статистика по гильдии <b>" + mes.text.split(' ')[1] + "</b>:\n"

    total_attack = 0
    total_defense = 0
    max_lvl = 0
    max_lvl_user = ""

    count = 1
    while row:
        response = response + '\n' + "{0}: <b>".format(count) + row[0] + "</b>" + "\n🏅" + str(row[1]) + " ⚔" + str(row[2]) + " 🛡" + str(row[3]) + '\n'
        total_attack += row[2]
        total_defense += row[3]
        if row[1] > max_lvl:
            max_lvl = row[1]
            max_lvl_user = row[0]

        row = cursor.fetchone()
        count += 1
    count -= 1
    response += "\n\n" + "Всего игроков: {0}\nВсего атаки: ⚔".format(count) + str(total_attack) + ", всего защиты: 🛡" + str(total_defense)
    response += "\n" + "Максимальный уровень у <b>" + max_lvl_user + "</b>, 🏅" + str(max_lvl)
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def notify_guild_attack(bot, update):
    print(get_time_remaining_to_battle())
    mes = update.message
    remaining_time = get_time_remaining_to_battle()
    if mes.forward_date - datetime.datetime.now() > datetime.timedelta(minutes=2):
        return 0
    if remaining_time > datetime.timedelta(minutes=15):
        return 0
    ready_to_battle = mes.text.count("[⚔]") + mes.text.count("[🛡]")
    sleeping = mes.text.count("[🛌]")
    print("sleeping =", sleeping)
    response = "<b>{0}</b>\nГотово к битве: <b>{1}</b>\nНе готово к битве, но занято <b>{2}</b>\n" \
               "Спит: <b>{3}</b>\n\nВремя до битвы: {4}\n".format(mes.text.splitlines()[0], ready_to_battle,
                                                                mes.text.count("\n") - ready_to_battle - sleeping,
                                                                sleeping, ":".join(str(remaining_time).partition(".")[0].split(":")[0:3]))
    tag = guilds_name_to_tag.get(mes.text.splitlines()[0][1:])
    if tag is not None:
        do_not_ready = []
        sleeping = []
        for string in mes.text.splitlines()[1:]:
            if not ("[⚔]" in string or "[🛡]" in string):
                nickname = string.partition("]")[2][1:]
                do_not_ready.append(nickname)
                if "[🛌]" in string:
                    sleeping.append(nickname)

        request = "select username, telegram_username from users where guild = %s"
        cursor.execute(request, (tag,))
        row = cursor.fetchone()
        in_dict_do_not_ready = []
        in_dict_sleeping = []
        ping_dict = {"do not ready" : in_dict_do_not_ready, "sleeping" : in_dict_sleeping}
        while row:
            db_nickname = row[0].partition("]")[2]
            if db_nickname in do_not_ready:
                in_dict_do_not_ready.append(row[1])
                if db_nickname in sleeping:
                    in_dict_sleeping.append(row[1])

            row = cursor.fetchone()
        ping_by_chat_id.update({mes.chat_id : ping_dict})
        response += "Пингануть тех, кто спит: /notify_guild_sleeping\n" \
                    "Пингануть всех, кто не готов: /notify_guild_not_ready"
    bot.send_message(chat_id = mes.chat_id, text = response, parse_mode = 'HTML')


def notify_guild_to_battle(bot, update):
    mes = update.message
    chat_dict = ping_by_chat_id.get(mes.chat_id)
    if chat_dict is None:
        return
    print(chat_dict, chat_dict.get("sleeping"))
    if mes.text.partition("@")[0].split("_")[2] == "sleeping":
        target_list = chat_dict.get("sleeping")
    else:
        target_list = chat_dict.get("do not ready")
    print(target_list)
    i = 0
    response = ""
    for username in target_list:
        if i >= 4:
            response += "\n БИТВА!"
            bot.send_message(chat_id = mes.chat_id, text = response)
            response = ""
            i = 0
        response += "@{0} ".format(username)
        i += 1
    response += "\n БИТВА!"
    bot.send_message(chat_id=mes.chat_id, text=response)


def g_attack(bot, update):
    mes = update.message
    num_users = 0
    total_attack = 0
    users = []
    num_guilds = int(mes.text.split(' ')[1])
    for i in g_attacking_users:
        num_users += 1
        total_attack += i.attack
        users.append(User_for_attack(i.username, i.attack, -1))



    ratio = mes.text.split(' ')[2]
    ratios = ratio.split(':')
    sum_ratio = 0
    for i in range(0, num_guilds):
        sum_ratio += int(ratios[i])
    # print(ratios)
    attacks = [int] * num_guilds
    for i in range(0, num_guilds):
        attacks[i] = int(ratios[i]) / sum_ratio * total_attack
    # print("sum_attack = ", total_attack, attacks)
    #       Здесь кончается верный кусок кода
    for i in range(0, num_users):
        # print("i = ", i, "username = ", users[i].username)
        min_remain = 100000000  # Перестанет работать, если вдруг суммарная атака достигнет этой величины
        min_number = 0
        flag = 0
        for j in range(0, num_guilds):
            # print("attacks[", j, "] =", attacks[j])
            remain = attacks[j] - users[i].attack
            # print("remain =", remain)
            if remain < min_remain and remain >= 0:
                min_remain = remain
                min_number = j
                flag = 1
                # print("YES")
        if flag:  # Есть свободное место под этого атакующего
            users[i].g_attacking = min_number
            attacks[min_number] = min_remain
        else:
            min_remain = -100000000
            for j in range(0, num_guilds):
                remain = attacks[j] - users[i].attack
                # print(remain, min_remain, min_number)
                if remain > min_remain:
                    min_remain = remain
                    min_number = j
                    attacks[j] = remain
            users[i].g_attacking = min_number
    response = "Рассчёт распределения урона подготовлен:"
    for i in range(0, num_guilds):
        response += "\n" + str(i) + " гильдия:\n"
        guild_attack = 0
        for j in range(0, num_users):
            if users[j].g_attacking == i:
                response += "<b>" + users[j].username + "</b> ⚔" + str(users[j].attack) + "\n"
                guild_attack += users[j].attack
        response += "Total attack: ⚔" + str(guild_attack) + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def g_all_attack(bot, update):
    mes = update.message
    num_attacking_guilds = int(mes.text.split(' ')[1])
    request = "SELECT COUNT(1) FROM users WHERE guild = '{0}'".format(mes.text.split(' ')[2])
    request2 = "SELECT username, user_attack FROM users WHERE guild = '{0}'".format(mes.text.split(' ')[2])
    for i in range (1, num_attacking_guilds):
        request += " OR guild = '{0}'".format(mes.text.split(' ')[i + 2])    # TODO: сделать нормально
        request2 += " OR guild = '{0}'".format(mes.text.split(' ')[i + 2])

    request2 += " ORDER BY user_attack DESC"
    #print(request)
    #print(request2)
    num_guilds = int(mes.text.split(' ')[num_attacking_guilds + 2])
    cursor.execute(request)
    row = cursor.fetchone()

    num_users = int(row[0])

    users = []

    cursor.execute(request2)
    row = cursor.fetchone()
    total_attack = 0
    i = 0
    #print(num_users)
    while row:
        #print(row)
        total_attack += int(row[1])
        #users[i].attack = int(row[1])
        #users[i].username = row[0]
        users.append(User_for_attack(row[0], int(row[1]), -1))
        #print("i = ", i, "username = ", users[i].username)
        #print("username[0] = ", users[0].username)
        i += 1
        row = cursor.fetchone()

    #print(i)

    ratio = mes.text.split(' ')[num_attacking_guilds + 3]
    ratios = ratio.split(':')
    sum_ratio = 0
    for i in range (0, num_guilds):
        sum_ratio += int(ratios[i])
    #print(ratios)
    attacks = [int] * num_guilds
    for i in range (0, num_guilds):
        attacks[i] = int(ratios[i]) / sum_ratio * total_attack
    #print("sum_attack = ", total_attack, attacks)
    #       Здесь кончается верный кусок кода
    for i in range (0, num_users):
        #print("i = ", i, "username = ", users[i].username)
        min_remain = 100000000    #Перестанет работать, если вдруг суммарная атака достигнет этой величины
        min_number = 0
        flag = 0
        for j in range (0, num_guilds):
            #print("attacks[", j, "] =", attacks[j])
            remain = attacks[j] - users[i].attack
            #print("remain =", remain)
            if remain < min_remain and remain >= 0:
                min_remain = remain
                min_number = j
                flag = 1
                #print("YES")
        if flag: #  Есть свободное место под этого атакующего
            users[i].g_attacking = min_number
            attacks[min_number] = min_remain
        else:
            min_remain = -100000000
            for j in range(0, num_guilds):
                remain = attacks[j] - users[i].attack
                #print(remain, min_remain, min_number)
                if remain > min_remain:
                    min_remain = remain
                    min_number = j
                    attacks[j] = remain
            users[i].g_attacking = min_number
    response = "Рассчёт распределения урона подготовлен:"
    for i in range (0, num_guilds):
        response += "\n" + str(i) + " гильдия:\n"
        guild_attack = 0
        for j in range (0, num_users):
            if users[j].g_attacking == i:
                response += "<b>" + users[j].username + "</b> ⚔" + str(users[j].attack) + "\n"
                guild_attack += users[j].attack
        response += "Total attack: ⚔" + str(guild_attack) + "\n"
    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def g_add_attack(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_attack
    global g_attacking_users
    request = "SELECT user_attack, username FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.reply_to_message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text="Пользователь не найден в базе данных")
        return
    current = User(id, row[1], row[0], 0)
    for i in g_attacking_users:
        if i.id == id:
            bot.send_message(chat_id=update.message.chat_id, text="Игрок уже атакует")
            return
    g_added_attack += row[0]
    g_attacking_users.append(current)
    response = "Пользователь добавлен. Всего атаки на цель: ⚔<b>{0}</b>\n".format(g_added_attack)
    response += "Атакующие игроки:\n"
    g_attacking_users.sort(key = lambda curr:curr.attack, reverse = True)
    for i in g_attacking_users:
        response += "<b>{0}</b> ⚔<b>{1}</b>\n".format(i.username, i.attack)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def g_del_attack(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_attack
    global g_attacking_users
    for i in g_attacking_users:
        if i.id == id:
            g_added_attack -= i.attack
            g_attacking_users.remove(i)
            bot.send_message(chat_id=update.message.chat_id, text="Игрок успешно удалён")
            return
    bot.send_message(chat_id=update.message.chat_id, text="Игрок не найден в списке для атаки")


def g_attacking_list(bot, update):
    response = "Атакующие игроки:\n"
    g_attacking_users.sort(key=lambda curr: curr.attack, reverse=True)
    for i in g_attacking_users:
        response += "<b>{0}</b> ⚔<b>{1}</b>\n".format(i.username, i.attack)
    response += "\n\nВсего атаки: ⚔<b>{0}</b>".format(g_added_attack)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')

def g_add_defense(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_defense
    global g_defending_users
    request = "SELECT user_defense, username FROM users WHERE telegram_id = %s"
    cursor.execute(request, (mes.reply_to_message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        bot.send_message(chat_id=update.message.chat_id, text="Пользователь не найден в базе данных")
        return
    current = User(mes.reply_to_message.from_user.id, row[1], 0, row[0])
    for i in g_defending_users:
        if i.id == id:
            bot.send_message(chat_id=update.message.chat_id, text="Игрок уже защищает")
            return
    g_added_defense += row[0]
    g_defending_users.append(current)
    response = "Пользователь добавлен. Всего защиты: 🛡<b>{0}</b>\n".format(g_added_defense)
    response += "Атакующие игроки:\n"
    g_defending_users.sort(key = lambda curr:curr.defense, reverse = True)
    for i in g_defending_users:
        response += "<b>{0}</b> 🛡<b>{1}</b>\n".format(i.username, i.defense)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')


def g_del_defense(bot, update):
    mes = update.message
    id = mes.reply_to_message.from_user.id
    global g_added_defense
    global g_defending_users
    for i in g_defending_users:
        if i.id == id:
            g_added_defense -= i.defense
            g_defending_users.remove(i)
            bot.send_message(chat_id=update.message.chat_id, text="Игрок успешно удалён")
            return
    bot.send_message(chat_id=update.message.chat_id, text="Игрок не найден в списке для защиты")

def g_defending_list(bot, update):
    response = "Защищающие игроки:\n"
    g_defending_users.sort(key=lambda curr: curr.defense, reverse=True)
    for i in g_defending_users:
        response += "<b>{0}</b> 🛡<b>{1}</b>\n".format(i.username, i.defense)
    response += "\n\nВсего защиты: 🛡<b>{0}</b>".format(g_added_defense)

    bot.send_message(chat_id=update.message.chat_id, text=response, parse_mode='HTML')



def g_help(bot, update):
    bot.send_message(chat_id = update.message.chat_id, text = "Список команд для работы с гильдиями:\nhttps://orderbot.page.link/nM9x") # https://telegra.ph/Komandy-dlya-raboty-s-gildiyami-10-16
    return