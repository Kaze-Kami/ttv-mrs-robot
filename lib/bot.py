"""
Created by Joscha Vack on 1/6/2020.
"""

from lib import info
from lib.command import Command
from lib.logger import log_call, log
from lib.config import save_whitelist, save_jackpot, Config, _format_dict
from lib.formatter import Formatter
from lib.live_counter import LiveCounter


def _log_response(command, message, pipeline):
    # type: (Command, str, str) -> None
    log_call('Bot:_log_response')
    log('debug', "Response via %s to '%s': %s" % (pipeline, command, message))


# noinspection PyBroadException
class Bot(object):
    def __init__(self, parent, config):
        # type: (object, Config) -> None
        log_call('Bot.__init__')
        self._parent = parent
        self._config = config
        self._formatter = Formatter(config)
        self._live_counter = LiveCounter(parent)

    """ ----------------
    " Required functions
    """

    def process(self, data):
        log_call('Bot.process', command=data.Message)
        if data.GetParam(0) == '!debug':  # check for debug command, todo: remove this for production builds
            self._process_debug_command(Command(data, True))
            return

        if data.GetParam(0)[0] == '!':
            if self._config['core.prefix.enable', bool]:
                if data.GetParam(0).replace('!', '').lower() != self._config['core.prefix.text']:
                    log('debug', 'Ignoring command %s, no prefix' % data.Message)
                    return
                command = Command(data, True)
            else:
                command = Command(data, False)
        else:
            log('debug', 'Ignoring message %s, no leading !' % data.Message)
            return

        # check general permission
        if self._parent.HasPermission(command.user_id, self._config['core.permission.value'], self._config['core.permission.info']):
            if not self._process_command(command) and self._config['core.prefix.enable', bool]:
                self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
        else:
            self._parent.SendStreamMessage(self._formatter.format('core.text.no_permission', user_name=command.user_name))

    def tick(self):
        self._live_counter.update()

    def shutdown(self):
        log_call('Bot.shutdown')
        self._update_jackpot(subtract=True)

    """ ----------------
    " Core functions
    """

    def _process_command(self, command):
        # type: (Command) -> bool
        log_call('Bot._process_command', command=command)
        # check for params
        if 0 == len(command):
            return False

        # check if is help
        if command[0] == self._config['core.help.keyword']:
            key = None
            if 1 == len(command):
                key = 'core.text.help'
            elif 2 == len(command):
                kw = command[1]
                if kw == self._config['gamble.keyword']:
                    key = 'gamble.text.help'
                elif kw == self._config['guess.keyword']:
                    key = 'guess.text.help'
                elif kw == self._config['d20.keyword']:
                    key = 'd20.text.help'
                elif kw == self._config['jackpot.keyword']:
                    key = 'jackpot.text.help'
            if key:
                self._respond(command, self._formatter.format(key, user=command.user_name))
            else:
                # malformed command
                self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
            # command processed
            return True
        else:
            kw = command[0]
            # check disclaimer commands
            if self._config['disclaimer.enable', bool]:
                if kw == self._config['disclaimer.keyword']:
                    if 1 == len(command):
                        if self._config['disclaimer.via_whisper'] and not command.is_whisper:
                            self._respond(command, self._formatter.format('disclaimer.text.via_whisper',
                                                                          user=command.user_name), target='whisper')
                        else:
                            self._respond(command, self._formatter.format('disclaimer.text.disclaimer'),
                                          target='whisper' if self._config['disclaimer.via_whisper'] else '')
                    else:
                        # malformed command
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                    # command processed
                    return True
                elif kw == self._config['disclaimer.acknowledge_keyword']:
                    if 1 == len(command):
                        if self._config['disclaimer.via_whisper'] and not command.is_whisper:
                            self._respond(command, self._formatter.format('disclaimer.text.via_whisper',
                                                                          user=command.user_name), target='whisper')
                        else:
                            log('info', 'Whitelisted %s (id=%s)' % (command.user_name, command.user_id))
                            self._config['disclaimer.whitelist'].append(command.user_id)
                            save_whitelist(self._config)
                            self._respond(command, self._formatter.format('disclaimer.text.acknowledged', user=command.user_name),
                                          target='whisper' if self._config['disclaimer.via_whisper'] else '')
                    else:
                        # malformed command
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                    # command processed
                    return True
            elif kw == self._config['disclaimer.keyword'] or kw == self._config['disclaimer.acknowledge_keyword']:
                # disclaimer disable
                if 1 == len(command):
                    if self._config['disclaimer.via_whisper'] and not command.is_whisper:
                        self._respond(command, self._formatter.format('disclaimer.text.via_whisper',
                                                                      user=command.user_name), target='whisper')
                    else:
                        self._respond(command, self._formatter.format('disclaimer.text.disable', user=command.user_name),
                                      target='whisper' if self._config['disclaimer.via_whisper'] else '')
                else:
                    # malformed command
                    self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                # command processed
                return True

            # check non disclaimer commands
            if kw == self._config['jackpot.keyword']:
                if 1 == len(command):
                    self._update_jackpot()
                    self._respond(command, self._formatter.format('jackpot.text.content', currency=self._parent.GetCurrencyName(), user=command.user_name))
                else:
                    # malformed command
                    self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                # command processed
                return True
            elif kw == self._config['gamble.keyword']:
                if 2 != len(command):
                    # malformed command
                    self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                elif self._check_access(command, 'gamble') and self._check_whitelist(command):
                    amount = self._parse_and_check_amount(command, 1)
                    if amount:
                        self._gamble(command, amount)
                    else:
                        # malformed command
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                # command processed
                return True
            elif kw == self._config['guess.keyword']:
                if 3 != len(command):
                    # malformed command
                    self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                elif self._check_access(command, 'guess') and self._check_whitelist(command):
                    # get amount
                    amount = self._parse_and_check_amount(command, 2)
                    if amount:
                        # get guess
                        try:
                            guess = command[1, int]
                            if guess < 0 or self._config['guess.max_val', int] < guess:
                                # guess not in range
                                self._respond(command, self._formatter.format('guess.text.not_in_range', user=command.user_name, guess=guess))
                            else:
                                self._guess(command, guess, amount)
                        except:
                            # malformed command
                            self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                    else:
                        # malformed command
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                # command processed
                return True
            elif kw == self._config['d20.keyword']:
                if 2 != len(command):
                    # malformed command
                    self._respond(command, self._formatter.format('core.text.malformed_command', user=command.user_name))
                elif self._check_access(command, 'd20'):
                    self._d20(command)
                # command processed
                return True

        # command not processed
        return False

    def _process_debug_command(self, command):
        # type: (Command) -> None
        log_call('Bot._process_debug_command', command=command)
        """
         commands are:
         !debug currency
         !debug currency @User
         !debug add [amount]
         !debug add @User [amount]
         !debug remove [amount]
         !debug remove @User [amount]
        """
        if 0 == len(command):
            log('warn', "Invalid debug command: '%s' (no keyword)" % command)
        else:
            kw = command[0]
            user_name = command.user_name
            user_id = command.user_id
            if kw == 'currency':
                if 2 == len(command):
                    user_name = command[1].replace('@', '')
                    user_id = self._get_user_id(user_name)
                elif 2 < len(command):
                    log('warn', "Invalid debug command: '%s' (too many params)" % command)
                    return
                self._respond(command, self._formatter.format_message('{user} has %d {currency}',
                                                                      int(self._parent.GetPoints(user_id)),
                                                                      user=user_name,
                                                                      currency=self._parent.GetCurrencyName()))
            elif kw == 'add' or kw == 'remove':
                if 1 == len(command):
                    log('warn', "Invalid debug command: '%s' (not enough params)" % command)
                    return
                else:
                    if 3 < len(command):
                        log('warn', "Invalid debug command: '%s' (too many params)" % command)
                        return
                    if 3 == len(command):
                        user_name = command[1].replace('@', '')
                        user_id = self._get_user_id(user_name)
                        amount = command[2]
                    else:
                        amount = command[1]
                    if amount == self._config['core.all_keyword']:
                        amount = self._parent.GetPoints(user_id)
                    else:
                        try:
                            amount = int(amount)
                        except:
                            log('warn', "Invalid debug command: '%s' (can not parse amount)" % command)
                            return
                if kw == "add":
                    self._parent.AddPoints(user_id, user_name, amount)
                    log('info', 'Gave %s %d coins.' % (user_name, amount))
                    action = 'Added'
                else:
                    self._parent.RemovePoints(user_id, user_name, amount)
                    log('info', 'Took %d coins from %s.' % (amount, user_name))
                    action = 'Removed'
                response = self._formatter.format_message('{action} %d {currency}, {user} now has %d {currency}',
                                                          amount, self._parent.GetPoints(user_id), user=user_name,
                                                          currency=self._parent.GetCurrencyName(), action=action)
                self._respond(command, response)
            else:
                log('warn', "Invalid debug command: '%s' (invalid keyword)" % command)
                return

    def _respond(self, command, response, target=''):
        # type: (Command, str, str) -> None
        log_call('Bot._respond', command=command, response=response, target=target)
        cmd = None
        if command.is_whisper or 'whisper' in target:
            if command.from_discord or 'discord' in target:
                target = 'Discord whisper'
                # cmd = lambda x: self._parent.SendDiscordDM(command.User, x)
            else:
                target = 'Stream whisper'

                def cmd(x):
                    self._parent.SendStreamWhisper(command.user_id, x + ' ' + self._config['core.text.twitch_bug'])
        else:
            if command.from_discord or 'discord' in target:
                target = 'Discord chat'
                # cmd = lambda x: self._parent.SendDiscordMessage(x)
            else:
                target = 'Stream chat'

                def cmd(x):
                    self._parent.SendStreamMessage(x)
        _log_response(command, response, target)
        if cmd:
            cmd(response)
        else:
            log('error', 'Responding to %s is not supported yet!' % target)

    """ ----------------
    " Utility functions
    """

    def _check_access(self, command, kind):
        # type: (Command, str) -> bool
        log_call('Bot._check_access', command=command, kind=kind)
        cooldown = int(self._parent.GetUserCooldownDuration(info.script_name, kind, command.user_id))
        reason = None
        if command.is_whisper:  # ignore whisper gamble commands
            reason = 'is whisper'
        elif not self._parent.HasPermission(command.user_id, self._config[kind + '.permission.value'], self._config[kind + '.permission.info']):
            self._respond(command, self._formatter.format('core.text.no_command_permission', keyword='{' + kind + '.keyword}', user=command.user_name))
            reason = 'no permission'
        elif cooldown:
            self._respond(command, self._formatter.format('core.text.on_cooldown', keyword='{' + kind + '.keyword}', user=command.user_name, cooldown=cooldown))
            reason = 'on cooldown'
        elif not self._config[kind + '.enable', bool]:
            self._respond(command, self._formatter.format('core.text.command_disable', keyword='{' + kind + '.keyword}', user=command.user_name))
            reason = 'disabled'

        if reason:
            log('debug', 'Ignoring command %s, %s' % (str(command), reason))
            return False
        return True

    def _check_whitelist(self, command):
        # type: (Command) -> bool
        log_call('Bot._check_whitelist', command=command)
        if not self._config['disclaimer.enable', bool] or command.user_id in self._config['disclaimer.whitelist']:
            return True
        else:
            self._respond(command, self._formatter.format('disclaimer.text.not_acknowledged', user=command.user_name),
                          target='whisper' if self._config['disclaimer.via_whisper'] else '')
            return False

    def _get_user_id(self, user_name):
        # type: (str) -> str
        log_call('Bot._get_user_id', user_name=user_name)
        viewer_ids = self._parent.GetViewerList()
        for viewer_id in viewer_ids:
            display_name = self._parent.GetDisplayName(viewer_id)
            if display_name == user_name:
                log('debug', 'user_id for %s: %s' % (user_name, viewer_id))
                return viewer_id
        raise Exception('User %s not found' % user_name)

    def _parse_and_check_amount(self, command, index):
        # type: (Command, int) -> int or None
        log_call('Bot._parse_and_check_amount', command=command, index=index)
        try:
            return command[index, int]
        except:  # parse failed either due to index or its not a number
            if command[index] == self._config['core.all_keyword']:
                return self._parent.GetPoints(command.user_id)
            return None

    def _get_jackpot(self):
        # type: () -> int
        log_call('Bot._get_jackpot')
        self._update_jackpot()
        return self._config['jackpot.sum']

    def _add_to_jackpot(self, amount):
        # type: (float) -> None
        log_call('Bot._add_to_jackpot', amout=amount)
        self._config['jackpot.entries'].append((amount, self._config['jackpot.decay.total', int] + self._live_counter.seconds_live))
        self._update_jackpot()

    def _clear_jackpot(self):
        # type: () -> None
        log_call('Bot._clear_jackpot')
        self._config['jackpot.entries'] = []
        save_jackpot(self._config)

    def _update_jackpot(self, subtract=False):
        # type: (bool) -> None
        log_call('Bot._update_jackpot', subtract=subtract)
        live_time = self._live_counter.seconds_live
        amount = 0.
        for i, v, t in reversed([(i, e[0], e[1]) for i, e in enumerate(self._config['jackpot.entries'])]):
            if t - live_time <= 0:
                log('debug', 'Removing entry %d from the jackpot (value=%d, time=%d)' % (i, v, t))
                del self._config['jackpot.entries'][i]
            else:
                log('debug', 'Jackpot entry %d: value=%d, time remaining=%d' % (i, v, t - live_time))
                if subtract:
                    self._config['jackpot.entries'][i][1] -= live_time
                amount += v
        self._config['jackpot.sum'] = int(amount)
        save_jackpot(self._config)

    """ ----------------
    " Minigames
    """

    # noinspection Duplicates
    def _gamble(self, command, amount):
        # type: (Command, int) -> None
        log_call('Bot._gamble', command=command, amount=amount)
        roll = self._parent.GetRandom(0, 100)
        add = False
        if roll + 1 == self._config['jackpot.number', int] and self._config['jackpot.enable', bool]:
            # jackpot
            jackpot = self._get_jackpot()
            self._clear_jackpot()
            log('debug', '%s won the jackpot of %d coins' % (command.user_name, jackpot))
            self._parent.AddPoints(command.user_id, command.user_name, jackpot)
            self._respond(command, self._formatter.format('jackpot.text.win', user=command.user_name, roll=self._config['jackpot.number'],
                                                          currency=self._parent.GetCurrencyName(), total=self._parent.GetPoints(command.user_id)))
        else:
            if self._config['gamble.triple.enable', bool] and roll < self._config['gamble.triple.chance', int]:
                amount *= self._config['gamble.win_multiplier', int] * 3
                add = True
            elif self._config['gamble.double.enable', bool] and roll < self._config['gamble.double.chance', int]:
                amount *= self._config['gamble.win_multiplier', int] * 2
                add = True
            elif roll <= self._config['gamble.chance', int]:
                amount *= self._config['gamble.win_multiplier', int] * 2
                add = True

            if add:
                log('debug', '%s won %d coins with roll %d' % (command.user_name, amount, roll))
                self._parent.AddPoints(command.user_id, command.user_name, amount)
            else:
                log('debug', '%s lost %d coins with roll %d' % (command.user_name, amount, roll))
                self._parent.RemovePoints(command.user_id, command.user_name, amount)
                if self._config['jackpot.enable', bool]:
                    log('debug', 'Adding %f coins to jackpot' % (amount * self._config['jackpot.percentage', float] / 100))
                    self._add_to_jackpot(amount * self._config['jackpot.percentage', float] / 100)

            self._respond(command, self._formatter.format('gamble.text.' + ('win' if add else 'lose'),
                                                          roll=100 - roll, user=command.user_name,
                                                          payout=amount, loss=amount,
                                                          currency=self._parent.GetCurrencyName(),
                                                          total=self._parent.GetPoints(command.user_id)))
        self._parent.AddUserCooldown(info.script_name, 'gamble', command.user_id, self._config['gamble.cooldown', int])

    # noinspection Duplicates
    def _guess(self, command, guess, amount):
        # type: (Command, int, int) -> None
        log_call('Bot._guess', command=command, guess=guess, amount=amount)
        roll = self._parent.GetRandom(0, self._config['guess.max_val', int] + 1)
        if roll == guess:
            amount *= self._config['guess.win_multiplier', int]
            log('debug', '%s won %d coins with roll %d (guess was %d)' % (command.user_name, amount, roll, guess))
            self._parent.AddPoints(command.user_name, command.user_id, amount)
            self._respond(command, self._formatter.format('guess.text.win', user=command.user_name, guess=guess,
                                                          payout=amount, total=self._parent.GetPoints(command.user_id),
                                                          currency=self._parent.GetCurrencyName()))
        else:
            log('debug', '%s lost %d coins with roll %d (guess was %d)' % (command.user_name, amount, roll, guess))
            self._parent.RemovePoints(command.user_id, command.user_name, amount)
            if self._config['jackpot.enable', bool]:
                log('debug', 'Adding %f coins to jackpot' % (amount * self._config['jackpot.percentage', float] / 100))
                self._add_to_jackpot(amount * self._config['jackpot.percentage', float] / 100)
            self._respond(command, self._formatter.format('guess.text.lose', user=command.user_name, guess=guess, roll=roll,
                                                          loss=amount, total=self._parent.GetPoints(command.user_id),
                                                          currency=self._parent.GetCurrencyName()))
        self._parent.AddUserCooldown(info.script_name, 'guess', command.user_id, self._config['guess.cooldown', int])

    def _d20(self, command):
        # type: (Command) -> None
        log_call('Bot._d20', command=command)
        texts = self._config['d20.text.results'].split(';')
        if not texts[-1]:
            texts = texts[:-1]
        res = texts[self._parent.GetRandom(0, len(texts))]
        self._respond(command, self._formatter.format_message(res, user=command.user_name, random_user=self._parent.GetRandomActiveUser()))
        self._parent.AddUserCooldown(info.script_name, 'd20', command.user_id, self._config['d20.cooldown'])

    @property
    def config(self):
        log_call('Bot.config.getter')
        return self._config

    @config.setter
    def config(self, config):
        log_call('Bot.config.setter')
        self._config = config
        self._formatter.config = config
