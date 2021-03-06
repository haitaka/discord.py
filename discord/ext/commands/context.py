# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2015-2016 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio

class Context:
    """Represents the context in which a command is being invoked under.

    This class contains a lot of meta data to help you understand more about
    the invocation context. This class is not created manually and is instead
    passed around to commands by passing in :attr:`Command.pass_context`.

    Attributes
    -----------
    message : :class:`discord.Message`
        The message that triggered the command being executed.
    bot : :class:`Bot`
        The bot that contains the command being executed.
    args : list
        The list of transformed arguments that were passed into the command.
        If this is accessed during the :func:`on_command_error` event
        then this list could be incomplete.
    kwargs : dict
        A dictionary of transformed arguments that were passed into the command.
        Similar to :attr:`args`\, if this is accessed in the
        :func:`on_command_error` event then this dict could be incomplete.
    prefix : str
        The prefix that was used to invoke the command.
    command
        The command (i.e. :class:`Command` or its superclasses) that is being
        invoked currently.
    invoked_with : str
        The command name that triggered this invocation. Useful for finding out
        which alias called the command.
    invoked_subcommand
        The subcommand (i.e. :class:`Command` or its superclasses) that was
        invoked. If no valid subcommand was invoked then this is equal to
        `None`.
    subcommand_passed : Optional[str]
        The string that was attempted to call a subcommand. This does not have
        to point to a valid registered subcommand and could just point to a
        nonsense string. If nothing was passed to attempt a call to a
        subcommand then this is set to `None`.
    """
    __slots__ = ['message', 'bot', 'args', 'kwargs', 'command', 'view',
                 'invoked_with', 'invoked_subcommand', 'subcommand_passed',
                 'prefix' ]

    def __init__(self, **attrs):
        self.message = attrs.pop('message', None)
        self.bot = attrs.pop('bot', None)
        self.args = attrs.pop('args', [])
        self.kwargs = attrs.pop('kwargs', {})
        self.prefix = attrs.pop('prefix')
        self.command = attrs.pop('command', None)
        self.view = attrs.pop('view', None)
        self.invoked_with = attrs.pop('invoked_with', None)
        self.invoked_subcommand = attrs.pop('invoked_subcommand', None)
        self.subcommand_passed = attrs.pop('subcommand_passed', None)

    @asyncio.coroutine
    def invoke(self, command, **kwargs):
        if len(kwargs) == 0:
            yield from command.invoke(self)
        else:
            yield from command.callback(**kwargs)
