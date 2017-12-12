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

from base import Field

MAX_LENGTH = 255

class CharField(Field):
    TYPE = 'CHAR'

    def __init__(self, max_length=MAX_LENGTH, *args, **kwargs):
        super(CharField, self).__init__(*args, **kwargs)
        self.max_length = max_length

    def get_db_field(self):
        if self.model_class._meta.database:
            return ("{0}({1})"
                    .format(self.model_class._meta.database.TYPES[self.TYPE],
                            self.max_length))

        return self.TYPE

    def create_field(self, name):
        field_string = ("{0} {1}({2})"
                        .format(name, self.model_class._meta.database.TYPES[self.TYPE], self.max_length))

        if self.unique:
            field_string += " UNIQUE"

        return field_string

    def insert_format(self, value):
        value = u"'{0}'".format(value)
        return value
