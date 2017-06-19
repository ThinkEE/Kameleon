################################################################################
# MIT License
#
# Copyright (c) 2017 Jean-Charles Fosse & Johann Bigler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################

import traceback

from twisted.internet.defer import inlineCallbacks

import commands

class CommandExecutor(object):
    """
    Encapsulates commands utilities. It has a number of commands, which can be
    manipulated by editing the self.commands dictionary.
    """

    def __init__(self, argv=None):
        self.argv = argv

        # Dictonary of command
        self.commands = {
            "--create": commands.Create,
            "--reset": commands.Reset,
            "--test": commands.Test
        }

    @inlineCallbacks
    def find_command(self, subcommand, models):
        """
        Find the corresponding command in order to execute it
        """

        # Unknown command
        if subcommand not in self.commands.keys() and subcommand != '--help':
            print('The command %s is unknown'%(subcommand))

        # Help show options
        elif subcommand == '--help':
            print('Invalid Command. Use the following commands: %s'%(self.commands))

        # Command exists. Call it
        else:
            cmd = self.commands[subcommand]()
            try:
                yield cmd.handle(models)
            except Exception as err:
                print("ERROR: Error in command handle: %s" %(err))
                traceback.print_exc()

    @inlineCallbacks
    def execute(self, models):
        """
        Is used to execute the command corresponding to the passed argument.
        """

        if self.argv:
            subcommand = self.argv[0]
        else:
            subcommand = '--help' # Display help if no arguments were given.

        yield self.find_command(subcommand, models)

@inlineCallbacks
def execute_command(models=None, argv=None):
    """
    A simple method that runs a CommandExecutor.
    """

    executor = CommandExecutor(argv)
    yield executor.execute(models)
