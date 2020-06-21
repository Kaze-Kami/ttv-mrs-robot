"""
Created by Joscha Vack on 1/13/2020.
"""

import codecs
import shutil
import json
import os

from lib.logger import log_call, log


def write_json(path, data, js=False):
    log_call('file_io:_write_json')
    with codecs.open(path, encoding="utf8", mode="w+") as f:
        json.dump(data, f, ensure_ascii=False)
    if js:
        with codecs.open(path.replace("json", "js"), encoding="utf8", mode="w+") as f:
            f.write("var settings = {0};".format(json.dumps(data, ensure_ascii=False).encode('utf8')))


def read_json(path):
    log_call('file_io:_read_json')
    with codecs.open(path, encoding="utf8", mode="r") as f:
        return json.load(f, encoding="utf8")


def exists_backup(path):
    log_call('file_io:exists_backup', path=path)
    return os.path.exists(path.replace('.json', '_backup.json'))


def backup_file(path):
    log_call('file_io:backup_file', path=path)
    backup_path = path.replace('.json', '_backup.json')
    shutil.copy(path, backup_path)
    log('info', 'Backed up file %s to %s' % (str(path), str(backup_path)))


def restore_file(path):
    log_call('file_io:restore_file', path=path)
    backup_path = path.replace('.json', '_backup.json')
    shutil.copy(backup_path, path)
    log('info', 'Restored file %s from %s' % (str(path), str(backup_path)))
