"""
Created by Joscha Vack on 1/6/2020.
"""

import json
import collections
import os

from lib import global_variables
from lib.logger import log_call, log
from lib.file_io import write_json, read_json


def _to_nested_dict(raw_data):
    log_call('config:_parse_json')
    parsed_data = collections.defaultdict(lambda: collections.defaultdict(collections.defaultdict))
    for k in raw_data:
        path = k.split('.')
        e = parsed_data
        for p in path[:-1]:
            e = e[p]
        e[path[-1]] = raw_data[k]
    return _recursive_to_dict(parsed_data)


def _default_config_data():
    log_call('config:_default_config_data')
    """
        Yea this is hardcoded but what'ya gonna do...?
        :return: the default config
        """
    data = {
        'core.log_level': 'info',
        'core.prefix.enable': True,
        'core.prefix.text': 'MrsRobot',
        'core.help.keyword': 'help',
        'core.permission.value': 'everyone',
        'core.permission.info': '',
        'core.all_keyword': 'all',
        'core.text.help': 'Available commands: {gamble.command}, {guess.command}, {d20.command}, {jackpot.command}. For more information on a command type {core.help.command} [keyword]. To view the disclaimer type {disclaimer.command}.',
        'core.text.no_permission': 'You have no permission to use the commands, {user}.',
        'core.text.no_command_permission': 'You have no permission to use the {keyword} command, {user}.',
        'core.text.command_disable': '{keyword} is currently disabled, {user}.',
        'core.text.malformed_command': 'I did not get that. Type {core.help.command} for help and try again.',
        'core.text.not_enough_currency': 'You don\'t have enough {currency} to do this, {user}.',
        'core.text.on_cooldown': '{keyword} is still on cooldown for {cooldown} seconds, {user}',
        'core.text.twitch_bug': 'Please close the whisper chat with the \'X\' and reopen it after replying to see new messages from me (that\'s a nice twitch but isn\'t it?).',

        # disclaimer settings
        'disclaimer.enable': True,
        'disclaimer.via_whisper': True,
        'disclaimer.keyword': 'disclaimer',
        'disclaimer.acknowledge_keyword': 'acknowledge',
        'disclaimer.text.via_whisper': 'You need to send this message via whisper, {user}',
        'disclaimer.text.disable': 'The disclaimer is currently disabled, {user}.',
        'disclaimer.text.disclaimer': 'Gambling can be addictive. Play responsibly. Underage gambling is an offence. Type {disclaimer.acknowledge_command} to acknowledge this disclaimer.',
        'disclaimer.text.acknowledged': 'You can {gamble.keyword} and {guess.keyword} now {user}.',
        'disclaimer.text.not_acknowledged': 'I\'m sorry {user} but you need to accept the disclaimer first to {gamble.keyword} or {guess.keyword}. Type {disclaimer.command} to display it.',

        # jackpot settings
        'jackpot.enable': True,
        'jackpot.keyword': 'jackpot',
        'jackpot.min_entry': 500,
        'jackpot.number': 100,
        'jackpot.percentage': 100,
        'jackpot.decay.enable': True,
        'jackpot.decay.seconds': 20,
        'jackpot.decay.hours': 0,
        'jackpot.decay.minutes': 0,
        'jackpot.text.content': 'The jackpot currently contains {jackpot.sum} {currency}, {user}',
        'jackpot.text.win': '{user} rolled {roll} and won the jackpot ({jackpot.sum} {currency})! He has {total} {currency} now.',
        'jackpot.text.help': 'Type {jackpot.command} to view the jackpot. Jackpot can be won by rolling {jackpot.number} while gambling with at least {jackpot.min_entry} {currency}.',

        # gamble settings
        'gamble.enable': True,
        'gamble.keyword': 'gamble',
        'gamble.permission.value': 'everyone',
        'gamble.permission.info': '',
        'gamble.cooldown': 10,
        'gamble.text.win': 'Roll was {roll}. {user} wins {payout} {currency} and has {total} {currency} now.',
        'gamble.text.lose': 'Roll was {roll}. {user} looses {loss} {currency} and has {total} {currency} now.',
        'gamble.text.help': 'Type {gamble.command} [amount] to gamble. You need to gamble at least {gamble.min_entry} {currency} and at least {jackpot.min_entry} {currency} to be eligible to win the jackpot. Chances to win are {gamble.chance}%',
        'gamble.text.entry_to_low': 'You need to gamble at least {gamble.min_entry} {currency}, {user}',
        'gamble.min_entry': 200,
        'gamble.chance': 25,
        'gamble.win_multiplier': 2,
        'gamble.double.enable': True,
        'gamble.double.chance': 10,
        'gamble.triple.enable': True,
        'gamble.triple.chance': 5,

        # guess settings
        'guess.enable': True,
        'guess.keyword': 'guess',
        'guess.permission.value': 'everyone',
        'guess.permission.info': '',
        'guess.cooldown': 10,
        'guess.text.win': '{user}\'s guess ({guess}) was right! He wins {payout} {currency} and has {total} {currency} now.',
        'guess.text.lose': '{user}\'s guess ({guess}) was wrong, roll was {roll}! He looses {loss} {currency} and has {total} {currency} now.',
        'guess.text.help': 'Type {guess.command} [guess] [amount] to guess. [guess] must be between 1 and {guess.max_val}',
        'guess.text.not_in_range': '{guess} is not a valid guess. It must be between 1 and {guess.max_val}, {user}',
        'guess.max_val': 20,
        'guess.win_multiplier': 5,

        # d20 settings
        'd20.enable': True,
        'd20.keyword': 'd20',
        'd20.permission.value': 'everyone',
        'd20.permission.info': '',
        'd20.cooldown': 10,
        'd20.text.results': 'd20 TEXT1;d20 TEXT2;20 TEXT3;d20 TEXT4;d20 TEXT5;d20 TEXT6',
        'd20.text.help': 'Type {d20.command} to roll the d20.',
    }
    return data


def load_config(jsondata=None, default=False):
    log_call('config:load_config', jsondata='Yes' if jsondata else 'No')

    # read whitelist
    if os.path.exists(global_variables.whitelist_file):
        try:
            raw_data = read_json(global_variables.whitelist_file)
        except Exception as e:
            log('error', 'Can not load whitelist file from %s: %s' % (global_variables.whitelist_file, repr(e)))
            raw_data = {'disclaimer.whitelist': []}
    else:
        raw_data = {'disclaimer.whitelist': []}
        log('warn', 'Whitelist file not found, creating new one')
        try:
            write_json(global_variables.whitelist_file, {'disclaimer.whitelist': []})
        except Exception as e:
            log('error', 'Failed to save whitelist to file %s: %s' % (global_variables.whitelist_file, repr(e)))

    # read jackpot
    if os.path.exists(global_variables.jackpot_file):
        try:
            jackpot_info = read_json(global_variables.jackpot_file)
            raw_data['jackpot.entries'] = [[float(v), int(t)] for v, t in zip(jackpot_info['jackpot.values'],
                                                                              jackpot_info['jackpot.times'])]
            total = 0
            for v, t in raw_data['jackpot.entries']:
                total += v
            raw_data['jackpot.sum'] = int(total)
        except Exception as e:
            log('error', 'Can not load jackpot info file from %s: %s' % (global_variables.jackpot_file, repr(e)))
            raw_data['jackpot.entries'] = []
            raw_data['jackpot.sum'] = 0
    else:
        raw_data['jackpot.entries'] = []
        raw_data['jackpot.sum'] = 0
        log('warn', 'Jackpot file not found, creating new one')
        try:
            write_json(global_variables.jackpot_file, {'jackpot.values': [], 'jackpot.times': []})
        except Exception as e:
            log('error', 'Failed to save jackpot to file %s: %s' % (global_variables.jackpot_file, repr(e)))

    # read config
    if jsondata:
        raw_data.update(json.loads(jsondata, encoding="utf-8"))
    elif default:
        raw_data.update(_default_config_data())
    elif os.path.exists(global_variables.config_file):
        try:
            raw_data.update(read_json(global_variables.config_file))
        except Exception as e:
            log('error', 'Can not load config file from %s: %s, falling back to default config' % (global_variables.config_file, repr(e)))
            raw_data.update(_default_config_data())
    else:
        raw_data.update(_default_config_data())
        log('warn', 'Config file not found, creating new one')
        try:
            write_json(global_variables.config_file, _default_config_data())
        except Exception as e:
            log('error', 'Failed to save config file to %s: %s' % (global_variables.config_file, repr(e)))
            raw_data.update(_default_config_data())

    raw_data['jackpot.decay.total'] = int(int(raw_data['jackpot.decay.seconds'])
                                          + int(raw_data['jackpot.decay.minutes']) * 60
                                          + int(raw_data['jackpot.decay.hours']) * 24 * 60)

    # append extra
    raw_data['core.prefix.value'] = ('!' + raw_data['core.prefix.text'] + ' ') if bool(raw_data['core.prefix.enable']) else '!'
    raw_data['core.help.command'] = '{core.prefix.value}{core.help.keyword}'
    raw_data['disclaimer.acknowledge_command'] = '{core.prefix.value}{disclaimer.acknowledge_keyword}'
    raw_data['disclaimer.command'] = '{core.prefix.value}{disclaimer.keyword}'
    raw_data['jackpot.command'] = '{core.prefix.value}{jackpot.keyword}'
    raw_data['gamble.command'] = '{core.prefix.value}{gamble.keyword}'
    raw_data['guess.command'] = '{core.prefix.value}{guess.keyword}'
    raw_data['d20.command'] = '{core.prefix.value}{d20.keyword}'

    parsed_data = _to_nested_dict(raw_data)
    config = Config(parsed_data)
    log('debug', 'Config:\n' + _format_dict(config.data, ind='  ', ind_inc='  '))
    return config


def save_config(config):
    log_call('config:save_config')
    data = _flatten_dict(config.data)

    # save and remove whitelist
    del data['disclaimer.whitelist']

    # save and remove jackpot
    del data['jackpot.entries']
    del data['jackpot.sum']
    del data['jackpot.decay.total']

    # remove extra
    del data['core.prefix.value']
    del data['core.help.command']
    del data['disclaimer.acknowledge_command']
    del data['disclaimer.command']
    del data['jackpot.command']
    del data['gamble.command']
    del data['guess.command']
    del data['d20.command']

    try:
        # save config
        write_json(global_variables.config_file, data, js=True)
        return True
    except Exception as e:
        log('error', 'Failed to save config: %s' % repr(e))
        return False


def save_whitelist(config):
    log_call('config:save_whitelist')
    whitelist = config['disclaimer.whitelist']
    try:
        write_json(global_variables.whitelist_file, {'disclaimer.whitelist': whitelist})
    except Exception as e:
        log('error', 'Failed to save whitelist to file %s: %s' % (global_variables.whitelist_file, repr(e)))


def save_jackpot(config):
    log_call('config:save_jackpot')
    jackpot_data = {
        'jackpot.values': [],
        'jackpot.times': []
    }
    for e in config['jackpot.entries']:
        jackpot_data['jackpot.values'].append(e[0])
        jackpot_data['jackpot.times'].append(e[1])
    try:
        write_json(global_variables.jackpot_file, jackpot_data)
    except Exception as e:
        log('error', 'Failed to save jackpot to file %s: %s' % (global_variables.jackpot_file, repr(e)))


def _flatten_dict(d, parent_key='', sep='.'):
    items = {}
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.update(_flatten_dict(v, new_key, sep))
        else:
            items[new_key] = v
    return items


def _recursive_to_dict(d):
    for k, v in d.items():
        if isinstance(v, collections.MutableMapping):
            d[k] = _recursive_to_dict(v)
    return dict(d)


def _format_dict(d, ind='', ind_inc=''):
    return '\n'.join(['%s%s: %s' % (
        ind, k, str(v) if '\n' not in str(v) else ('\n' + ind + ind_inc).join(('\n' + v).replace('\r', '').split('\n')))
                      if not isinstance(v, collections.MutableMapping)
                      else ind + k + '\n' + _format_dict(v, ind + ind_inc, ind_inc) for k, v in d.items()])


class Config(object):
    def __init__(self, data_dict):
        log_call('Config.__init__')
        self._data_dict = data_dict

    def __getitem__(self, args):
        log_call('Config.__getitem__', args=args)
        try:
            key, fmt = args
        except:
            key = args
            fmt = None
        """
        returns item of arbitrary depth from the data dict
        eg. a.b.c -> self._data[a][b][c]
        :param key: path-like key separated by '.'
        :return: data dict entry for the key
        """
        indices = key.split('.')
        val = self._data_dict
        for i in indices:
            val = val[i]
        return fmt(val) if fmt else val

    def __setitem__(self, key, value):
        log_call('Config.__setitem__', key=key, value=value)
        indices = key.split('.')
        val = self._data_dict
        for i in indices[:-1]:
            val = val[i]
        val[indices[-1]] = value

    def __contains__(self, key):
        log_call('Config.__contains__', key=key)
        indices = key.split('.')
        val = self._data_dict
        for i in indices:
            if i in val:
                val = val[i]
            else:
                return False
        return True

    @property
    def data(self):
        log_call('Config.data.getter')
        return self._data_dict
