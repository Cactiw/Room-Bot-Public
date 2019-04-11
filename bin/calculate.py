import math


def calculate_pogs(bot, update, args):
    mes = update.message
    if not args or len(args) < 2:
        bot.send_message(chat_id=mes.chat_id, text="Неверный синтаксис")
        return
    try:
        num_threads = int(args[0])
        price = int(args[1])
    except ValueError:
        bot.send_message(chat_id=mes.chat_id, text="Неверный синтаксис")
        return
    threads_need_per_pog = math.ceil(120.0/price) + 12
    num_pogs = num_threads//threads_need_per_pog
    num_threads_to_be_sold = (threads_need_per_pog - 12) * num_pogs
    bot.send_message(chat_id=mes.chat_id, text="Для крафта <b>{}</b> 👝 нужно продать <b>{}</b> thread "
                                               "по <b>{}</b>💰".format(num_pogs, num_threads_to_be_sold, price),
                     parse_mode = 'HTML')
