import os
from os.path import join as pj

from tools.path import get_relative_path
from patcher.init import init_folders_if_needed

from patcher.filesys import create_binary_file
from patcher.patch import reconstitute_file


def load(data_path, save_path):
    init_folders_if_needed(data_path, save_path)
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
