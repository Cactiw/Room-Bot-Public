from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerChannel

from work_materials.globals import RESULTS_PARSE_CHANNEL_ID, TEST_CHANNEL_ID, castles_stats_queue

try:
    from config import phone, username, password, api_id, api_hash
except ImportError:
    pass


def script_work():
    global client
    admin_client = TelegramClient(username, api_id, api_hash)
    admin_client.start(phone, password)

    with admin_client as client:
        admin_client.get_entity("ChatWarsBot")
        client.add_event_handler(stats_handler, event=events.NewMessage)
        print("telegram script launched")

        admin_client.run_until_disconnected()


async def stats_handler(event):
    text = event.message.message
    if event.message.to_id == PeerChannel(RESULTS_PARSE_CHANNEL_ID) and 'Результаты сражений:' in text:
        print("put stats in queue")
        castles_stats_queue.put(text)
        return
