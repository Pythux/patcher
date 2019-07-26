import os


def str_digit(nb, nb_digit):
    str_nb = str(nb)
    zero_to_add = max(0, nb_digit - len(str_nb))
    return '0' * zero_to_add + str_nb


def dir_patch_name(nb):
    return 'xpatch-' + str_digit(nb, 2)


def create_dirs(save_path):
    li_dir_to_create = [
        'src_new',
        'src',
    ]
    for dir_name in li_dir_to_create:
        os.makedirs(os.path.join(save_path, dir_name))


def init_folders_if_needed(data_path, save_path):
    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    if os.listdir(save_path) == []:
        create_dirs(save_path)

    if not os.path.isdir(data_path):
        os.makedirs(data_path)
