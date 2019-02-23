import traceback, logging

def create_sticker_set(bot, update):
    #bot.createNewStickerSet(user_id=update.message.from_user.id, name = "brash_by_My_order_dev_bot", title = "brash", png_sticker=update.message.reply_to_message.sticker.file_id,
    #                        emojis=update.message.reply_to_message.sticker.emoji)
    print("success")


def send_sticker_emoji(bot, update):
    try:
        emoji = update.message.reply_to_message.sticker.emoji
    except Exception:
        logging.error(traceback.format_exc())
        return
    response = "{0}".format(emoji)
    bot.send_message(chat_id = update.message.chat_id, text=response)
