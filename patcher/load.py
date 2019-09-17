import os
from os.path import join as pj
import shutil

from tools.path import get_relative_path
from tools.tar import extract_tar
from tools.log import logi
from patcher.init import init_folders_if_needed

from patcher.filesys import create_binary_file
from patcher.patch import reconstitute_file


def load(save_path, data_path, save_mode=None):
    """load data in save_path to data_path"""
    if os.path.exists(data_path):
        logi('data already loaded in “{}”'.format(data_path))
        return

    if save_mode == 'patch file by file':
        init_folders_if_needed(data_path, save_path)
        load_file_by_file(save_path, data_path)

    elif save_mode == 'all in one':
        init_folders_if_needed(os.path.dirname(data_path), save_path)
        # make_tar(data_path)
        tar_ram_path = data_path + '.tar'
        tar_disk_path = pj(save_path, os.path.basename(save_path)) + '.tar'
        if not os.path.exists(tar_disk_path):
            logi('file: {} does not exist, can\'t load to {}'.format(tar_disk_path, data_path))
            return

        logi(tar_disk_path, tar_ram_path)
        shutil.copy2(tar_disk_path, tar_ram_path)
        extract_tar(tar_ram_path, extract_path=os.path.dirname(data_path))
        os.unlink(tar_ram_path)

    elif save_mode == 'overide file by file':
        init_folders_if_needed(os.path.dirname(data_path), save_path)
        shutil.copytree(pj(save_path, 'src'), data_path)

    else:
        logi('save_mode: "{}" not implemented'.format(save_mode))


def load_file_by_file(save_path, data_path):
    src = pj(save_path, 'src')
    walk = os.walk(src)
    for dirpath, dirnames, filenames in walk:
        for file_name in filenames:
            relative_path = get_relative_path(src, pj(dirpath, file_name))
            file = reconstitute_file(relative_path, save_path)
            create_binary_file(pj(data_path, relative_path), file)

        for dir_name in dirnames:
            relative_path = get_relative_path(src, pj(dirpath, dir_name))
            try:
                os.makedirs(pj(data_path, relative_path))
            except FileExistsError:
                pass
