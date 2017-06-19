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

import sys

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from management import execute_command

from templates import models

BANNER = r"""
             ___     ___ __         __  ___     __
|__/ /\ |\/||__ |   |__ /  \|\ |   |  \|__ |\/|/  \
|  \/~~\|  ||___|___|___\__/| \|   |__/|___|  |\__/

"""

def error(failure):
    print("ERROR: Failure")
    print(failure)

@inlineCallbacks
def main(argv):

    yield models.DATABASE.connect()
    yield execute_command(models, argv=argv)

if __name__ == "__main__":

    print("")
    print("-------------------------------------------------------------------")
    print(BANNER)

    argv = None
    if len(sys.argv) > 1:
        argv = sys.argv[1:]

    d = main(argv)

    reactor.run()

    if models.DATABASE and hasattr(models.DATABASE, "connection"):
        print("")
        print("DEBUG: Database closed")
        models.DATABASE.connection.close()
    else:
        print("")

    print("INFO: Kameleon stopped")
    print("-------------------------------------------------------------------")
