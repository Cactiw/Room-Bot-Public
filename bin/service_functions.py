from work_materials.globals import moscow_tz
import datetime


def get_time_remaining_to_battle():
    now = datetime.datetime.now(tz=moscow_tz).replace(tzinfo=None) - datetime.datetime.combine(
        datetime.datetime.now().date(), datetime.time(hour=0))
    if now < datetime.timedelta(hours=1):

        return datetime.timedelta(hours=1) - now
    time_from_first_battle = now - datetime.timedelta(hours=1)
    while time_from_first_battle > datetime.timedelta(hours=8):
        time_from_first_battle -= datetime.timedelta(hours=8)
    time_remaining = datetime.timedelta(hours=8) - time_from_first_battle
    return time_remaining
