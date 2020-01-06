"""
Created by Joscha Vack on 1/5/2020.
"""

import codecs
import json
from os import path

from lib import info


class Configuration(object):
    def __init__(self, settings_file=None):
        loaded = False
        cfg = None
        try:
            with codecs.open(settings_file, encoding="utf-8-sig", mode="r") as f:
                cfg = json.load(f, encoding="utf-8")
                loaded = True
        except Exception as e:
            info.parent.Log(info.script_name, 'Failed to load settings from %s (%s)' % (settings_file, repr(e)))
            # create default config
            self.prefix = '!lucky'
            self.raw_help_command = '{prefix}?'
            self.raw_malformed_request_response = 'I did not get that. Type \'{0}\' for help and try again.'
            self.raw_help_message = 'Type: \'{gamble}\' to gamble, \'{guess}\' to guess, \'{0} command\' to view more information about a command.'
            self.raw_help_texts = {
                'gamble': 'Use \'{command} [amount]\' to gamble. Chances of winning are {chance}',
                'guess': 'Use \'{command} [amount] [guess]\' to guess. Guess has to be between 0 and {max}'
            }
            self.permission = 'everyone'
            self.permission_info = ''
            self.time_format_hours = '%d hours'
            self.time_format_hour = 'one hour'
            self.time_format_minutes = '%d minutes'
            self.time_format_minute = 'one minute'
            self.time_format_seconds = '%d seconds'
            self.time_format_second = 'one second'
            self.time_format_separator = 'and'
            self.raw_not_permitted_message = 'You are not permitted to use this command {user}.'
            self.require_ok = True
            self.whitelist = []
            self.disclaimer_keyword = "disclaimer"
            self.disclaimer_acknowledge_keyword = "acknowledge"
            self.raw_disclaimer = 'Gambling can be addictive. Play responsibly. Underage gambling is an offence. Type \'{acknowledge}\' to acknowledge this disclaimer.'
            self.raw_not_ok_message = 'You need to acknowledge the gambling disclaimer before gambling, {user}. Type \'{disclaimer}\' to display it.'
            self.raw_disclaimer_acknowledged_message = 'You can gamble now {user}!'
            self.raw_out_of_currency_message = 'You don\'t have enough {currency} to do this!'
            self.gamble_keyword = 'gamble'
            self.guess_keyword = 'guess'
            self.win_multipliers = {
                'gamble': 2,
                'guess': 5
            }
            self.raw_win_messages = {
                'gamble': '{user} won {winnings} {currency} and has {total} {currency}!',
                'guess': '{user} won {winnings} {currency} and has {total} {currency}!'
            }
            self.raw_loss_messages = {
                'gamble': '{user} lost {loss} {currency} and has {total} {currency}!',
                'guess': '{user} lost {loss} {currency} and has {total} {currency}!'
            }
            self.permissions = {
                'gamble': 'everyone',
                'guess': 'everyone'
            }
            self.permissions_info = {
                'gamble': '',
                'guess': ''
            }
            self.cooldowns = {
                'gamble': 250,
                'guess': 250
            }
            self.raw_cooldown_messages = {
                'gamble': 'You can not gamble again already {user}. You need to wait {cooldown}',
                'guess': 'You can not guess again already {user}. You need to wait {cooldown}'
            }
            self.gamble_chance = 1
            self.guess_max_val = 100
            self.save(settings_file)

        if loaded:
            # simplify cfg
            permissions = {
                'gamble': cfg['gamble_permission'],
                'guess': cfg['guess_permission']
            }
            cfg['permissions'] = permissions
            del cfg['gamble_permission']
            del cfg['guess_permission']

            permissions_info = {
                'gamble': cfg['gamble_info'],
                'guess': cfg['guess_info']
            }
            cfg['permissions_info'] = permissions_info
            del cfg['gamble_info']
            del cfg['guess_info']

            cooldowns = {
                'gamble': int(cfg['gamble_cooldown']),
                'guess': int(cfg['guess_cooldown'])
            }
            cfg['cooldowns'] = cooldowns
            del cfg['gamble_cooldown']
            del cfg['guess_cooldown']

            raw_cooldown_messages = {
                'gamble': str(cfg['raw_gamble_cooldown_message']),
                'guess': str(cfg['raw_guess_cooldown_message'])
            }
            cfg['raw_cooldown_messages'] = raw_cooldown_messages
            del cfg['raw_gamble_cooldown_message']
            del cfg['raw_guess_cooldown_message']

            raw_help_texts = {
                'gamble': str(cfg['gamble_help']),
                'guess': str(cfg['guess_help'])
            }
            cfg['raw_help_texts'] = raw_help_texts
            del cfg['gamble_help']
            del cfg['guess_help']

            raw_win_messages = {
                'gamble': str(cfg['raw_gamble_win_message']),
                'guess': str(cfg['raw_guess_win_message'])
            }
            cfg['raw_win_messages'] = raw_win_messages
            del cfg['raw_gamble_win_message']
            del cfg['raw_guess_win_message']

            raw_loss_messages = {
                'gamble': str(cfg['raw_gamble_loss_message']),
                'guess': str(cfg['raw_guess_loss_message'])
            }
            cfg['raw_loss_messages'] = raw_loss_messages
            del cfg['raw_gamble_loss_message']
            del cfg['raw_guess_loss_message']

            win_multipliers = {
                'gamble': float(cfg['gamble_win_multiplier']),
                'guess': float(cfg['guess_win_multiplier'])
            }
            cfg['win_multipliers'] = win_multipliers
            del cfg['gamble_win_multiplier']
            del cfg['guess_win_multiplier']

            # ensure strings where we need them
            cfg['raw_help_command'] = str(cfg['raw_help_command'])
            cfg['raw_malformed_request_response'] = str(cfg['raw_malformed_request_response'])
            cfg['raw_help_message'] = str(cfg['raw_help_message'])
            cfg['time_format_hours'] = str(cfg['time_format_hours'])
            cfg['time_format_hour'] = str(cfg['time_format_hour'])
            cfg['time_format_minutes'] = str(cfg['time_format_minutes'])
            cfg['time_format_minute'] = str(cfg['time_format_minute'])
            cfg['time_format_seconds'] = str(cfg['time_format_seconds'])
            cfg['time_format_second'] = str(cfg['time_format_second'])
            cfg['time_format_separator'] = str(cfg['time_format_separator'])
            cfg['raw_disclaimer'] = str(cfg['raw_disclaimer'])
            cfg['raw_not_ok_message'] = str(cfg['raw_not_ok_message'])
            cfg['raw_disclaimer_acknowledged_message'] = str(cfg['raw_disclaimer_acknowledged_message'])
            cfg['raw_out_of_currency_message'] = str(cfg['raw_out_of_currency_message'])

            # ensure number where we need numbers
            cfg['gamble_chance'] = float(cfg['gamble_chance'])
            cfg['guess_max_val'] = int(cfg['guess_max_val'])

            # ensure bool where we need bools
            cfg['require_ok'] = bool(cfg['require_ok'])

            self.__dict__ = cfg

        info.parent.Log(info.script_name, 'Config loaded:')
        info.parent.Log(info.script_name, str(self))

    def reload(self, jsondata):
        cfg = json.loads(jsondata, encoding="utf-8")
        permissions = {
            'gamble': cfg['gamble_permission'],
            'guess': cfg['guess_permission']
        }
        cfg['permissions'] = permissions
        del cfg['gamble_permission']
        del cfg['guess_permission']

        permissions_info = {
            'gamble': cfg['gamble_info'],
            'guess': cfg['guess_info']
        }
        cfg['permissions_info'] = permissions_info
        del cfg['gamble_info']
        del cfg['guess_info']

        cooldowns = {
            'gamble': int(cfg['gamble_cooldown']),
            'guess': int(cfg['guess_cooldown'])
        }
        cfg['cooldowns'] = cooldowns
        del cfg['gamble_cooldown']
        del cfg['guess_cooldown']

        raw_cooldown_messages = {
            'gamble': str(cfg['raw_gamble_cooldown_message']),
            'guess': str(cfg['raw_guess_cooldown_message'])
        }
        cfg['raw_cooldown_messages'] = raw_cooldown_messages
        del cfg['raw_gamble_cooldown_message']
        del cfg['raw_guess_cooldown_message']

        raw_help_texts = {
            'gamble': str(cfg['gamble_help']),
            'guess': str(cfg['guess_help'])
        }
        cfg['raw_help'] = raw_help_texts
        del cfg['gamble_help']
        del cfg['guess_help']

        raw_win_messages = {
            'gamble': str(cfg['raw_gamble_win_message']),
            'guess': str(cfg['raw_guess_win_message'])
        }
        cfg['raw_win_messages'] = raw_win_messages
        del cfg['raw_gamble_win_message']
        del cfg['raw_guess_win_message']

        loss_win_messages = {
            'gamble': str(cfg['loss_gamble_win_message']),
            'guess': str(cfg['loss_guess_win_message'])
        }
        cfg['loss_win_messages'] = loss_win_messages
        del cfg['loss_gamble_win_message']
        del cfg['loss_guess_win_message']

        win_multipliers = {
            'gamble': float(cfg['gamble_win_multiplier']),
            'guess': float(cfg['guess_win_multiplier'])
        }
        cfg['win_multipliers'] = win_multipliers
        del cfg['gamble_win_multiplier']
        del cfg['guess_win_multiplier']

        # ensure strings where we need them
        cfg['raw_help_command'] = str(cfg['raw_help_command'])
        cfg['raw_malformed_request_response'] = str(cfg['raw_malformed_request_response'])
        cfg['raw_help_message'] = str(cfg['raw_help_message'])
        cfg['time_format_hours'] = str(cfg['time_format_hours'])
        cfg['time_format_hour'] = str(cfg['time_format_hour'])
        cfg['time_format_minutes'] = str(cfg['time_format_minutes'])
        cfg['time_format_minute'] = str(cfg['time_format_minute'])
        cfg['time_format_seconds'] = str(cfg['time_format_seconds'])
        cfg['time_format_second'] = str(cfg['time_format_second'])
        cfg['time_format_separator'] = str(cfg['time_format_separator'])
        cfg['raw_disclaimer'] = str(cfg['raw_disclaimer'])
        cfg['raw_not_ok_message'] = str(cfg['raw_not_ok_message'])
        cfg['raw_disclaimer_acknowledged_message'] = str(cfg['raw_disclaimer_acknowledged_message'])
        cfg['raw_out_of_currency_message'] = str(cfg['raw_out_of_currency_message'])

        # ensure number where we need numbers
        cfg['gamble_chance'] = float(cfg['gamble_chance'])
        cfg['guess_max_val'] = int(cfg['gamble_chance'])

        # ensure bool where we need bools
        cfg['require_ok'] = bool(cfg['require_ok'])

        self.__dict__ = cfg
        info.parent.Log(info.script_name, 'Config reloaded:')
        info.parent.Log(info.script_name, str(self))

    def save(self, settings_file):
        cfg = dict(self.__dict__)

        del cfg['permissions']
        cfg['gamble_permission'] = self.permissions['gamble']
        cfg['guess_permission'] = self.permissions['guess']

        del cfg['permissions_info']
        cfg['gamble_info'] = self.permissions_info['gamble']
        cfg['guess_info'] = self.permissions_info['guess']

        del cfg['cooldowns']
        cfg['gamble_cooldown'] = self.cooldowns['gamble']
        cfg['guess_cooldown'] = self.cooldowns['guess']

        del cfg['raw_cooldown_messages']
        cfg['raw_gamble_cooldown_message'] = self.raw_cooldown_messages['gamble']
        cfg['raw_guess_cooldown_message'] = self.raw_cooldown_messages['guess']

        del cfg['raw_help_texts']
        cfg['gamble_help'] = self.raw_help_texts['gamble']
        cfg['guess_help'] = self.raw_help_texts['guess']

        del cfg['raw_win_messages']
        cfg['raw_gamble_win_message'] = self.raw_win_messages['gamble']
        cfg['raw_guess_win_message'] = self.raw_win_messages['guess']

        del cfg['raw_loss_messages']
        cfg['raw_gamble_loss_message'] = self.raw_loss_messages['gamble']
        cfg['raw_guess_loss_message'] = self.raw_loss_messages['guess']

        del cfg['win_multipliers']
        cfg['gamble_win_multiplier'] = self.win_multipliers['gamble']
        cfg['guess_win_multiplier'] = self.win_multipliers['guess']

        try:
            with codecs.open(settings_file, encoding="utf-8-sig", mode="w+") as f:
                json.dump(cfg, f, encoding="utf-8", default='')
            with codecs.open(settings_file.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(cfg, encoding='utf-8')))
            info.parent.Log(info.script_name, "Config saved to file '%s'" % settings_file)
        except Exception as e:
            info.parent.Log(info.script_name, "Failed to save settings to file '%s'. (%s)" % (settings_file, repr(e)))

        info.parent.Log(info.script_name, 'Config saved:')
        info.parent.Log(info.script_name, str(self))

    def __str__(self):
        return '{\n' + ',\n'.join('\t%s: %s' % (k, v) for k, v in self.__dict__.items()) + '\n}'

    def prefix_command(self, command):
        return '%s %s' % (self.prefix, command)

    def format_time(self, time):
        seconds = time % 60
        time //= 60
        minutes = time % 60
        time //= 60
        out = ''
        if time:
            if 1 == time:
                out = self.time_format_hours
            else:
                out = self.time_format_hours % time
        if minutes:
            if out:
                out += ', '
            if 1 == minutes:
                out += self.time_format_minute
            else:
                out += self.time_format_minutes % minutes
        if seconds:
            if out:
                out += ' ' + self.time_format_separator + ' '
            if 1 == seconds:
                out += self.time_format_seconds
            else:
                out += self.time_format_minutes % seconds

        return out

    def format_win_message(self, kind, user, winnings, total):
        return self.raw_win_messages[kind].replace('{user}', '@' + user).replace('{winnings}', str(winnings)).replace('{total}', str(total)).replace('{currency}', info.parent.GetCurrencyName())

    def format_loss_message(self, kind, user, loss, total):
        return self.raw_loss_messages[kind].replace('{user}', '@' + user).replace('{loss}', str(loss)).replace('{total}', str(total)).replace('{currency}', info.parent.GetCurrencyName())

    def format_cooldown_message(self, kind, user, cooldown):
        return self.raw_cooldown_messages[kind].replace('{user}', '@' + user).replace('{cooldown}', self.format_time(cooldown))

    def format_not_permitted_message(self, user):
        return self.raw_not_permitted_message.replace('{user}', '@' + user)

    def format_not_ok_message(self, user):
        return self.raw_not_ok_message.replace('{disclaimer}', self.prefix_command(self.disclaimer_keyword)).replace('{user}', '@' + user)

    def format_acknowledged_message(self, user):
        return self.raw_disclaimer_acknowledged_message.replace('{user}', '@' + user)

    @property
    def help_command(self):
        return self.raw_help_command.replace('{prefix}', self.prefix)

    @property
    def malformed_request_response(self):
        return self.raw_malformed_request_response % self.help_command

    @property
    def help_message(self):
        return self.raw_help_message.replace('{gamble}', self.gamble_keyword).replace('{guess}', self.guess_keyword).replace('{0}', self.help_command)

    @property
    def disclaimer(self):
        return self.raw_disclaimer.replace('{acknowledge}', self.prefix_command(self.disclaimer_acknowledge_keyword))

    @property
    def out_of_currency_message(self):
        return self.raw_out_of_currency_message.replace('{currency}', info.parent.GetCurrencyName())

    @property
    def gamble_help(self):
        return self.raw_help_texts['gamble'].replace('{command}', self.prefix_command(self.gamble_keyword)).replace('{chance}', '%d%%' % self.gamble_chance)

    @property
    def guess_help(self):
        return self.raw_help_texts['guess'].replace('{command}', self.prefix_command(self.guess_keyword)).replace('{max}', str(self.guess_max_val))
