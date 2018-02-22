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

from twisted.internet.defer import inlineCallbacks, returnValue

from base import Query

class UpdateQuery(Query):
    """
    Object representing an update query
    """

    def __init__(self, model_class, values):
        super(UpdateQuery, self).__init__(model_class)
        # Values to update
        self.values = values
        self.return_id = self.model_class._meta.primary_key

    @inlineCallbacks
    def execute(self):
        query, values = self.database.generate_update(self)

        # If return id. Use runQuery else use runOperation
        if self.return_id:
            result = yield self.database.runQuery(query, values)
            if result and self.model_class._meta.primary_key:
                returnValue(result[0][0])
        else:
            yield self.database.runOperation(query, values)

        returnValue(None)
