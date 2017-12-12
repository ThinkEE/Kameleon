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
from primaryKeyField import PrimaryKeyField
from referenceField import ReferenceField

class ForeignKeyField(Field):

    def __init__(self, rel_model, reference=None, related_name=None, on_delete=False, on_update=False, *args, **kwargs):
        super(ForeignKeyField, self).__init__(*args, **kwargs)

        self.rel_model = rel_model
        self.reference = reference or rel_model._meta.fields["id"]
        self.related_name = related_name
        self.on_delete = on_delete
        self.on_update = on_update

    def add_to_model(self, model_class, name):
        self.name = name
        self.model_class = model_class

        self.related_name = self.related_name or "%ss"%(model_class._meta.name)

        model_class._meta.add_field(self)

        if self.related_name in self.rel_model._meta.fields:
            print("ERROR: Foreign key conflict")

        if self.related_name in self.rel_model._meta.reverse_rel:
            print("ERROR: Foreign key %s already exists on model %s"%(self.related_name, model_class._meta.name))

        self.model_class._meta.rel[self.name] = self
        self.model_class._meta.rel_class[self.rel_model] = self

        reference = ReferenceField(self.model_class)
        reference.add_to_model(self.rel_model, self.related_name, self.name)

    def create_field(self, name):
        _type = self.reference.get_db_field()
        field_string = "%s %s REFERENCES %s(%s)" %(self.name, _type, self.rel_model._meta.table_name, self.reference.name)

        if self.on_delete:
            field_string += " ON DELETE CASCADE"

        if self.on_update:
            field_string += " ON UPDATE CASCADE"

        if self.unique:
            field_string += " UNIQUE"

        return field_string

    def insert_format(self, value):
        value = u"'{0}'".format(value)
        return value
