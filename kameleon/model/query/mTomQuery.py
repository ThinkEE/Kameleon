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

class AddQuery(Query):
    """
    Add a many to many relation between to model. Works only on a many to many
    table.
    """
    def __init__(self, model_class, obj1, obj2):
        super(AddQuery, self).__init__(model_class)
        self.objs = [obj1, obj2]
        # Sort object as they are sorted in the table
        self.objs.sort(key=lambda x: self.model_class._meta.sorted_fields_names.index(x._meta.name))

    @inlineCallbacks
    def execute(self):
        # Execute only if the model is a middle table in a many to many
        # relation
        if self.model_class._meta.many_to_many:
            query = self.database.generate_add(self)
            yield self.database.runOperation(query)
        returnValue(None)

class RemoveQuery(Query):
    def __init__(self, model_class, obj1, obj2):
        super(RemoveQuery, self).__init__(model_class)
        self.objs = [obj1, obj2]
        self.objs.sort(key=lambda x: self.model_class._meta.sorted_fields_names.index(x._meta.name))

    @inlineCallbacks
    def execute(self):
        # Execute only if the model is a middle table in a many to many
        # relation
        if self.model_class._meta.many_to_many:
            query = self.database.generate_remove(self)
            yield self.database.runOperation(query)
        returnValue(None)
