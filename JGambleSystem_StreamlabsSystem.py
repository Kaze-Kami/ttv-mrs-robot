# append lib to search path
import sys
import os

sys.path.append(os.path.dirname(__file__))

import clr
import traceback
import ctypes

from lib import info
from lib import global_variables
from lib import logger

from lib.logger import log_call, log, log_levels, make_log_file
from lib.config import load_config, save_config, save_whitelist, save_jackpot
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
        # set up log file
        make_log_file()
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
    try:
        if data.Message and not data.IsRawData():
            log_call('JBetSystem:Execute', data=data.Message)
            global bot
            bot.process(data)
    except:
        log('error', traceback.format_exc())


def Tick():
    try:
        # log_call('JBetSystem:Tick', trace=True)
        global bot
        bot.tick()
    except:
        log('error', traceback.format_exc())


def Parse(parse_string, user_id, username, target_id, target_name, message):
    try:
        log_call('JBetSystem:Parse', parse_string=parse_string, user_id=user_id, username=username, target_id=target_id,
                 target_name=target_name, message=message)
    except:
        log('error', traceback.format_exc())


def ReloadSettings(jsondata):
    try:
        log_call('JBetSystem:ReloadSettings')
        global bot
        config = load_config(jsondata)
        logger.log_level = log_levels[config['core.log_level'].lower()]
        bot.config = config
        save_config(config)
    except:
        log('error', traceback.format_exc())


def Unload():
    try:
        log_call('JBetSystem:Unload')
        global bot
        bot.shutdown()
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
        ret = ctypes.windll.user32.MessageBoxW(0, u"You are about to reset the settings, "
                                                  "are you sure you want to continue?"
                                                  "This will not clear the whitelist or jackpot file",
                                               u"Reset settings file?", 4)
        if ret == 6:  # yes is 6
            global bot
            bot.config = load_config(default=True)
            save_config(bot.config)
            ret = ctypes.windll.user32.MessageBoxW(0, u"Successfully restored to default values",
                                                   u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def ClearWhitelist():
    try:
        log_call('JBetSystem:ClearWhitelist')
        ret = ctypes.windll.user32.MessageBoxW(0, u"You are about to clear the whitelist, "
                                                  "are you sure you want to continue?",
                                               u"Clear whitelist?", 4)
        if ret == 6:  # yes is 6
            global bot
            bot.config['disclaimer.whitelist'] = []
            save_whitelist(bot.config)
            ret = ctypes.windll.user32.MessageBoxW(0, u"Successfully cleared the whitelist",
                                                   u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def ClearJackpot():
    try:
        log_call('JBetSystem:ClearJackpot')
        ret = ctypes.windll.user32.MessageBoxW(0, u"You are about to clear the jackpot, "
                                                  "are you sure you want to continue?",
                                               u"Clear jackpot?", 4)
        if ret == 6:  # yes is 6
            global bot
            bot.config['jackpot.entries'] = []
            bot.config['jackpot.sum'] = 0
            save_jackpot(bot.config)
            ret = ctypes.windll.user32.MessageBoxW(0, u"Successfully cleared the jackpot",
                                                   u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def OpenReadme():
    try:
        log_call('JBetSystem:OpenReadme')
        os.startfile(global_variables.readme_path)
    except:
        log('error', traceback.format_exc())
