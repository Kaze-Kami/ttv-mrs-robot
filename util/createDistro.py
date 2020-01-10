"""
Created by Joscha Vack on 1/5/2020.
"""

from zipfile import ZipFile
from os import path, remove, listdir, mkdir
from shutil import copy


def file_paths(root, base=''):
    """
    Recursively lists all files in a directory
    """

    paths = []
    for e in listdir(root):
        p = path.join(root, e)
        if path.isdir(p):
            paths.extend(file_paths(p, base=e))
        else:
            paths.append(path.join(base, e))
    return paths


def remove_files(root):
    # for what ever reason we have to delete folders recursively - i guess ;_;
    if not path.exists(dist_path):
        return

    files = list(listdir(root))
    for e in files:
        p = path.join(root, e)
        if path.isdir(p):
            remove_files(p)
        else:
            remove(p)


if __name__ == '__main__':
    # dirs to copy
    base_path = path.join(r'D:\Dev\Python\JGambleSystem')
    dist_path = path.join(base_path, r'dist\JGambleSystem.zip')
    lib_path = path.join(base_path, 'lib')
    overlays_path = path.join(base_path, 'Overlays')
    resource_path = path.join(base_path, 'resources')

    # zip root folder
    zip_root = path.join('JGambleSystem')

    # streamlabs scripts dir
    scripts_path = path.join(r'C:\Users\Kanjiu Akuma\AppData\Roaming\Streamlabs\Streamlabs Chatbot\Services\Scripts\JGambleSystem')
    if not path.exists(scripts_path):
        mkdir(scripts_path)
    remove_files(scripts_path)

    print('Creating distribution at "%s"' % dist_path)
    # remove old zip if exists
    if path.exists(dist_path):
        remove(dist_path)

    # create folders if necessary
    if not path.exists(path.join(scripts_path, 'lib')):
        mkdir(path.join(scripts_path, 'lib'))
    if not path.exists(path.join(scripts_path, 'Overlays')):
        mkdir(path.join(scripts_path, 'Overlays'))
    if not path.exists(path.join(scripts_path, 'resources')):
        mkdir(path.join(scripts_path, 'resources'))

    with ZipFile(path.join(dist_path), mode='w') as zf:
        for dr in listdir(base_path):
            if dr not in ['.idea', 'util', 'dist', 'LICENSE', '.gitignore', '.git']:
                if path.isdir(path.join(base_path, dr)):
                    fl = file_paths(path.join(base_path, dr))
                    for f in fl:
                        zf.write(path.join(base_path, dr, f), path.join(dr, f))
                        copy(path.join(base_path, dr, f), path.join(scripts_path, dr, f))
                else:
                    zf.write(path.join(base_path, dr), dr)
                    copy(path.join(base_path, dr), path.join(scripts_path, dr))

