"""
Created by Joscha Vack on 1/5/2020.
"""

from lib import info

help_message = """"""


class Bot:
    def __init__(self, configuration, parent):
        self._parent = parent
        self._config = configuration

    def process(self, cmd):
        if cmd.IsRawData():  # ignore those
            return

        # Log cmd
        self.log_command(cmd)

        # Execute
        if cmd.IsChatMessage():
            user_id = cmd.User
            user_name = cmd.UserName

            if not self._parent.HasPermission(user_id, self._config.permission, self._config.permission_info):
                self._parent.SendStreamMessage(self._config.format_not_permitted_message(user_name))

            # debug commands
            if cmd.GetParam(0).lower() == '!debug':
                if 1 == cmd.GetParamCount():
                    return
                else:
                    kw = cmd.GetParam(1)
                    if kw == 'currency':
                        self._parent.SendStreamMessage('@%s has %d %s' % (user_name, self._parent.GetPoints(user_id), self._parent.GetCurrencyName()))
                    elif kw == 'add':
                        if 2 == cmd.GetParamCount():
                            return
                        else:
                            self._parent.AddPoints(user_id, user_name, cmd.GetParam(2))
                    elif kw == 'remove':
                        if 2 == cmd.GetParamCount():
                            return
                        else:
                            self._parent.RemovePoints(user_id, user_name, cmd.GetParam(2))

            if cmd.GetParam(0).lower() == self._config.help_command:  # display help
                if 2 == cmd.GetParamCount():
                    self.send_help(user_name, cmd.GetParam(1))
                else:
                    self.send_help(user_name)

            elif cmd.GetParam(0).lower() == self._config.prefix:  # should be chat command
                if 1 == cmd.GetParamCount():
                    self.send_help(user_name)
                else:
                    keyword = cmd.GetParam(1)
                    if keyword == self._config.gamble_keyword:
                        if not self._parent.HasPermission(user_id, self._config.permissions['gamble'],
                                                          self._config.permissions_info['gamble']):
                            self._parent.SendStreamMessage(self._config.format_not_permitted_message(user_name))
                        if 3 == cmd.GetParamCount():
                            self.gamble(user_id, user_name, int(cmd.GetParam(2)))
                        else:
                            self.send_help(user_name, self._config.gamble_keyword)
                    elif keyword == self._config.guess_keyword:
                        if not self._parent.HasPermission(user_id, self._config.permissions['guess'],
                                                          self._config.permissions_info['guess']):
                            self._parent.SendStreamMessage(self._config.format_not_permitted_message(user_name))
                        if 4 == cmd.GetParamCount():
                            self.guess(user_id, user_name, int(cmd.GetParam(2)), int(cmd.GetParam(3)))
                        else:
                            self.send_help(user_name, self._config.guess_keyword)
                    elif keyword == self._config.disclaimer_keyword:
                        self._parent.SendStreamMessage('@%s %s' % (user_name, self._config.disclaimer))
                    elif keyword == self._config.disclaimer_acknowledge_keyword:
                        self._config.whitelist.append(user_id)
                        self._parent.SendStreamMessage(self._config.format_acknowledged_message(user_name))
                        self._config.save(info.settings_path)
                    else:
                        self.send_help(user_name)

    def tick(self):
        pass

    def gamble(self, user_id, user_name, amount):
        self.bet(user_id, user_name, amount, 'gamble', lambda x: x <= self._config.gamble_chance, 100)

    def guess(self, user_id, user_name, amount, guess):
        self.bet(user_id, user_name, amount, 'guess', lambda x: x == guess, self._config.guess_max_val)

    def bet(self, user_id, user_name, amount, kind, check, max_res):
        # check whitelist
        if user_id not in self._config.whitelist:
            self._parent.SendStreamMessage(self._config.format_not_ok_message(user_name))
            return

        # check cooldown
        cd = self._parent.GetUserCooldownDuration(info.script_name, kind, user_id)
        self.log('debug', '%s cooldown: %d, uid: %s' % (kind, cd, user_id))
        if cd:
            self._parent.SendStreamMessage(
                self._config.format_cooldown_message('gamble', user_name, cd))
            return

        # check points
        points = self._parent.GetPoints(user_id)
        if points < amount:
            self._parent.SendStreamMessage('@%s %s' % (user_name, self._config.out_of_currency_message))
            return

        # gamble
        result = self._parent.GetRandom(0, max_res)
        if check(int(result)):
            winnings = amount * self._config.win_multipliers[kind]
            self._parent.AddPoints(user_id, user_name, winnings)
            self._parent.SendStreamMessage(
                self._config.format_win_message(kind, user_name, winnings, self._parent.GetPoints(user_id)))
        else:
            self._parent.RemovePoints(user_id, user_name, amount)
            self._parent.SendStreamMessage(
                self._config.format_loss_message(kind, user_name, amount, self._parent.GetPoints(user_id)))

        # set cooldown
        self._parent.AddUserCooldown(info.script_name, kind, user_id, self._config.cooldowns[kind])

    @property
    def config(self):
        return self._config

    def check_permissions(self, user):
        return self._parent.HasPermission(user, self._config.permission, self._config.info)

    def send_help(self, user, keyword=None):
        if keyword == self._config.gamble_keyword:
            self._parent.SendStreamMessage('@%s %s' % (user, self._config.gamble_help))
        elif keyword == self._config.guess_keyword:
            self._parent.SendStreamMessage('@%s %s' % (user, self._config.guess_help))
        else:
            self._parent.SendStreamMessage('@%s %s' % (user, self._config.help_message))

    def log_command(self, cmd):
        params = ', '.join([cmd.GetParam(i) for i in range(cmd.GetParamCount())])
        kind = 'Unknown'
        if cmd.IsChatMessage():
            kind = 'ChatMessage'
        elif cmd.IsRawData():
            kind = 'RawData'
        self.log('command', 'Params (%d): %s, Kind: %s, User: %s (UN: %s)' % (
            cmd.GetParamCount(), params if 0 < cmd.GetParamCount() else 'None', kind, cmd.User, cmd.UserName))

    def log(self, kind, msg):
        self._parent.Log(info.script_name, '[%s]: %s' % (kind.upper(), msg))
