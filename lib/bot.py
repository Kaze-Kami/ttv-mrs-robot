"""
Created by Joscha Vack on 1/6/2020.
"""
import lib.global_variables
import lib.info
from lib import info
from lib.config import save_whitelist
from lib.formatter import Formatter
from lib.logger import log_call, log


def _log_command(command):
    log_call('Bot:_log_command')
    params = ' '.join([command.GetParam(i) for i in range(command.GetParamCount())])
    source = 'discord' if command.IsFromDiscord() else 'stream'
    kind = 'Whisper' if command.IsWhisper() else 'Chat'
    log('info', "%s command from %s by User %s: '%s'" % (kind, source, command.UserName, params))


def _log_response(command, message, pipeline):
    log_call('Bot:_log_response')
    params = ' '.join([command.GetParam(i) for i in range(command.GetParamCount())])
    log('debug', "Response via %s to '%s' by %s: %s" % (pipeline, params, command.UserName, message))


class Bot:
    def __init__(self, parent, config):
        log_call('Bot.__init__')
        self._parent = parent
        self._config = config
        self._formatter = Formatter(config)

    """ ----------------
    " Required functions
    """

    def process(self, command):
        log_call('Bot.process', command=command.Message)
        if command.IsRawData():  # ignore those
            return
        _log_command(command)

        # check general permission
        if not self._parent.HasPermission(command.User, self._config['core.permission.value'],
                                          self._config['core.permission.info']):
            self._parent.SendStreamMessage(self._formatter.format('core.message.not_ok', user_name=command.UserName))

        # process debug commands first
        if command.GetParam(0).lower() == '!debug':
            self._process_debug_command(command)
            pass
        else:
            self._process_command(command)

    def tick(self):
        log_call('Bot.tick')

    """ ----------------
    " Core functions
    """

    def _process_command(self, command):
        log_call('Bot._process_command', command=command.Message)
        # check if is help
        if command.GetParam(0) == self._formatter.format('core.help.command'):
            key = 'core.text.malformed_command'
            if 1 == command.GetParamCount():
                key = 'core.text.help'
            elif 2 == command.GetParamCount():
                kw = command.GetParam(1)
                if kw == self._config['gamble.keyword']:
                    key = 'gamble.text.help'
                elif kw == self._config['guess.keyword']:
                    key = 'guess.text.help'
                elif kw == self._config['d20.keyword']:
                    key = 'd20.text.help'
            self._respond(command, self._formatter.format(key, user=command.UserName))
        elif command.GetParam(0) == self._config['core.prefix']:
            user_id = command.User
            user_name = command.UserName
            if 1 < command.GetParamCount():
                kw = command.GetParam(1)
                if self._config['core.disclaimer.enable']:  # check disclaimer commands
                    if kw == self._config['core.disclaimer.keyword']:
                        if 2 == command.GetParamCount():
                            if self._config['core.disclaimer.via_whisper'] and not command.IsWhisper():
                                self._respond(command, self._formatter.format('core.text.disclaimer_via_whisper',
                                                                              user=user_name), target='chat')
                            else:
                                self._respond(command, self._formatter.format('core.text.disclaimer'),
                                              target='whisper' if self._config['core.disclaimer.via_whisper'] else '')
                        else:
                            # malformed command
                            self._respond(command,
                                          self._formatter.format('core.text.malformed_command', user=user_name))
                            return
                    elif kw == self._config['core.acknowledge.keyword']:
                        if 2 == command.GetParamCount():
                            if self._config['core.disclaimer.via_whisper'] and not command.IsWhisper():
                                self._respond(command, self._formatter.format('core.text.disclaimer_via_whisper',
                                                                              user=user_name), target='chat')
                            else:
                                log('info', 'Whitelisted %s (id=%s)' % (user_name, user_id))
                                self._config['core.acknowledge.whitelist'].append(user_id)
                                save_whitelist(self._config)
                                self._respond(command, self._formatter.format('core.text.acknowledged', user=user_name),
                                              target='whisper' if self._config['core.disclaimer.via_whisper'] else '')
                        else:
                            # malformed command
                            self._respond(command,
                                          self._formatter.format('core.text.malformed_command', user=user_name))
                        return
                elif kw == self._config['core.disclaimer.keyword'] or kw == self._config['core.acknowledge.keyword']:
                    # disclaimer disable
                    if self._config['core.disclaimer.via_whisper'] and not command.IsWhisper():
                        self._respond(command, self._formatter.format('core.text.disclaimer_via_whisper',
                                                                      user=user_name), target='chat')
                    else:
                        self._respond(command, self._formatter.format('core.text.disclaimer_disable', user=user_name),
                                      target='whisper' if self._config['core.disclaimer.via_whisper'] else '')
                    return
                if kw == self._config['gamble.keyword']:
                    if 3 != command.GetParamCount():
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=user_name))
                        return
                    if not self._check_access(command, 'gamble') or not self._check_whitelist(command, user_id,
                                                                                              user_name):
                        return
                    amount = self._parse_and_check_amount(command, 2)
                    if not amount:
                        return
                    self._gamble(command, amount)
                elif kw == self._config['guess.keyword']:
                    if 4 != command.GetParamCount():
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=user_name))
                        return
                    if not self._check_access(command, 'guess') or not self._check_whitelist(command, user_id,
                                                                                             user_name):
                        return
                    # get amount
                    amount = self._parse_and_check_amount(command, 3)
                    if not amount:
                        return
                    # get guess
                    try:
                        guess = int(command.GetParam(2))
                    except:
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=user_name))
                        return
                    self._guess(command, amount, guess)
                    pass
                elif kw == self._config['d20.keyword']:
                    if 2 != command.GetParamCount():
                        self._respond(command, self._formatter.format('core.text.malformed_command', user=user_name))
                        return
                    if not self._check_access(command, 'd20'):
                        return
                    self._d20(user_id, user_name)
                else:  # malformed command
                    self._respond(command, self._formatter.format('core.text.malformed_command', user=user_name))
            else:  # unknown command
                self._respond(command, self._formatter.format('core.text.malformed_command', user=user_name))

    def _process_debug_command(self, command):
        log_call('Bot._process_debug_command', command=command.Message)
        """
         commands are:
         !debug currency
         !debug currency @User
         !debug add [amount]
         !debug add @User [amount]
         !debug remove [amount]
         !debug remove @User [amount]
        """
        if 1 == command.GetParamCount():
            log('warn', "Invalid debug command: '%s' (invalid params)" % command.Message)
            return
        else:
            user_id = command.User
            user_name = command.UserName
            kw = command.GetParam(1)
            if kw == 'currency':
                if command.GetParamCount() == 3:
                    user_name = command.GetParam(2).replace('@', '')
                    user_id = self._get_user_id(user_name)
                self._respond(command, self._formatter.format_message('{user} has %d {currency}',
                                                                      int(self._parent.GetPoints(user_id)),
                                                                      user=user_name,
                                                                      currency=self._parent.GetCurrencyName()))
            elif kw == 'add' or kw == 'remove':
                if command.GetParamCount() < 3:
                    log('warn', "Invalid debug command: '%s' (invalid params)" % command.Message)
                    return
                else:
                    if command.GetParamCount() == 4:
                        user_name = command.GetParam(2).replace('@', '')
                        user_id = self._get_user_id(user_name)
                        amount = command.GetParam(3)
                    else:
                        amount = command.GetParam(2)
                    if amount == self._config['core.all_keyword']:
                        amount = self._parent.GetPoints(user_id)
                    else:
                        try:
                            amount = int(amount)
                        except:
                            self._respond(command,
                                          self._formatter.format('core.text.malformed_command', user=user_name))
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
                log('warn', "Invalid debug command: '%s' (invalid keyword)" % command.Message)

    def _respond(self, command, response, target=''):
        log_call('Bot._respond', command=command.Message, response=response, target=target)
        cmd = None
        if command.IsWhisper() or 'whisper' in target:
            if command.IsFromDiscord() or 'discord' in target:
                target = 'Discord whisper'
                # cmd = lambda x: self._parent.SendDiscordDM(command.User, x)
            else:
                target = 'Stream whisper'
                cmd = lambda x: self._parent.SendStreamWhisper(command.User,
                                                               x + ' ' + self._config['core.text.twitch_bug'])
        else:
            if command.IsFromDiscord() or 'discord' in target:
                target = 'Discord chat'
                # cmd = lambda x: self._parent.SendDiscordMessage(x)
            else:
                target = 'Stream chat'
                cmd = lambda x: self._parent.SendStreamMessage(x)
        _log_response(command, response, target)
        if cmd:
            cmd(response)
        else:
            log('error', 'Responding to %s is not supported yet!' % target)

    """ ----------------
    " Utility functions
    """

    def _check_access(self, command, kind):
        log_call('Bot._check_access', command=command.Message, kind=kind)
        cooldown = int(self._parent.GetUserCooldownDuration(info.script_name, kind, command.User))
        if command.IsWhisper():  # ignore whisper gamble commands
            log('debug', 'Ignoring command %s, is whisper' % command.Message)
            return False
        elif not self._parent.HasPermission(command.User, self._config[kind + '.permission.value'],
                                            self._config[kind + '.permission.info']):
            self._respond(command, self._formatter.format('core.text.no_command_permission',
                                                          keyword='{' + kind + '.keyword}',
                                                          user=command.UserName))
            log('debug', 'Ignoring command %s, no permission' % command.Message)
            return False
        elif cooldown:
            self._respond(command, self._formatter.format('core.text.on_cooldown', keyword='{' + kind + '.keyword}',
                                                          user=command.UserName, cooldown=cooldown))
            log('debug', 'Ignoring command %s, on cooldown' % command.Message)
            return False
        elif not self._config[kind + '.enable']:
            self._respond(command, self._formatter.format('core.text.command_disable', keyword='{' + kind + '.keyword}',
                                                          user=command.UserName))
            log('debug', 'Ignoring command %s, disabled' % command.Message)
            return False
        return True

    def _check_whitelist(self, command, user_id, user_name):
        log_call('Bot._check_whitelist', command=command.Message, user_name=user_name, user_id=user_id)
        if not self._config['core.disclaimer.enable'] or user_id in self._config['core.acknowledge.whitelist']:
            return True
        else:
            self._respond(command, self._formatter.format('core.text.not_acknowledged', user=user_name),
                          target='whisper' if self._config['core.disclaimer.via_whisper'] else '')
            return False

    def _get_user_id(self, user_name):
        log_call('Bot._get_user_id', user_name=user_name)
        viewer_ids = self._parent.GetViewerList()
        for viewer_id in viewer_ids:
            display_name = self._parent.GetDisplayName(viewer_id)
            if display_name == user_name:
                log('debug', 'user_id for %s: %s' % (user_name, viewer_id))
                return viewer_id
        raise Exception('User %s not found' % user_name)

    def _parse_and_check_amount(self, command, index):
        log_call('Bot._parse_amount', command=command.Message, index=index)
        amount = command.GetParam(index)
        if amount == self._config['core.all_keyword']:  # check for all
            return self._parent.GetPoints(command.User)
        else:
            try:
                amount = int(amount)
                if self._parent.GetPoints(command.User) < amount:  # check user points
                    self._respond(command,
                                  self._formatter.format('core.text.not_enough_currency', user=command.UserName,
                                                         currency=self._parent.GetCurrencyName()))
                    return None
                return amount
            except:  # parsing failed -> invalid input
                self._respond(command, self._formatter.format('core.text.malformed_command', user=command.UserName))
                return None

    """ ----------------
    " Minigames
    """

    def _gamble(self, command, amount):
        log_call('Bot._gamble', command=command.Message, amount=amount)
        roll = self._parent.GetRandom(0, 100)
        add = False
        if self._config['gamble.triple.enable'] and roll < int(self._config['gamble.triple.chance']):
            amount *= int(self._config['gamble.win_multiplier']) * 3
            add = True
        elif self._config['gamble.double.enable'] and roll < int(self._config['gamble.double.chance']):
            amount *= int(self._config['gamble.win_multiplier']) * 2
            add = True
        elif roll <= int(self._config['gamble.chance']):
            amount *= int(self._config['gamble.win_multiplier']) * 2
            add = True

        if add:
            self._parent.AddPoints(command.User, command.UserName, amount)
        else:
            self._parent.RemovePoints(command.User, command.UserName, amount)

        log('debug', '%s %s %d coins with roll %d' % (command.UserName, 'won' if add else 'lost', amount, roll))
        self._respond(command, self._formatter.format('gamble.text.' + ('win' if add else 'lose'),
                                                      roll=100 - roll,
                                                      user=command.UserName,
                                                      payout=amount,
                                                      loss=amount,
                                                      currency=self._parent.GetCurrencyName(),
                                                      total=self._parent.GetPoints(command.User)))
        self._parent.AddUserCooldown(info.script_name, 'gamble', command.User, self._config['gamble.cooldown'])

    def _guess(self, command, guess, amount):
        log_call('Bot._guess', command=command.Message, guess=guess, amount=amount)
        roll = self._parent.GetRandom(0, int(self._config['guess.max_val']))
        if roll == guess:
            amount *= int(self._config['guess.win_multiplier'])
            log('debug', '%s won %d coins with roll %d (guess was %d)' % (command.UserName, amount, roll, guess))
            self._parent.AddPoints(command.User, command.UserName, amount)
            self._respond(command, self._formatter.format('guess.text.win',
                                                          user=command.UserName,
                                                          guess=guess,
                                                          payout=amount,
                                                          total=self._parent.GetPoints(command.User),
                                                          currency=self._parent.GetCurrencyName()))
        else:
            log('debug', '%s lost %d coins with roll %d (guess was %d)' % (command.UserName, amount, roll, guess))
            self._parent.RemovePoints(command.User, command.UserName, amount)
            self._respond(command, self._formatter.format('guess.text.lose',
                                                          user=command.UserName,
                                                          guess=guess,
                                                          roll=roll,
                                                          loss=amount,
                                                          total=self._parent.GetPoints(command.User),
                                                          currency=self._parent.GetCurrencyName()))
        self._parent.AddUserCooldown(info.script_name, 'guess', command.User, self._config['guess.cooldown'])

    def _d20(self, command):
        log_call('Bot._d20', command=command.Message)
        texts = self._config['d20.text.results'].replpace('\r').split('\n')
        if not texts[-1]:
            texts = texts[:-1]
        res = texts[self._parent.GetRando(0, len(texts))]
        self._respond(command, self._formatter.format_message(res, user=command.UserName, random_user=self._parent.GetRandomActiveUser()))
        self._parent.AddUserCooldown(info.script_name, 'd20', command.User, self._config['d20.cooldown'])

    @property
    def config(self):
        log_call('Bot.config', trace=True)
        return self._config
