import math
from datetime import datetime

from CRUD_vanilla.connection import sql_sqlite


def create_db(db_location):
    create_tables = ['''
        CREATE TABLE patcher_last_save
            (id INTEGER PRIMARY KEY NOT NULL,
            last_save timestamp UNIQUE NOT NULL)
        ''']

    for table in create_tables:
        sql_sqlite(db_location, table)


def get_last_save_time(db_location):
    last = sql_sqlite(
        db_location,
        'select last_save from patcher_last_save' +
        ' order by last_save desc limit 1')
    if last == []:
        return None
    return last[0][0]


def insert_last_save_time(last_save, db_location):
    id_inserted = sql_sqlite(
        db_location,
        "insert into patcher_last_save(last_save) values (?)", last_save)
    sql_sqlite(
        db_location,
        "delete from patcher_last_save where id <> ?", id_inserted)


def time_in_mn_since_last_save(db_location):
    now = datetime.now()
    last_scan = get_last_save_time(db_location)
    if not last_scan:
        return None
    time_delta = now - last_scan
    return math.ceil(time_delta.seconds / 60)
