# append lib to search path
import sys
import os

sys.path.append(os.path.dirname(__file__))

import clr
import traceback
import ctypes

from lib import info, global_variables, logger

from lib.bot import Bot
from lib.logger import log_call, log, log_levels, make_log_file
from lib.config import load_config, save_config, save_whitelist, save_jackpot
from lib.file_io import backup_file, restore_file, exists_backup

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

        # create resource folder if necessary
        if not os.path.exists(global_variables.resource_dir):
            os.mkdir(global_variables.resource_dir)

        # set up log file
        make_log_file()
        log_call('JBetSystem:Init')

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
        ret = ctypes.windll.user32.MessageBoxW(0, u"You are about to reset the settings. "
                                                  u"This will not clear the whitelist or jackpot file. "
                                                  u"Are you sure you want to continue?",
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
        ret = ctypes.windll.user32.MessageBoxW(0, u"You are about to clear the whitelist. "
                                                  u"Are you sure you want to continue?",
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
        ret = ctypes.windll.user32.MessageBoxW(0, u"You are about to clear the jackpot. "
                                                  u"Are you sure you want to continue?",
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
        os.startfile(global_variables.readme_file)
    except:
        log('error', traceback.format_exc())


def BackupConfig():
    try:
        log_call('JBetSystem:BackupConfig')
        ret = ctypes.windll.user32.MessageBoxW(0,
                                               u"You are about to backup the config. "
                                               u"This will overwrite any existing backup. "
                                               u"Are you sure you want to continue?",
                                               u"Backup config?", 4)
        if ret == 6:  # yes is 6
            backup_file(global_variables.config_file)
            ret = ctypes.windll.user32.MessageBoxW(0, u"Backup successful", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def BackupWhitelist():
    try:
        log_call('JBetSystem:BackupWhitelist')
        ret = ctypes.windll.user32.MessageBoxW(0,
                                               u"You are about to backup the whitelist. "
                                               u"This will overwrite any existing backup. "
                                               u"Are you sure you want to continue?",
                                               u"Backup whitelist?", 4)
        if ret == 6:  # yes is 6
            backup_file(global_variables.whitelist_file)
            ret = ctypes.windll.user32.MessageBoxW(0, u"Backup successful", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def BackupJackpot():
    try:
        log_call('JBetSystem:BackupJackpot')
        ret = ctypes.windll.user32.MessageBoxW(0,
                                               u"You are about to backup the jackpot. "
                                               u"This will overwrite any existing backup. "
                                               u"Are you sure you want to continue?",
                                               u"Backup jackpot?", 4)
        if ret == 6:  # yes is 6
            backup_file(global_variables.jackpot_file)
            ret = ctypes.windll.user32.MessageBoxW(0, u"Backup successful.", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def BackupAll():
    try:
        log_call('JBetSystem:Backup all')
        ret = ctypes.windll.user32.MessageBoxW(0,
                                               u"You are about to backup the config, whitelist and jackpot. "
                                               u"This will overwrite all existing backups. "
                                               u"Are you sure you want to continue?",
                                               u"Backup all?", 4)
        if ret == 6:  # yes is 6
            backup_file(global_variables.config_file)
            backup_file(global_variables.whitelist_file)
            backup_file(global_variables.jackpot_file)
            ret = ctypes.windll.user32.MessageBoxW(0, u"Backup successful.", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def RestoreConfig():
    try:
        log_call('JBetSystem:RestoreConfig')
        if exists_backup(global_variables.config_file):
            ret = ctypes.windll.user32.MessageBoxW(0,
                                                   u"You are about to restore the config. "
                                                   u"This will overwrite the current config. "
                                                   u"Are you sure you want to continue?",
                                                   u"Restore config?", 4)
            if ret == 6:  # yes is 6
                restore_file(global_variables.config_file)
                ret = ctypes.windll.user32.MessageBoxW(0, u"Restore successful. please reload the script.", u"Ok!", 0)
        else:
            ret = ctypes.windll.user32.MessageBoxW(0, u"No config backup found", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def RestoreWhitelist():
    try:
        log_call('JBetSystem:RestoreWhitelist')
        if exists_backup(global_variables.whitelist_file):
            ret = ctypes.windll.user32.MessageBoxW(0,
                                                   u"You are about to restore the whitelist. "
                                                   u"This will overwrite the current whitelist. "
                                                   u"Are you sure you want to continue?",
                                                   u"Restore whitelist?", 4)
            if ret == 6:  # yes is 6
                restore_file(global_variables.whitelist_file)
                ret = ctypes.windll.user32.MessageBoxW(0, u"Restore successful. please reload the script.", u"Ok!", 0)
        else:
            ret = ctypes.windll.user32.MessageBoxW(0, u"No whitelist backup found", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def RestoreJackpot():
    try:
        log_call('JBetSystem:RestoreJackpot')
        if exists_backup(global_variables.jackpot_file):
            ret = ctypes.windll.user32.MessageBoxW(0,
                                                   u"You are about to restore the jackpot. "
                                                   u"This will overwrite the current jackpot. "
                                                   u"Are you sure you want to continue?",
                                                   u"Restore jackpot?", 4)
            if ret == 6:  # yes is 6
                restore_file(global_variables.jackpot_file)
                ret = ctypes.windll.user32.MessageBoxW(0, u"Restore successful. please reload the script.", u"Ok!", 0)
        else:
            ret = ctypes.windll.user32.MessageBoxW(0, u"No jackpot backup found", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())


def RestoreAll():
    try:
        log_call('JBetSystem:RestoreAll')
        ret = ctypes.windll.user32.MessageBoxW(0,
                                               u"You are about to restore the config, whitelist and jackpot. "
                                               u"This will overwrite the current data. "
                                               u"Are you sure you want to continue?",
                                               u"Restore all?", 4)
        if ret == 6:  # yes is 6
            skip = ''
            if exists_backup(global_variables.config_file):
                restore_file(global_variables.config_file)
            else:
                skip += 'Config'
            if exists_backup(global_variables.whitelist_file):
                restore_file(global_variables.whitelist_file)
            else:
                if skip:
                    skip += ', '
                skip += 'Whitelist'
            if exists_backup(global_variables.jackpot_file):
                restore_file(global_variables.jackpot_file)
            else:
                if skip:
                    skip += 'and '
                skip += 'Jackpot'
            if skip:
                ret = ctypes.windll.user32.MessageBoxW(0, u"Restore finished. No backups found for %s. Please reload the script." % skip, u"Ok!", 0)
            else:
                ret = ctypes.windll.user32.MessageBoxW(0, u"Restore successful. please reload the script.", u"Ok!", 0)
    except:
        log('error', traceback.format_exc())