"""
Created by Joscha Vack on 1/6/2020.

formatted texts used:
    {core.prefix}?
    I did not get that. Type \'{core.help.command}\' for help and try again.
    Type: \'{gamble.command}\' to gamble, \'{guess.command}\' to guess, \'{core.help.command} command\' to view more information about a command.
    Use \'{gamble.command} [amount]\' to gamble. Chances of winning are {gamble.chance}
    Use \'{guess.command} [amount] [guess]\' to guess. Guess has to be between 0 and {guess.max_val}
    You are not permitted to use this command {user.mention}.
    Gambling can be addictive. Play responsibly. Underage gambling is an offence. Type \'{core.acknowledge.command}\' to acknowledge this disclaimer.
    You need to acknowledge the gambling disclaimer before gambling, {user}. Type \'{core.disclaimer.command}\' to display it.
    You can gamble now {user.mention}!
    You don\'t have enough {currency} to do this!
    {user.mention} won {winnings} {currency} and has {total} {currency}!
    {user.mention} won {winnings} {currency} and has {total} {currency}!
    {user.mention} lost {loss} {currency} and has {total} {currency}!
    {user.mention} lost {loss} {currency} and has {total} {currency}!
    You can not gamble again already {user.mention}. You need to wait {cooldown}
    You can not guess again already {user.mention}. You need to wait {cooldown}

available identifiers in config:
    user (requires user_name in data):
        mention
        name
    core:
        prefix
        acknowledge:
            keyword
            command
        disclaimer:
            keyword
            command
        help:
            keyword
            command
    gamble:
        keyword
        command
        chance
    guess:
        keyword
        command
        max_value
other identifiers:
    currency
    total
    winnings
    loss
    cooldown
"""
import re

from logger import log_call

# regex for replacements
reg = re.compile(r'{(.*?)}')


class Formatter:
    def __init__(self, config):
        log_call('Formatter.__init__')
        self._config = config

    def format(self, key, *data, **kw_data):
        log_call('Formatter.format', key=key, data=data, kw_data=kw_data)
        return self._format_text(self._config[key], *data, **kw_data)

    def format_message(self, message, *data, **kw_data):
        log_call('Formatter.message', message=message, data=data, kw_data=kw_data)
        return self._format_text(message, *data, **kw_data).capitalize()

    def _format_text(self, text, *data, **kw_data):
        log_call('Formatter._format_text', text=text, data=data, kw_data=kw_data)
        matches = list(reg.finditer(text))
        for m in reversed(matches):
            k = m.group(1)
            v = m.group(0)
            if k in kw_data:
                v = self._format_text(str(kw_data[k]), **kw_data)
            elif k in self._config:
                v = self._format_text(str(self._config[k]), **kw_data)
            else:
                raise KeyError(k)
            text = text[:m.start()] + v + text[m.end():]
        return text % data if data else text
