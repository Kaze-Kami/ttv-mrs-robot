"""
Created by Joscha Vack on 1/11/2020.
"""
import sys

from lib.logger import log_call


# noinspection PyBroadException
class Command(object):
    def __init__(self, data, remove_prefix):
        log_call('Command.__init__', data=data.Message, remove_prefix=remove_prefix)
        self._data = data
        self._params = [data.GetParam(i).lower() for i in range(data.GetParamCount())]  # copy params
        if 0 < len(self._params):  # replace prefix or leading !
            if remove_prefix:
                self._params = self._params[1:]
            else:
                self._params[0] = self._params[0].replace('!', '')

        self._from_stream = not data.IsFromDiscord()
        self._is_whisper = data.IsWhisper()

    def __len__(self):
        log_call('Command.__len__')
        return len(self._params)

    def __iter__(self):
        log_call('Command.__iter__')
        for p in self._params:
            yield p

    def __getitem__(self, args):
        log_call('Command.__getitem__', args=args)
        try:
            i, f = args
        except:
            i = args
            f = str
        return f(self._params[i])

    def __str__(self):
        log_call('Command.__str__.getter')
        return "Command '%s' by '%s' (id=%s) from %s %s: %d params %s" % (
            self.message, self.user_name, self.user_id, self.origin, self.kind, len(self), '[' + ', '.join(self.params) + ']')

    @property
    def is_whisper(self):
        log_call('Command.is_whisper.getter')
        return self._is_whisper

    @property
    def is_chat(self):
        log_call('Command.is_chat.getter')
        return not self._is_whisper

    @property
    def from_stream(self):
        log_call('Command.from_stream.getter')
        return self._from_stream

    @property
    def from_discord(self):
        log_call('Command.from_discord.getter')
        return not self._from_stream

    @property
    def message(self):
        log_call('Command.message.getter')
        return self._data.Message

    @property
    def params(self):
        log_call('Command.params.getter')
        return self._params

    @property
    def kind(self):
        log_call('Command.kind.getter')
        return 'whisper' if self._is_whisper else 'chat'

    @property
    def origin(self):
        log_call('Command.origin.getter')
        return 'stream' if self._from_stream else 'discord'

    @property
    def user_id(self):
        log_call('Command.user_id.getter')
        return self._data.User

    @property
    def user_name(self):
        log_call('Command.user_name.getter')
        return self._data.UserName
