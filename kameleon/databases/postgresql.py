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

from base import Database

class PostgresqlDatabase(Database):

    JOIN = "JOIN"
    LEFT_JOIN = "LEFT JOIN"

    TYPES = {
        'BOOL': 'bool',
        'CHAR': 'varchar',
        'FLOAT': 'float',
        'INT': 'int',
        'JSON': 'jsonb',
        'DATE': 'timestamp'
    }

    def connectionError(self, f):
        print("ERROR: connecting failed with {0}".format(f.value))

    @inlineCallbacks
    def _connect(self, **kwargs):
        from txpostgres import txpostgres, reconnection
        from txpostgres.reconnection import DeadConnectionDetector

        class LoggingDetector(DeadConnectionDetector):

            def startReconnecting(self, f):
                print("ERROR: database connection is down (error: {0})"
                      .format(f.value))
                return DeadConnectionDetector.startReconnecting(self, f)

            def reconnect(self):
                print("INFO: Reconnecting...")
                return DeadConnectionDetector.reconnect(self)

            def connectionRecovered(self):
                print("INFO: connection recovered")
                return DeadConnectionDetector.connectionRecovered(self)

        self.connection = txpostgres.Connection(detector=LoggingDetector())
        d = self.connection.connect(host=kwargs['host'],
                                    database=self.name,
                                    user=kwargs['user'],
                                    password=kwargs['password'])
        d.addErrback(self.connection.detector.checkForDeadConnection)
        d.addErrback(self.connectionError)
        yield d
        print("INFO: Database connected -- %s" %self.name)

    @inlineCallbacks
    def _close(self, *args):
        try:
            if self.connection:
                yield self.connection.close()
        except Exception as err:
            print("ERROR: while closing DB connection")
            print(err)
        else:
            print("INFO: Connection close cleanly")

    @inlineCallbacks
    def runOperation(self, operation):
        try:
            yield self.connection.runOperation(operation)
        except Exception as err:
            print("ERROR: Running operation %s" %operation)
            print(err)

    @inlineCallbacks
    def runQuery(self, query):
        answer = []
        try:
            answer = yield self.connection.runQuery(query)
        except Exception as err:
            print("ERROR: Running query %s" %query)
            print(err)
            # Return special values if error. The code should be able to know
        returnValue(answer)

    def create_table_title(self, name):
        return "CREATE TABLE %s (" %(name)

    def create_table_field_end(self, current, field):
        return " %s %s);" %(current,field)

    def create_table_field(self, current, field):
        return " %s %s," %(current,field)

    def create_unique(self, current, unique):
        return " %s UNIQUE (%s)," %(current, ",".join(unique))

    def delete_table(self, table_name, cascade=True):
        operation = "DROP TABLE IF EXISTS %s"%(table_name)
        if cascade:
            operation += " CASCADE"

        operation +=";"
        return operation

    def generate_insert(self, query):

        keys = ",".join([x.encode("utf-8") for x in query.values.keys()])
        values = ",".join([x.encode("utf-8") for x in query.values.values()])

        str_query = ("INSERT INTO {0} ({1}) VALUES ({2})"
                    .format(query.model_class._meta.table_name, keys, values))

        if query.on_conflict:
            str_query += (" ON CONFLICT ({0}) DO UPDATE SET ({1}) = ({2})"
                         .format(",".join(query.on_conflict), keys, values))

        if query.return_id:
            str_query += " RETURNING id"

        str_query += ";"
        return str_query

    def generate_delete(self, query):

        where=''
        if query._where:
            i = 0
            if isinstance(query._where, str):
                where = "WHERE {0}".format(query._where)
            else:
                for value in query._where:
                    if i == 0:
                        con = "WHERE "
                    else:
                        con = " AND "
                    where += "%s %s.%s %s '%s'"%(con, value.lhs.model_class._meta.table_name, value.lhs.name, value.op, value.rhs)
                    i+=1

        query = 'DELETE FROM {0} {1};'.format(query.model_class._meta.table_name, where)
        return query

    def generate_update(self, query):

        if query.model_class._meta.primary_key:
            _id = query.values["id"]
            del query.values["id"]

        keys = ",".join([x.encode("utf-8") for x in query.values.keys()])
        values = ",".join([x.encode("utf-8") for x in query.values.values()])

        if query.model_class._meta.primary_key:
            str_query = ("UPDATE {0} SET ({1})=({2}) WHERE id = {3}"
                        .format(query.model_class._meta.table_name, keys, values, _id))
        else:
            # XXX To Do: If not id -> check if one of the field is Unique. If one is unique use it to update
            print("ERROR: Not primary key cannot update row. Need to be implemented")
            raise Exception("ERROR: Not primary key cannot update row. Need to be implemented")

        if query.return_id:
            str_query += " RETURNING id"

        str_query += ";"
        return str_query

    def generate_add(self, query):
        table_name = query.model_class._meta.table_name

        query = ("INSERT INTO {0} ({1}) SELECT {2} WHERE NOT EXISTS (SELECT {3} FROM {0} WHERE {3}='{5}' AND {4}='{6}');"
                .format(table_name,
                        ",".join(query.model_class._meta.sorted_fields_names),
                        ",".join([str(obj.id) for obj in query.objs]),
                        query.model_class._meta.sorted_fields_names[0],
                        query.model_class._meta.sorted_fields_names[1],
                        query.objs[0].id,
                        query.objs[1].id))
        return query

    def generate_remove(self, query):
        table_name = query.model_class._meta.table_name

        query = ("DELETE FROM {0} WHERE {1} = '{3}' AND {2}='{4}';"
                .format(table_name,
                        query.model_class._meta.sorted_fields_names[0],
                        query.model_class._meta.sorted_fields_names[1],
                        query.objs[0].id,
                        query.objs[1].id))

        return query

    def generate_select(self, queryInstance):
        target = '*'

        joint = ""
        if queryInstance._joins:
            for join in queryInstance._joins:

                # XXX To Do: Implement other join type
                joint_type = join.joint_type
                if joint_type == self.JOIN:
                    joint_type = self.JOIN
                else:
                    joint_type = self.LEFT_JOIN

                if join.dest in join.src._meta.rel_class and join.src.isForeignKey(join.src._meta.rel_class[join.dest]):
                    clause1 = "%s.%s"%(join.src._meta.table_name, join.src._meta.rel_class[join.dest].name)
                    clause2 = "%s.%s"%(join.dest._meta.table_name, join.src._meta.rel_class[join.dest].reference.name)

                elif join.src in join.dest._meta.rel_class and join.dest.isForeignKey(join.dest._meta.rel_class[join.src]):
                    clause1 = "%s.%s"%(join.src._meta.table_name, join.dest._meta.rel_class[join.src].reference.name)
                    clause2 = "%s.%s"%(join.dest._meta.table_name, join.dest._meta.rel_class[join.src].name)

                else:
                    raise Exception("Logic error")

                joint += "%s %s on (%s = %s) "%(joint_type, join.dest._meta.table_name, clause1, clause2)

        where=''
        if queryInstance._where:
            i = 0
            if isinstance(queryInstance._where, str):
                where = "WHERE {0}".format(queryInstance._where)
            else:
                where = queryInstance._where.parse()
                where = "WHERE {0}".format(where)

        end = ";"
        if queryInstance._delete:
            queryType = "DELETE"
            if queryInstance.model_class._meta.primary_key:
                end = " RETURNING id;"
        else:
            queryType = "SELECT {0}".format(",".join(target))

        query = ('{0} FROM {1} {2} {3}{4}'
                .format(queryType, queryInstance.model_class._meta.table_name,
                        joint, where, end))
        # print(query)
        return query

    def parse_select(self, query, result):
        class_list = []

        if query._joins:
            current = [None]*len(query._joins) + [None]
            models_class = {}
            rel = []
            pos = {}

            for res in result:
                start = len(query.model_class._meta.sorted_fields_names)
                curr_list = res[:start]
                i = 0

                if not models_class:
                    pos[query.model_class] = i
                    rel.append(None)

                if not str(curr_list) in models_class:
                    kwargs = dict(zip(query.model_class._meta.sorted_fields_names, curr_list))
                    last_model = query.model_class(**kwargs)
                    models_class[str(curr_list)] = {
                        "model": last_model
                    }
                    class_list.append(last_model)

                current[i] = models_class[str(curr_list)]

                for join in query._joins:
                    curr_list = res[start:start+len(join.dest._meta.sorted_fields_names)]

                    start += len(join.dest._meta.sorted_fields_names)
                    i += 1

                    if len(rel) == i:
                        pos[join.dest] = i
                        rel.append(pos[join.src])

                    if curr_list == [None]*len(join.dest._meta.sorted_fields_names):
                        current[i] = {
                            "model" : None
                        }
                        if not i in current[rel[i]]:
                            current[rel[i]][i] = {}

                        current[rel[i]][i]["None"] = current[i]
                        continue
                    else:
                        if not i in current[rel[i]] or not str(curr_list) in current[rel[i]][i]:
                            kwargs = dict(zip(join.dest._meta.sorted_fields_names, curr_list))
                            new_model = join.dest(**kwargs)
                            current[i] = {
                                "model" : new_model
                            }

                            if not i in current[rel[i]]:
                                current[rel[i]][i] = {}

                            current[rel[i]][i][str(curr_list)] = current[i]
                        else:
                            current[i] = current[rel[i]][i][str(curr_list)]
                            continue

                        current[i] = current[rel[i]][i][str(curr_list)]
                        new_model = current[i]["model"]

                        if join.src in pos:
                            if join.src._meta.many_to_many:
                                middle_table_index = rel[i]
                                index = pos[current[rel[i]]["model"].__class__]
                                x = getattr(new_model, current[rel[i]]["model"]._meta.rel_class[join.dest].related_name)
                                x.append(current[rel[index]]["model"])
                                x = getattr(current[rel[index]]["model"], current[rel[i]]["model"]._meta.rel_class[join.dest].name)
                                x.append(new_model)

                            elif not join.dest._meta.many_to_many:
                                if current[rel[i]]["model"].isForeignKey(current[rel[i]]["model"]._meta.rel_class[join.dest]):
                                    x = getattr(new_model, current[rel[i]]["model"]._meta.rel_class[join.dest].related_name)
                                    x.append(current[rel[i]]["model"])
                                    setattr(current[rel[i]]["model"], current[rel[i]]["model"]._meta.rel_class[join.dest].name, new_model)

                                elif current[rel[i]]["model"].isReferenceField(current[rel[i]]["model"]._meta.rel_class[join.dest]):
                                    x = getattr(current[rel[i]]["model"], current[rel[i]]["model"]._meta.rel_class[join.dest].name)
                                    x.append(new_model)
                                    setattr(new_model, current[rel[i]]["model"]._meta.rel_class[join.dest].related_name, current[rel[i]]["model"])
                                else:
                                    raise Exception("Here Logic error")

                        else:
                            raise Exception("Logic error")

        else:
            for res in result:
                kwargs = dict(zip(query.model_class._meta.sorted_fields_names, res))
                class_list.append(query.model_class(**kwargs))

        return class_list

    def propagate(self, model):
        print("WARNING: Ignoring propagate -- Function not set")
