import os
from os.path import join as pj
import bsdiff4

from tools.log import logi

from patcher.init import dir_patch_name
from patcher.filesys import (
    get_binary_file_content, create_binary_file, delete_old_and_mv_new_to_src)


def reconstitute_file(relative_path, save_path):
    src_file = get_binary_file_content(pj(save_path, 'src', relative_path))
    li_patch = get_li_patch(relative_path, save_path)
    return compose_patch(src_file, *li_patch)


def get_li_patch(relative_path, save_path):
    li_patch = []
    i = 0
    while True:
        i += 1
        patch_dir = os.path.join(save_path, dir_patch_name(i))
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


def add_new_patch(relative_path, patch, patch_index, save_path):
    patch_dir = os.path.join(save_path, dir_patch_name(patch_index))
    if not os.path.isdir(patch_dir):
        os.makedirs(patch_dir)
    create_binary_file(
        os.path.join(patch_dir, relative_path), patch)


def try_patch(relative_path, data_path, save_path):
    current_file = get_binary_file_content(pj(data_path, relative_path))
    src_file = get_binary_file_content(pj(save_path, 'src', relative_path))
    li_patch = get_li_patch(relative_path, save_path)
    file_stored = compose_patch(src_file, *li_patch)
    if current_file != file_stored:
        patch = bsdiff4.diff(file_stored, current_file)
        total_size_in_disk = len(src_file) + sum(map(len, li_patch))
        len_ram_file = len(current_file)
        if len(patch) < len_ram_file and total_size_in_disk < len_ram_file * 3:
            logi('add new patch for: {}'.format(relative_path))
            add_new_patch(relative_path, patch, len(li_patch) + 1)
        else:
            logi('del olds patch and create src_new for ' + relative_path)
            create_binary_file(
                os.path.join(save_path, 'src_new', relative_path),
                current_file)
            delete_old_and_mv_new_to_src(save_path)
    # else:
    #     logi('no change for: ' + relative_path)
