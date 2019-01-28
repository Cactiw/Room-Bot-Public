import logging, datetime, random

from work_materials.globals import *

photo_ids = ['AgADAgADZqoxG6FDeEopaNAfHJyqCsRFXw8ABM1KXzxYZ8oC1EcBAAEC',
             'AgADAgADZ6oxG6FDeEqZfNoeKhCerClMOQ8ABJMXJ6sBF7i_wxACAAEC',
             'AgADAgADaKoxG6FDeEref06d_7R9qURFOQ8ABCo-MZ4mAe2r_xACAAEC',
             'AgADAgADaaoxG6FDeEowvAG50PFWHnteOQ8ABApYnLTxs53zVxICAAEC',
             'AgADAgAD7KoxG5BReUo0DFf7Z_CYF5xXXw8ABEXNR_JlVzKNi0YBAAEC'
             ]

def set_class(bot, update):
    print("here")
    mes = update.message
    current_class = mes.text.partition(" ")[0]
    if current_class in classes_list:
        class_skill = None
        if current_class == 'Ranger':
            class_skill = int(mes.text.partition("Aiming")[0][:-2].split()[-1])
            logging.info("class_skill = {0}".format(class_skill))

        request = "update users set user_class = %s, class_skill_lvl = %s where telegram_id = %s"
        cursor.execute(request, (current_class, class_skill, mes.from_user.id))
        bot.send_message(chat_id = mes.chat_id, text = "Класс успешно обновлён, <b>{0}</b>".format(current_class),
                         parse_mode = 'HTML')


def ranger_notify(bot, job):
    context = job.context
    response = "Поднимай свой лук, <b>{0}</b>\n@{1}".format(context[1], context[0])
    file_id = random.choice(photo_ids)
    bot.sendPhoto(chat_id=context[2], caption=response, photo=file_id, parse_mode='HTML')


def rangers_notify_start(bot, update, time_to_battle):
    guild_names = guilds_chat_ids.keys()
    count = 0
    for guild in guild_names:
        request = "select telegram_username, username, class_skill_lvl from users where guild = %s and class_skill_lvl is not NULL"
        cursor.execute(request, (guild, ))
        row = cursor.fetchone()
        chat_id =guilds_chat_ids.get(guild)
        while row:
            telegram_username = row[0]
            username = row[1]
            class_skill_lvl = row[2]
            context = [telegram_username, username, chat_id]
            print(class_skill_lvl)
            time_to_aim_mins = ranger_aiming_minutes[class_skill_lvl]
            time_to_aim = datetime.timedelta(minutes=time_to_aim_mins)
            time_to_notify = time_to_battle - time_to_aim
            if time_to_notify >= datetime.timedelta(minutes=0):
                job.run_once(ranger_notify, time_to_notify, context=context)
                #job.run_once(ranger_notify, 1, context=context)        TEST

            row = cursor.fetchone()
            count += 1
    bot.send_message(chat_id = update.message.chat_id, text = "Запланровано оповещение <b>{0}</b> бедных лучников".format(count),
                     parse_mode = 'HTML')
