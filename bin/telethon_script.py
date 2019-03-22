from telethon import TelegramClient, events
from telethon.utils import PeerChannel

from work_materials.globals import RESULTS_PARSE_CHANNEL_ID, TEST_CHANNEL_ID, castles_stats_queue

from config import phone, username, password, api_id, api_hash


def script_work():
    global client
    admin_client = TelegramClient(username, api_id, api_hash, update_workers=1, spawn_read_thread=False)
    admin_client.start(phone, password)

    client = admin_client
    admin_client.get_entity("ChatWarsBot")
    client.add_event_handler(stats_handler, event=events.NewMessage)
    print("telegram script launched")
    #timer = Timer(interval=5, function=update_guild_stats, args=[client, True]).start()

    admin_client.idle()


def stats_handler(event):
    text = event.message.message
    #print(text.split("\n\n"))
    if event.message.to_id == PeerChannel(TEST_CHANNEL_ID):
        castles_stats_queue.put(text)
        return