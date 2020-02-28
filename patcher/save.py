import os
from os.path import join as pj
import shutil

from tools.log import logi, logd
from tools.path import get_relative_path, scan_file_dir
from tools.tar import make_tar

from patcher.init import init_folders_if_needed

from patcher.filesys import (
    copy_data_in_src, delete_olds, delete_old_and_mv_new_to_src, delete_path)


def fn_dir(relative_path, data_path, save_path):
    """diff in dir means new or deleted files/dirs
        we will only handle the deleted files/dirs here"""
    data_list_dir = set(os.listdir(pj(data_path, relative_path)))
    src_list_dir = set(os.listdir(pj(save_path, 'src', relative_path)))
    deleted = src_list_dir - data_list_dir
    for del_file_dir in deleted:
        delete_olds(pj(relative_path, del_file_dir), save_path)


def fn_dir_and_file_with_path(abs_path, data_path, save_path, try_patch):
    relative_path = get_relative_path(data_path, abs_path)
    if not os.path.exists(pj(save_path, 'src', relative_path)):
        logi('create src: ' + pj(save_path, 'src', relative_path))
        copy_data_in_src(abs_path, data_path, save_path)
    else:
        if os.path.isfile(abs_path):
            try_patch(relative_path, data_path, save_path)
        else:
            fn_dir(relative_path, data_path, save_path)


def save(data_path, save_path, save_mode=None, change_since_mn=None):
    init_folders_if_needed(data_path, save_path)
    # if the systeme have shutdown at the wrong moment,
    # there may be files in "src_new" to process
    # to return to a proper state
    delete_old_and_mv_new_to_src(save_path)
    if save_mode == 'patch file by file':
        from patcher.patch import try_patch

        def fn_dir_and_file(abs_path):
            fn_dir_and_file_with_path(abs_path, data_path, save_path, try_patch)

        scan_file_dir(data_path, None, change_since_mn,
                      fn_dir_and_file, fn_dir_and_file)

    elif save_mode == 'all in one':
        make_tar(data_path)
        tar_ram_path = data_path + '.tar'
        tar_disk_path = pj(save_path, os.path.basename(save_path)) + '.tar'
        # too much time and RAM to process
        # fn_dir_and_file_with_path(tar_path, os.path.dirname(data_path), save_path)
        if not os.path.exists(tar_disk_path):
            shutil.copy2(tar_ram_path, tar_disk_path)
        else:
            with open(tar_ram_path, 'rb') as ram_tar:
                with open(tar_disk_path, 'wb') as disk_tar:
                    disk_tar.write(ram_tar.read())
        os.unlink(tar_ram_path)

    elif save_mode == 'overide file by file':
        init_folders_if_needed(data_path, save_path)
        save_path = pj(save_path, 'src')
        walk = os.walk(data_path)
        for dirpath, dirnames, filenames in walk:
            for file_name in filenames:
                relative_path = get_relative_path(data_path, pj(dirpath, file_name))
                with open(pj(save_path, relative_path), 'wb') as fp_disk:
                    with open(pj(dirpath, file_name), 'rb') as fp_ram:
                        fp_disk.write(fp_ram.read())

            for dir_name in dirnames:
                relative_path = get_relative_path(data_path, pj(dirpath, dir_name))
                dir_disk_path = pj(save_path, relative_path)
                dir_ram_path = pj(dirpath, dir_name)
                try_make_dirs(dir_disk_path)
                set_disk = set(os.listdir(dir_disk_path))
                set_ram = set(os.listdir(dir_ram_path))
                for to_delete in set_disk - set_ram:
                    logd('delete: ' + pj(dir_disk_path, to_delete))
                    delete_path(pj(dir_disk_path, to_delete))
    else:
        logi('save_mode: "{}" not implemented'.format(save_mode))


def try_make_dirs(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
