"""
Created by Joscha Vack on 1/6/2020.
"""

import codecs
import json
import collections

import global_variables
from logger import log_call, log
from lib import info


def _write_json(path, data, js=False):
    log_call('config:_write_json')
    with codecs.open(path, encoding="utf-8-sig", mode="w+") as f:
        json.dump(data, f, encoding="utf-8", default='')
    if js:
        with codecs.open(path.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
            f.write("var settings = {0};".format(json.dumps(data, encoding='utf-8')))


def _read_json(path):
    log_call('config:_read_json')
    with codecs.open(path, encoding="utf-8-sig", mode="r") as f:
        return json.load(f, encoding="utf-8")


def _parse_config(raw_data):
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
        'core.prefix': '!lucky',
        'core.permission.value': 'everyone',
        'core.permission.info': '',
        'core.all_keyword': 'all',
        'core.disclaimer.enable': True,
        'core.disclaimer.via_whisper': True,
        'core.disclaimer.keyword': 'disclaimer',
        'core.acknowledge.keyword': 'acknowledge',
        'core.text.help': 'Available commands: {gamble.command}, {guess.command}, {d20.command}. For more information on a command type {core.help.command} [keyword]. To view the disclaimer type {core.disclaimer.command}.',
        'core.text.no_permission': 'You have no permission to use the commands, {user}.',
        'core.text.no_command_permission': 'You have no permission to use the {keyword} command, {user}.',
        'core.text.command_disable': '{keyword} is currently disabled, {user}.',
        'core.text.malformed_command': 'I did not get that. Type {core.help.command} for help and try again.',
        'core.text.not_enough_currency': 'You don\'t have enough {currency} to do this, {user}.',
        'core.text.disclaimer_via_whisper': 'You need to send this message via whisper, {user}',
        'core.text.not_acknowledged': 'I\'m sorry {user} but you need to accept the disclaimer first to {gamble.keyword} or {guess.keyword}. Type {core.disclaimer.command} to display it.',
        'core.text.disclaimer_disable': 'The disclaimer is currently disabled, {user}.',
        'core.text.disclaimer': 'Gambling can be addictive. Play responsibly. Underage gambling is an offence. Type {core.acknowledge.command} to acknowledge this disclaimer.',
        'core.text.acknowledged': 'You can {gamble.keyword} and {guess.keyword} now {user}.',
        'core.text.twitch_bug': 'Please close the whisper chat with the \'X\' and reopen it after replying to see new messages from me (that\'s a nice twitch but isn\'t it?).',
        # gamble settings
        'gamble.enable': True,
        'gamble.keyword': 'gamble',
        'gamble.permission.value': 'everyone',
        'gamble.permission.info': '',
        'gamble.text.win': 'Roll was {roll}. {user} wins {payout} {currency} and has {total} {currency} now.',
        'gamble.text.lose': 'Roll was {roll}. {user} looses {loss} {currency} and has {total} {currency} now.',
        'gamble.text.help': 'Type {gamble.command} [amount] to gamble. Chances to win are {gamble.chance}%',
        'gamble.chance': 10,
        'gamble.win_multiplier': 1,
        # guess settings
        'guess.enable': True,
        'guess.keyword': 'guess',
        'guess.permission.value': 'everyone',
        'guess.permission.info': '',
        'guess.text.win': '{user}\'s guess ({guess}) was right! He wins {payout} and has {total} {currency} now.',
        'guess.text.lose': '{user}\'s guess ({guess}) was wrong, roll was {roll}! He looses {loss} and has {total} {currency} now.',
        'guess.text.help': 'Type {guess.command} [guess] [amount] to guess. [guess] must be between 0 and {guess.max_val}',
        'guess.max_val': 20,
        'guess.win_multiplier': 5,
        # d20 settings
        'd20.enable': False,
        'd20.keyword': 'd20',
        'd20.permission.value': 'everyone',
        'd20.permission.info': '',
        'd20.text.results': 'd20 TEXT1\nd20 TEXT2\nd20 TEXT3\nd20 TEXT4\nd20 TEXT5\nd20 TEXT6',
        'd20.text.help': 'Type {d20.command} to roll the d20.',
    }
    return data


def load_config(jsondata=None):
    log_call('config:load_config', jsondata=jsondata if jsondata else 'No')
    # read extra first so we can overwrite keys if needed
    try:
        raw_data = _read_json(global_variables.settings_extra_path)
    except Exception as e:
        log('error', 'Can not load config extra file from %s: %s' % (global_variables.settings_extra_path, repr(e)))
        raw_data = {}

    # read whitelist
    try:
        raw_data.update(_read_json(global_variables.whitelist_path))
    except Exception as e:
        log('error', 'Can not load whitelist file from %s: %s' % (global_variables.settings_extra_path, repr(e)))
        raw_data['core.acknowledge.whitelist'] = []

    # read jackpot
    try:
        jackpot_info = _read_json(global_variables.jackpot_info_path)
        raw_data['core.jackpot.entries'] = [(v, t) for v, t in zip(jackpot_info['core.jackpot.values'],
                                                                   jackpot_info['core.jackpot.times'])]
        raw_data['core.jackpot.sum'] = sum(jackpot_info['core.jackpot.values'])
    except Exception as e:
        log('error', 'Can not load jackpot info file from %s: %s' % (global_variables.settings_extra_path, repr(e)))
        raw_data['core.jackpot.sum'] = 0
        raw_data['core.jackpot.entries'] = []

    # read config
    if jsondata:
        raw_data.update(json.loads(jsondata, encoding="utf-8"))
    else:
        try:
            raw_data.update(_read_json(global_variables.settings_path))
        except Exception as e:
            log('error', 'Can not load config file from %s: %s, falling back to default config' % (
                global_variables.settings_path, repr(e)))
            raw_data.update(_default_config_data())

    parsed_data = _parse_config(raw_data)
    config = Config(parsed_data)
    log('debug', 'Config:\n' + _format_dict(config.data, ind='  ', ind_inc='  '))
    return config


def save_config(config):
    log_call('config:save_config')
    data = _flatten_dict(config.data)

    # save and remove whitelist
    del data['core.acknowledge.whitelist']

    # save and remove jackpot
    del config['core.jackpot.entries']
    del config['core.jackpot.sum']

    # remove extras
    try:
        extra = _read_json(global_variables.settings_extra_path)

        for k in extra:
            del data[k]
    except Exception as e:
        log('error', 'Can not load config extra file from %s: %s' % (global_variables.settings_extra_path, repr(e)))

    try:
        # save config
        _write_json(global_variables.settings_path, data, js=True)
    except Exception as e:
        log('error', 'Failed to save config: %s' % repr(e))


def default_config():
    log_call('config:default_config')
    try:
        raw_data = _read_json(global_variables.settings_extra_path)
    except Exception as e:
        log('error', 'Can not load config extra file from %s: %s' % (global_variables.settings_extra_path, repr(e)))
        raw_data = {}
    raw_data.update(_default_config_data())

    parsed_data = _parse_config(raw_data)
    config = Config(parsed_data)
    log('debug', 'Config:\n' + _format_dict(config.data, ind='  ', ind_inc='  '))
    return config


def save_whitelist(config):
    whitelist = config['core.acknowledge.whitelist']
    try:
        _write_json(global_variables.whitelist_path, {'core.acknowledge.whitelist': whitelist})
    except Exception as e:
        log('error', 'Failed to whitelist to file %s: %s' % (global_variables.whitelist_path, repr(e)))


def save_jackpot(config):
    jackpot_data = {
        'core.jackpot.values': [],
        'core.jackpot.times': []
    }
    for e in config['core.jackpot.entries']:
        jackpot_data['core.jackpot.values'].append(e[0])
        jackpot_data['core.jackpot.times'].append(e[1])
    try:
        _write_json(global_variables.jackpot_info_path, jackpot_data)
    except Exception as e:
        log('error', 'Failed to jackpot to file %s: %s' % (global_variables.jackpot_info_path, repr(e)))


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


class Config:
    def __init__(self, data_dict):
        log_call('Config.__init__')
        self._data_dict = data_dict

    @property
    def data(self):
        log_call('Config.data')
        return self._data_dict

    def __getitem__(self, key):
        log_call('Config.__getitem__', key=key)
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
        return val

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
