import os

import bsdiff4

from patcher.init import disk_data, dir_patch_name
from patcher.filesys import get_binary_file_content, create_binary_file


def get_li_patch(relative_path):
    li_patch = []
    i = 0
    while True:
        i += 1
        patch_dir = os.path.join(disk_data, dir_patch_name(i))
        if os.path.isdir(patch_dir):
            binary = get_binary_file_content(
                os.path.join(patch_dir, relative_path))
            if binary is not None:
                li_patch.append(binary)
        else:
            break
    return li_patch


def compose_patch(*li_content):
    if len(li_content) == 0:
        raise SystemError('compose_patch need at least one element, not 0')
    elif len(li_content) == 1:
        return li_content[0]

    a, b, *t = li_content
    return compose_patch(bsdiff4.patch(a, b), *t)


def add_new_patch(relative_path, patch, patch_index):
    patch_dir = os.path.join(disk_data, dir_patch_name(patch_index))
    if not os.path.isdir(patch_dir):
        os.makedirs(patch_dir)
    create_binary_file(
        os.path.join(patch_dir, relative_path), patch)
