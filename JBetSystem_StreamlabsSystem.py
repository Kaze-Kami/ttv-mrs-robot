# append lib to search path
import sys
import os

sys.path.append(os.path.dirname(__file__))

import clr
import traceback

from lib import info
from lib import global_variables
from lib import logger

from lib.logger import log_call, log, log_levels
from lib.config import load_config, save_config, default_config
from lib.bot import Bot

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

ScriptName = info.script_name
Website = info.website
Description = info.description
Creator = info.creator
Version = info.version

bot = None


# ---------------------------
#   Required functions
# ---------------------------
def Init():
    try:
        global_variables.parent = Parent
        # clear log file
        with open(global_variables.log_file_path, 'w'):
            pass

        log_call('JBetSystem:Init')
        # for debugging purposes: log available methods from Parent object
        # for method_name in dir(Parent):
        #     log('trace', 'Method Parent.%s' % method_name)

        global bot
        #   Load settings
        config = load_config()
        logger.log_level = log_levels[config['core.log_level'].lower()]
        bot = Bot(Parent, config)
    except:
        log('error', traceback.format_exc())


def Execute(data):
    if data.Message:
        try:
            log_call('JBetSystem:Execute', data=data.Message)
            global bot
            bot.process(data)
        except:
            log('error', traceback.format_exc())


def Tick():
    try:
        # log_call('JBetSystem:Tick', trace=True)
        global bot
        # bot.tick()
    except:
        log('error', traceback.format_exc())


def Parse(parse_string, user_id, username, target_id, target_name, message):
    log_call('JBetSystem:Parse', parse_string=parse_string, user_id=user_id, username=username, target_id=target_id, target_name=target_name, message=message)


def ReloadSettings(jsondata):
    try:
        log_call('JBetSystem:ReloadSettings')
        global bot
        bot.config = load_config(jsondata)
        save_config(bot.config)
    except:
        log('error', traceback.format_exc())


def Unload():
    try:
        log_call('JBetSystem:Unload')
        global bot
        # save_config(bot.config)
    except:
        log('error', traceback.format_exc())


def ScriptToggled(state):
    try:
        log_call('JBetSystem:ScriptToggled')
    except:
        log('error', traceback.format_exc())


# ---------------------------
#   Custom functions for ui
# ---------------------------

def RestoreDefaultSettings():
    try:
        log_call('JBetSystem:RestoreDefaultSettings')
        global bot
        bot.config = default_config()
        save_config(bot.config)
    except Exception as e:
        log('error', repr(e))
