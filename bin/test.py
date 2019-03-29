import sys, time
from telegram.ext import CommandHandler, MessageHandler, Filters
from work_materials.globals import dispatcher, updater, job


def message_test():
    from work_materials.globals import AUTO_TEST_CHANNEL_ID
    dispatcher.add_handler(MessageHandler(Filters.all, success))#sys.exit(0)))
    updater.start_polling(clean=False)
    print("sending to {}".format(AUTO_TEST_CHANNEL_ID))
    print("sending message")
    message1 = dispatcher.bot.sync_send_message(chat_id=AUTO_TEST_CHANNEL_ID, text='123')
    time.sleep(2)
    message2 = dispatcher.bot.sync_send_message(chat_id=AUTO_TEST_CHANNEL_ID, text='/test_message')
    updater.stop()
    if message1.chat_id == message2.chat_id == AUTO_TEST_CHANNEL_ID:
        print("test successful")
        sys.exit(0)
    sys.exit(1)


def success(bot, update):
    print(update)
    print("test successful")
    sys.exit(0)
