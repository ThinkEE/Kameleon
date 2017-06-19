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

import fields, collections, bcrypt

from twisted.internet.defer import inlineCallbacks, returnValue

from fields import PrimaryKeyField
from query import SelectQuery, \
                  InsertQuery, \
                  AddQuery, \
                  RemoveQuery, \
                  UpdateQuery, \
                  DeleteQuery

"""
Metaclass enables to have a set of variable for each class Model.
This set of variable is represented by the class ModelOptions
"""
_METACLASS_ = '_metaclass_helper_'
def with_metaclass(meta, base=object):
    return meta(_METACLASS_, (base,), {})

class ModelOptions(object):
    """
    Represents all the options associated to a model.
    They are accesible using the _meta variable from a Model object
    """
    def __init__(self, cls,
                table_name = None,
                database = None,
                primary_key = True,
                on_conflict = [],
                unique = [],
                many_to_many = False,
                order = [],
                propagate = False):

        # Model class
        self.model_class = cls

        # Model name
        self.name = cls.__name__.lower()

        # Table name. Either set by the user or derivated from name
        self.table_name = table_name.lower() if table_name else self.name

        # Database to use
        self.database = database

        # Does the models have a primary key. If so it will be set by Kameleon
        self.primary_key = primary_key

        # XXX
        self.on_conflict = on_conflict

        # List of field which association should be unique.
        # XXX #3 Today it receive a string.
        # It should be receiving a list of fields
        self.unique = unique

        # Is this model a middle table for a many to many link
        self.many_to_many = many_to_many
        # Map of links represented by this table. Filled by the class
        self.links = {}

        # Order to respect. Useful if table not created by the ORM
        self.order = order

        # Should any change on a model be propagate
        self.propagate = propagate

        # Map of fields
        self.fields = {}

        # Map of reverse relation fields
        self.reverse_fields = {}

        # List of fields sorted in order
        self.sorted_fields = []
        # Fields name sorted in order
        self.sorted_fields_names = []

        # Map of direct relation
        self.rel = {}

        # Map of reverse relation
        self.reverse_rel = {}

        # Map of related classes and the field associated
        self.rel_class = {}

    def add_field(self, field):
        """
        Add a field to the class. It makes sure all related variables are
        up to date
        """
        if field.name in self.fields:
            print("WARNING: Field {0} already in model {1}"
                  .format(field.name, self.table_name))
            return

        self.fields[field.name] = field
        self.sorted_fields.append(field)
        self.sorted_fields_names.append(field.name)

class BaseModel(type):
    """
    Metaclass for all models.
    """

    def __new__(cls, name, bases, attrs):
        if name == _METACLASS_ or bases[0].__name__ == _METACLASS_:
            return super(BaseModel, cls).__new__(cls, name, bases, attrs)

        # Get all variable defined in the meta class of each model.
        meta_options = {}
        meta = attrs.pop('Meta', None)
        if meta:
            for k, v in meta.__dict__.items():
                if not k.startswith('_'):
                    meta_options[k] = v

        # Create Model class and its options
        cls = super(BaseModel, cls).__new__(cls, name, bases, attrs)
        cls._meta = ModelOptions(cls, **meta_options)

        # If many to many initialize the links between the two tables.
        if cls._meta.many_to_many:
            links = []
            if cls._meta.order:
                for attr in cls._meta.order:
                    if attr in attrs:
                        links.append((attr, attrs[attr]))
            else:
                for key, value in attrs.items():
                    if not key.startswith('_'):
                        links.append((key, value))

            links[0][1].related_name = links[1][0]
            links[0][1].add_to_model(cls, links[0][0])

            links[1][1].related_name = links[0][0]
            links[1][1].add_to_model(cls, links[1][0])

        # Else it is a basic model.
        else:
            # If primary key
            if cls._meta.primary_key:
                # Create primary key field
                cls.id = fields.PrimaryKeyField()
                # Add field to the model
                cls.id.add_to_model(cls, PrimaryKeyField.name)

            # Add each field to the model
            if cls._meta.order:
                for attr in cls._meta.order:
                    if attr in attrs:
                        attrs[attr].add_to_model(cls, attr)
            else:
                for key, value in attrs.items():
                    if not key.startswith('_'):
                        value.add_to_model(cls, key)

        return cls

class Model(with_metaclass(BaseModel)):
    """
    Represents a model in the database with all its fields and current values
    """

    def __init__(self, **kwargs):
        # Map of all fields and associated values
        self.dictValues = {}

        # Initialize each field. If no value set it to None
        for k, v in self._meta.fields.items():
            if k in kwargs:
                self.dictValues[k] = kwargs[k]
                setattr(self, k, kwargs[k])
            else:
                self.dictValues[k] = None
                setattr(self, k, None)

        # Set primary key to None if no value provided
        if self._meta.primary_key and not "id" in self.dictValues:
            self.dictValues["id"] = None
            object.__setattr__(self, "id", None)

        # Initialize reverse relation as empty list.
        for field in self._meta.reverse_rel:
            object.__setattr__(self, field, [])

        if self._meta.database.subscribe:
            self._meta.database.connection.subscribe(self.propagate_update, u"wamp.postgresql.propagadate.{0}".format(self._meta.name))

    def __setattr__(self, name, value):
        """
        Overide __setattr__ to update dict value and field value at once
        """
        object.__setattr__(self, name, value)

        if name in self.dictValues: # If updating a field value
            if self._meta.fields[name].salt: # field is salt
                # If field is already salt do nothing.
                # XXX Could create a security issue. What happend is value
                # starts with $2b$ but it's not encrypted. Not critical for now
                if not ("$2b$" in value and value[:4] == "$2b$"):
                    value = bcrypt.hashpw(value.encode('utf8'), bcrypt.gensalt())
                    object.__setattr__(self, name, value)

            # If value is an instance of model class and has a relation.
            # Append it to the corresponding field list
            if hasattr(value, "_meta") and self.isForeignKey(self._meta.fields[name]):
                self.dictValues[name] = getattr(value, self._meta.fields[name].reference.name)
                return

            self.dictValues[name] = value

    @classmethod
    def isForeignKey(cls, _field):
        """
        Is the field an instance of ForeignKeyField
        """
        return isinstance(_field, fields.ForeignKeyField)

    @classmethod
    def isReferenceField(cls, _field):
        """
        Is the field an instance of ReferenceField
        """
        return isinstance(_field, fields.ReferenceField)

    @classmethod
    @inlineCallbacks
    def create_table(cls, *args, **kwargs):
        """
        Creates a table in the database.
        """
        init = cls._meta.database.create_table_title(cls._meta.table_name)
        i = 1
        fields = zip(cls._meta.sorted_fields_names,  cls._meta.sorted_fields)
        for field in fields:
            field_string = field[1].create_field(field[0])
            if i == len(fields):
                if cls._meta.unique:
                    init = cls._meta.database.create_unique(init, cls._meta.unique)
                init = cls._meta.database.create_table_field_end(init, field_string)
            else:
                init = cls._meta.database.create_table_field(init, field_string)
            i+=1

        yield cls._meta.database.runOperation(init)

    @classmethod
    @inlineCallbacks
    def delete_table(cls, *args, **kwargs):
        """
        Deletes table from database
        """
        operation = cls._meta.database.delete_table(cls._meta.table_name)
        yield cls._meta.database.runOperation(operation)

    @classmethod
    @inlineCallbacks
    def insert(cls, values):
        """
        Insert a row to the table with the given values
        """
        result = yield InsertQuery(cls, values).execute()
        returnValue(result)

    @classmethod
    @inlineCallbacks
    def update(cls, values):
        """
        Update values in row
        """
        result = yield UpdateQuery(cls, values).execute()
        returnValue(result)

    @classmethod
    @inlineCallbacks
    def create(cls, **kwargs):
        """
        Instanciates a model class object and save it into the database.
        """
        inst = cls(**kwargs)
        yield inst.save()
        returnValue(inst)

    @classmethod
    def all(cls):
        """
        Get all rows from a table
        """
        return SelectQuery(cls)

    @classmethod
    @inlineCallbacks
    def add(cls, obj1, obj2):
        """
        Add a link between two model
        """
        if not cls._meta.many_to_many:
            raise Exception("ERROR: Add called on non many to many model")

        query = AddQuery(cls, obj1, obj2)
        yield query.execute()

        if not getattr(obj1, obj2._meta.name):
            setattr(obj1, obj2._meta.name, [obj2])
        else:
            getattr(obj1, obj2._meta.name).append(obj2)

        if not getattr(obj2, obj1._meta.name):
            setattr(obj2, obj1._meta.name, [obj1])
        else:
            getattr(obj2, obj1._meta.name).append(obj1)


    @classmethod
    @inlineCallbacks
    def remove(cls, obj1, obj2):
        """
        Remove a link between two model
        """
        if not cls._meta.many_to_many:
            raise Exception("ERROR: Remove called on non many to many model")

        query = RemoveQuery(cls, obj1, obj2)
        yield query.execute()

        if obj2 in getattr(obj1, obj2._meta.name):
            getattr(obj1, obj2._meta.name).remove(obj2)

        if obj1 in getattr(obj2, obj1._meta.name):
            getattr(obj2, obj1._meta.name).remove(obj1)

    @classmethod
    def delete(cls):
        """
        Delete a row in the database
        """
        query_instance = DeleteQuery(cls)
        return query_instance

    @inlineCallbacks
    def save(self):
        """
        Save a row
        """
        # For each field get the value to insert
        values = {key : self._meta.fields[key].insert_format(value) for key, value in self.dictValues.items()}
        if self._meta.primary_key:
            # If an id exist then we should update
            if self.id:
                pk = yield self.update(values)
                if self._meta.propagate:
                    self._meta.database.propagate(self)

            # Else it means we should create the row
            else:
                # XXX To Do: What happen if insert failed. What should we return
                del values["id"]
                pk = yield self.insert(values)

            # Update id value
            self.id = pk
        else:
            yield self.insert(values)

    def propagate_update(self, dict_values):
        print("********* New value received for model", dict_values)
