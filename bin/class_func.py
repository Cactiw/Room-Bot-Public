import logging, datetime, random

from work_materials.globals import *
from work_materials.constants import archer_photo_ids, sentinel_photo_ids, knight_photo_ids


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

def knight_critical(bot, update):
    file_id = random.choice(knight_photo_ids)
    response = "Сегодня на поле боя ты показал невиданную храбрость, и удача к тебе была благосконна - твоя ярость" \
               " не знала границ, твои соратники уважительно преклоняют голову перед тобой"
    bot.sendPhoto(chat_id = update.message.chat_id, reply_to_message_id = update.message.message_id,
                     caption = response, photo=file_id)

def sentinel_critical(bot, update):
    file_id = random.choice(sentinel_photo_ids)
    response = "Зачастую люди рискуют другими, чтобы защитить себя. Истинный Защитник рискует собой, дабы защитить других.\n" \
               "Сегодня ты сражался за всех тех людей, что остались в замке и со страхом ждали конца сражения."
    bot.sendPhoto(chat_id = update.message.chat_id, reply_to_message_id = update.message.message_id,
                     caption = response, photo=file_id)


def ranger_notify(bot, job):
    context = job.context
    response = "Поднимай свой лук, <b>{0}</b>\n@{1}".format(context[1], context[0])
    file_id = random.choice(archer_photo_ids)
    try:
        bot.sendPhoto(chat_id=context[2], caption=response, photo=file_id, parse_mode='HTML')
    except BadRequest:
        bot.send_message(chat_id = admin_ids[0], text = "Ошибка при отправке уведомления лучнику, photo_id =\n{0}".format(file_id))


def rangers_notify_start(bot, update, time_to_battle):
    try:
        callback_chat_id = update.message.chat_id
    except AttributeError:
        try:
            callback_chat_id = int(update)
        except TypeError:
            return
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
    bot.send_message(chat_id = callback_chat_id, text = "Запланировано оповещение <b>{0}</b> бедных лучников".format(count),
                     parse_mode = 'HTML')
