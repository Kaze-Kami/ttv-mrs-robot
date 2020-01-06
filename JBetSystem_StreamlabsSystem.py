# append lib to search path
import sys
import os

sys.path.append(os.path.dirname(__file__))

import clr
from lib import info
from lib.bot import Bot
from lib.configuration import Configuration

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
    info.parent = Parent
    global bot
    #   Create Settings Directory

    if not os.path.exists(info.resource_dir):
        Parent.Log(info.script_name, "Created resources dir")
        os.makedirs(info.resource_dir)

    #   Load settings
    config = Configuration(info.settings_path)
    bot = Bot(config, Parent)


def Execute(data):
    global bot
    bot.process(data)


def Tick():
    global bot
    bot.tick()


def Parse(parseString, userid, username, targetid, targetname, message):
    pass


def ReloadSettings(jsonData):
    global bot
    bot.config.reload(jsonData)
    bot.config.save(info.settings_path)


def Unload():
    pass


def ScriptToggled(state):
    pass


# ---------------------------
#   Custom functions for ui
# ---------------------------

def RestoreDefaultSettings():
    bot.settings = Configuration(info.settings_path)
