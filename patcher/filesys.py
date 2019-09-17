import os
from os.path import join as pj
import shutil
from tools.path import get_relative_path

from patcher.init import dir_patch_name


def get_binary_file_content(path):
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            return f.read()
    if os.path.exists(path):
        raise SystemError('path must be a file, path: ' + path)
    return None


def create_binary_file(path, content):
    dirs, _ = os.path.split(path)
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    with open(path, 'wb') as f:
        f.write(content)


def copy_data_in_src(abs_path, data_path, save_path):
    relative_path = get_relative_path(data_path, abs_path)
    relavive_path_to_make, name_to_copy = os.path.split(relative_path)
    path_src_to_make = pj(save_path, 'src', relavive_path_to_make)
    path_dest = pj(path_src_to_make, name_to_copy)

    if not os.path.exists(path_src_to_make):
        os.makedirs(path_src_to_make)

    if os.path.isdir(abs_path):
        shutil.copytree(abs_path, path_dest)
    else:
        shutil.copy2(abs_path, path_dest)


def delete_old_and_mv_new_to_src(save_path):
    """only work on file/dir in "src_new",
       a file/dir in "src_new" means it's already exist
        at least in "src" folder

        if there is files/dirs in "src_new":
            for each, delete it's occurence in
                src, xpatch-1, 2, ...
            move the file to "src"
            delete emptied dir in src_new
    """
    src_new = pj(save_path, 'src_new')
    walk = os.walk(src_new, topdown=False)
    for dirpath, dirnames, filenames in walk:
        for file_name in filenames:
            relative_path = get_relative_path(src_new, pj(dirpath, file_name))

            delete_olds(relative_path, save_path)
            os.rename(pj(save_path, 'src_new', relative_path),
                      pj(save_path, 'src', relative_path))

        for emptied_dir in dirnames:
            os.rmdir(pj(dirpath, emptied_dir))


def delete_olds(relative_path, save_path):
    try_delete(pj(save_path, 'src', relative_path))
    delete_patchs(relative_path, save_path)


def delete_path(path):
    delete_fn = shutil.rmtree
    if os.path.isfile(path):
        delete_fn = os.unlink
    delete_fn(path)


def try_delete(path):
    if os.path.exists(path):
        delete_path(path)
        return True
    return False


def delete_patchs(relative_path, save_path):
    i = 0
    while True:
        i += 1
        patch_dir = pj(save_path, dir_patch_name(i))
        deleted_somthing = try_delete(pj(patch_dir, relative_path))
        if deleted_somthing:
            if os.listdir(patch_dir) == []:
                shutil.rmtree(patch_dir)
        else:
            break
