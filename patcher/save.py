import os
from os.path import join as pj
from datetime import datetime

import bsdiff4

import logging
import tools.log
from tools.path import get_relative_path, scan_file_dir
from patcher.init import init_if_needed, ram_data, disk_data

from patcher.time import time_in_mn_since_last_save, insert_last_save_time
from patcher.filesys import (
    get_binary_file_content, copy_data_in_src,
    create_binary_file, delete_old_and_mv_new_to_src, delete_olds)
from patcher.patch import get_li_patch, compose_patch, add_new_patch


def log(msg): tools.log.log(logging.info, msg, deep=2)


def fn_dir(relative_path):
    """diff in dir means new or deleted files/dirs
        we will only handle the deleted files/dirs here"""
    ram_list_dir = set(os.listdir(pj(ram_data, relative_path)))
    src_list_dir = set(os.listdir(pj(disk_data, 'src', relative_path)))
    deleted = src_list_dir - ram_list_dir
    for del_file_dir in deleted:
        delete_olds(pj(relative_path, del_file_dir))


def fn_dir_and_file(abs_path):
    relative_path = get_relative_path(ram_data, abs_path)
    if not os.path.exists(pj(disk_data, 'src', relative_path)):
        log('create src: ' + pj(disk_data, 'src', relative_path))
        copy_data_in_src(abs_path)
    else:
        if os.path.isfile(abs_path):
            try_patch(relative_path)
        else:
            fn_dir(relative_path)


def try_patch(relative_path):
    ram_file = get_binary_file_content(pj(ram_data, relative_path))
    src_file = get_binary_file_content(pj(disk_data, 'src', relative_path))
    li_patch = get_li_patch(relative_path)
    file_stored = compose_patch(src_file, *li_patch)
    if ram_file != file_stored:
        patch = bsdiff4.diff(file_stored, ram_file)
        total_size_in_disk = len(src_file) + sum(map(len, li_patch))
        len_ram_file = len(ram_file)
        if len(patch) < len_ram_file and total_size_in_disk < len_ram_file * 3:
            log('add new patch for: {}'.format(relative_path))
            add_new_patch(relative_path, patch, len(li_patch) + 1)
        else:
            log('del olds patch and create src_new for ' + relative_path)
            create_binary_file(
                os.path.join(disk_data, 'src_new', relative_path), ram_file)
            delete_old_and_mv_new_to_src()
    # else:
    #     log('no change for: ' + relative_path)


def save():
    start_saving = datetime.now()
    change_since_mn = time_in_mn_since_last_save()
    scan_file_dir(ram_data, 100, change_since_mn,
                  fn_dir_and_file, fn_dir_and_file)
    insert_last_save_time(start_saving)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    init_if_needed()

    # if the systeme have shutdown at the wrong moment,
    # there may be files in "src_new" to process
    # to return to a proper state
    delete_old_and_mv_new_to_src()

    # save the diff from last save
    save()
