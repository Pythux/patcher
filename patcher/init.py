import os
import sys
import json
from tools.path import to_absolute_path
from database.connection import sql_sqlite


test_disk_dir = '/tmp/test_lswf/on_disk'
test_ram_dir = '/tmp/test_lswf/on_ram'


# ! loading config
with open('config.json') as conf:
    conf = json.loads(conf.read())
    db_name = conf['db_name']
    disk_dir = to_absolute_path(conf['data_store_on_disk'])
    ram_dir = to_absolute_path(conf['ram_directory'])
    if hasattr(sys, '_called_from_test'):
        disk_dir = test_disk_dir
        ram_dir = test_ram_dir

    disk_data = os.path.join(disk_dir, 'data')
    ram_data = os.path.join(ram_dir, 'data')


def sql(req, *params):
    return sql_sqlite(os.path.join(ram_dir, db_name), req, *params)


def create_table():
    create_tables = ['''
        CREATE TABLE patcher_last_save
            (id INTEGER PRIMARY KEY NOT NULL,
            last_save timestamp UNIQUE NOT NULL)
        ''']

    for table in create_tables:
        sql(table)


def try_create_table():
    is_table_exist = sql(
        "SELECT name FROM sqlite_master" +
        " WHERE type='table' AND name='patcher_last_save';")
    if is_table_exist == []:
        create_table()


def str_digit(nb, nb_digit):
    str_nb = str(nb)
    zero_to_add = max(0, nb_digit - len(str_nb))
    return '0' * zero_to_add + str_nb


def dir_patch_name(nb):
    return 'xpatch-' + str_digit(nb, 2)


def create_dirs():
    li_dir_to_create = [
        'src_new',
        'src',
    ]
    li_dir_to_create += [dir_patch_name(i) for i in range(1, 3)]
    for dir_name in li_dir_to_create:
        os.makedirs(os.path.join(disk_data, dir_name))


def init_if_needed():
    if not os.path.isfile(os.path.join(disk_dir, db_name)):
        os.makedirs(disk_data)
        create_table()
    try_create_table()
    if os.listdir(disk_data) == []:
        create_dirs()


if __name__ == "__main__":
    init_if_needed()
