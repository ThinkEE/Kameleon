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

import json
from datetime import datetime

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

from postgresql import PostgresqlDatabase

class WampPostgresqlDatabase(PostgresqlDatabase):
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self, name, **connect_kwargs):
        super(WampPostgresqlDatabase, self).__init__(name, connect_kwargs)
        self.subscribe = True

    @classmethod
    def default(cls, obj):
        if isinstance(obj, datetime):
            return {
                "_type": "datetime",
                "data": obj.strftime(cls.TIME_FORMAT)
            }
        return json.JSONEncoder.default(cls, obj)

    @classmethod
    def object_hook(cls, obj):
        if '_type' not in obj:
            return obj

        _type = obj['_type']
        if _type == 'datetime':
            return datetime.strptime(obj["data"], cls.TIME_FORMAT)

    @classmethod
    def encode(cls, data):
        return json.JSONEncoder(default=cls.default).encode(data)

    @classmethod
    def decode(cls, string):
        return json.JSONDecoder(object_hook=cls.object_hook).decode(string)

    @inlineCallbacks
    def _connect(self, **kwargs):
        self.wait_connection = Deferred()
        self.connection = kwargs['session']
        self.runOperation_uri = u'wamp.postgresql.%s.run.operation' %(self.name.lower())
        self.runQuery_uri = u'wamp.postgresql.%s.run.query' %(self.name.lower())
        yield self.wait_connection

    def connected(self):
        if not self.wait_connection:
            self.wait_connection = Deferred()

        from autobahn.wamp.types import SubscribeOptions
        self.connection.subscribe(self._ready, u"wamp.postgresql.ready", options=SubscribeOptions(get_retained=True))

    def disconnected(self):
        if self.wait_connection:
            d, self.wait_connection = self.wait_connection, None

    def _ready(self, message):
        if message == 'Ready':
            if self.wait_connection:
                d, self.wait_connection = self.wait_connection, None
                d.callback(True)

    @inlineCallbacks
    def _close(self, *args):
        print("DEBUG: Closing connection to %s" %(self.database))
        yield 1

    @inlineCallbacks
    def runOperation(self, operation):
        try:
            yield self.connection.call(self.runOperation_uri, operation)
        except Exception as err:
            print("ERROR: Running operation %s" %operation)
            print(err)

    @inlineCallbacks
    def runQuery(self, query):
        answer = []
        try:
            answer = yield self.connection.call(self.runQuery_uri, query)
            answer = self.decode(answer)
        except Exception as err:
            print("ERROR: Running query %s" %query)
            print(err)
            # XXX Return special values if error. The code should be able to know
        returnValue(answer)

    def propagate(self, model):
        print("INFO: Propagating information on -- wamp.postgresql.propagadate.{0} --".format(model._meta.name))
        self.connection.publish(u"wamp.postgresql.propagadate.{0}".format(model._meta.name), model.dictValues)
