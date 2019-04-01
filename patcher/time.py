import math
from datetime import datetime

from patcher.init import sql


def get_last_save_time():
    last = sql('select last_save from patcher_last_save' +
               ' order by last_save desc limit 1')
    if last == []:
        return None
    return last[0][0]


def insert_last_save_time(last_save):
    id_inserted = sql(
        "insert into patcher_last_save(last_save) values (?)", last_save)
    sql("delete from patcher_last_save where id <> ?", id_inserted)


def time_in_mn_since_last_save():
    now = datetime.now()
    last_scan = get_last_save_time()
    if not last_scan:
        return None
    time_delta = now - last_scan
    return math.ceil(time_delta.seconds / 60)
