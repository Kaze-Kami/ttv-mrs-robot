"""
Created by Joscha Vack on 1/7/2020.
"""
import codecs
import os
from os import path
from datetime import date

from lib import global_variables
from lib import info

log_levels = {
    'trace': 0,
    'debug': 1,
    'info': 2,
    'warn': 3,
    'error': 4,
    'none': 5
}

last_log_file = 0

log_level = log_levels['info']


def next_log_file():
    if 100000 < os.path.getsize(global_variables.log_file):
        global last_log_file
        while os.path.exists(path.join(global_variables.log_dir, date.today().isoformat() + '-%d.log' % last_log_file)):
            last_log_file += 1

        # set new log file
        global_variables.log_file = path.join(global_variables.log_dir, date.today().isoformat() + '-%d.log' % last_log_file)
        log('info', 'Created new log file: %s' % str(global_variables.log_file))


def make_log_file():
    # check log dir
    if not path.exists(global_variables.log_dir):
        os.mkdir(global_variables.log_dir)

    for f in os.listdir(global_variables.log_dir):
        os.remove(os.path.join(global_variables.log_dir, f))

    # reset last log file
    global last_log_file
    last_log_file = 0
    global_variables.log_file = path.join(global_variables.log_dir, date.today().isoformat() + '-0.log')
    with open(global_variables.log_file, 'a'):
        pass
    next_log_file()


def log_call(fun, level_trace=True, **kwargs):
    args = ', '.join(['%s=%s' % (k, str(v)) for k, v in kwargs.items()])
    log('trace' if level_trace else 'debug', 'function %s(%s)' % (fun, args), 'trace')


def log(level, msg, kind=None):
    if not kind:
        kind = level
    global log_level
    # log to console
    msg = '[%s]: %s' % (kind.upper(), msg)
    if log_level <= log_levels[level]:
        global_variables.parent.Log(info.script_name, msg)

    # log to file
    next_log_file()
    with codecs.open(global_variables.log_file, encoding='utf-8-sig', mode='a') as f:
        f.write(msg)
        f.write('\n')
