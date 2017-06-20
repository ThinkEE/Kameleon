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

import operator

from twisted.internet.defer import inlineCallbacks, returnValue

from base import Query

class Join(object):
    """
    Class representing a join clause
    """
    def __init__(self, src, dest, joint_type, on):
        self.src = src
        self.dest = dest
        self.joint_type = joint_type
        self.on = on

class SelectQuery(Query):
    """
    Class representing a select query with its join and where clause
    """
    def __init__(self, model_class):
        super(SelectQuery, self).__init__(model_class)
        # Query result
        self._results = None

        # Number of entries returned
        self._total = 0

        # Is it a delete query
        self._delete = False

        # List of joins
        self._joins = []
        # Current table to use to join
        self._table_join = self.model_class

    def where(self, *expressions):
        """
        Set the where clause
        """
        self._where = reduce(operator.and_, expressions)
        return self

    def switch(self, dest):
        """
        Switch the current table for the next join
        """
        self._table_join = dest
        return self

    def join(self, dest, join_type=None, on=None):
        """
        If on not specified then use the ForeignKey between the two models
        """
        # XXX #5 To DO: Manage on and join_type
        join = Join(self._table_join, dest, join_type, on)
        self._joins.append(join)
        self._table_join = dest
        return self

    def delete(self):
        """
        Set this query as a delete query
        """
        self._delete = True
        return self

    @inlineCallbacks
    def execute(self):
        """
        Execute query
        """
        # Generate Query
        computedQuery = self.database.generate_select(self)

        # Run query
        result = yield self.database.runQuery(computedQuery)

        # Parse result
        self._results = self.database.parse_select(self, result)
        self._total = len(self._results)
        returnValue(self)

    def __iter__(self):
        return iter(self._results)

    # If value bigger than number of objects, return the last object of the list
    def __getitem__(self, index):
        if self._total <= 0:
            return []
        elif index >= self._total:
            return self._results[self._total-1]
        else:
            return self._results[index]
