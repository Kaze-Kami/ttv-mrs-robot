"""
Created by Joscha Vack on 1/7/2020.
"""

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

log_level = log_levels['info']


def make_log_file():
    # check log dir
    if not path.exists(global_variables.log_dir):
        os.mkdir(global_variables.log_dir)

    # set log file
    global_variables.log_file_path = path.join(global_variables.log_dir, date.today().isoformat() + '.log')
    log('info', 'Log file: ' + str(global_variables.log_file_path))


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
    with open(global_variables.log_file_path, 'a') as f:
        f.write(msg)
        f.write('\n')
