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

from twisted.internet.defer import inlineCallbacks

class Database(object):
    """
    Base class for any Database implementation
    """

    TYPES = {
        'BOOL': 'bool',
        'CHAR': 'varchar',
        'FLOAT': 'float',
        'INT': 'int',
        'DATE': 'timestamp'
    }

    def __init__(self, name, **connect_kwargs):
        self.name = name
        self.connect_kwargs = connect_kwargs

    @inlineCallbacks
    def connect(self):
        yield self._connect(**self.connect_kwargs)

    @inlineCallbacks
    def close(self):
        yield self._close()

    @inlineCallbacks
    def runOperation(self, *args, **kwargs):
        """
        Run an operation on the Database. The database do not send any answers back
        """
        raise NotImplementedError('Run operation not implemented')

    @inlineCallbacks
    def runQuery(self, *args, **kwargs):
        """
        Run an query on the Database. The database send an answer back
        """
        raise NotImplementedError('Run query not implemented')
