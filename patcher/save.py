import os
from os.path import join as pj

from tools.log import logi
from tools.path import get_relative_path, scan_file_dir

from patcher.init import init_if_needed
from patcher.patch import try_patch
from patcher.filesys import (
    copy_data_in_src, delete_olds, delete_old_and_mv_new_to_src)


def fn_dir(relative_path, data_path, save_path):
    """diff in dir means new or deleted files/dirs
        we will only handle the deleted files/dirs here"""
    data_list_dir = set(os.listdir(pj(save_path, relative_path)))
    src_list_dir = set(os.listdir(pj(data_path, 'src', relative_path)))
    deleted = src_list_dir - data_list_dir
    for del_file_dir in deleted:
        delete_olds(pj(relative_path, del_file_dir))


def fn_dir_and_file(abs_path, data_path, save_path):
    relative_path = get_relative_path(data_path, abs_path)
    if not os.path.exists(pj(save_path, 'src', relative_path)):
        logi('create src: ' + pj(save_path, 'src', relative_path))
        copy_data_in_src(abs_path)
    else:
        if os.path.isfile(abs_path):
            try_patch(relative_path)
        else:
            fn_dir(relative_path)


def save(data_path, save_path, change_since_mn=None):
    init_if_needed(data_path, save_path)
    # if the systeme have shutdown at the wrong moment,
    # there may be files in "src_new" to process
    # to return to a proper state
    delete_old_and_mv_new_to_src(save_path)

    scan_file_dir(data_path, 100, change_since_mn,
                  fn_dir_and_file, fn_dir_and_file)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    # save the diff from last save
    save()
