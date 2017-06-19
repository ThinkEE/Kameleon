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




#############################*****************##################################
"""
                            Not up to date. See postgresql
"""
#############################*****************##################################

from twisted.internet.defer import inlineCallbacks, returnValue

from base import Database

class MysqlDatabase(Database):

    DB_API_NAME = "MySQLdb"

    JOIN = "JOIN"
    LEFT_JOIN = "LEFT JOIN"

    TYPES = {
        'BOOL': 'bool',
        'CHAR': 'varchar',
        'FLOAT': 'float',
        'INT': 'int',
        'DATE': 'timestamp'
    }

    # def _connect(self, **kwargs):
    #     from twisted.enterprise import adbapi
    #
    #     class ReconnectingConnectionPool(adbapi.ConnectionPool):
    #         """Reconnecting adbapi connection pool for MySQL.
    #
    #         This class improves on the solution posted at
    #         http://www.gelens.org/2008/09/12/reinitializing-twisted-connectionpool/
    #         by checking exceptions by error code and only disconnecting the current
    #         connection instead of all of them.
    #
    #         Also see:
    #         http://twistedmatrix.com/pipermail/twisted-python/2009-July/020007.html
    #
    #         (2006: MySQL server has gone away
    #          2013: Lost connection to MySQL server
    #          1213: Deadlock found when trying to get lock)
    #         """
    #         def _runInteraction(self, interaction, *args, **kw):
    #             from MySQLdb import OperationalError
    #
    #             try:
    #                 return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
    #             except OperationalError, e:
    #                 if e[0] not in (2006, 2013, 1213):
    #                     raise
    #                 print("ERROR: %s got error %s, retrying operation" % (self.__class__.__name__, e))
    #                 conn = self.connections.get(self.threadID())
    #                 self.disconnect(conn)
    #                 # try the interaction again
    #                 return adbapi.ConnectionPool._runInteraction(self, interaction, *args, **kw)
    #
    #     self.connection = ReconnectingConnectionPool(self.DB_API_NAME, db=self.name, host=kwargs['host'], user=kwargs['user'], passwd=kwargs['password'])
    #
    # def _close(self, *args):
    #     print("INFO: Connection close cleanly")
    #
    # @inlineCallbacks
    # def runOperation(self, operation):
    #     print("Run Operation ", operation)
    #     try:
    #         yield self.connection.runOperation(operation)
    #     except Exception as err:
    #         print("ERROR: Running operation %s" %operation)
    #         print(err)
    #
    # @inlineCallbacks
    # def runQuery(self, query):
    #     print("Run Query ", query)
    #     answer = []
    #     try:
    #         answer = yield self.connection.runQuery(query)
    #     except Exception as err:
    #         print("ERROR: Running query %s" %query)
    #         print(err)
    #         # Return special values if error. The code should be able to know
    #     returnValue(answer)
    #
    # def generate_insert(self, query):
    #
    #     keys = ",".join([unicode(x) for x in query.values.keys()])
    #     values = ",".join([unicode(x) for x in query.values.values()])
    #
    #     str_query = ("INSERT INTO {0} ({1}) VALUES ({2})"
    #                 .format(query.model_class._meta.table_name, keys, values))
    #
    #     if query.on_conflict:
    #         str_query += (" ON CONFLICT ({0}) DO UPDATE SET ({1}) = ({2})"
    #                      .format(",".join(query.on_conflict), keys, values))
    #
    #     if query.return_id:
    #         str_query += " RETURNING id"
    #
    #     str_query += ";"
    #     return str_query
    #
    # def query(self, queryInstance):
    #     target = '*' or queryInstance.params
    #
    #     joint = ""
    #     # if queryInstance._joins:
    #     #     for join in queryInstance._joins:
    #     #
    #     #         # XXX To Do: Implement other join type
    #     #         joint_type = join.joint_type
    #     #         if joint_type == self.JOIN:
    #     #             joint_type = self.JOIN
    #     #         else:
    #     #             joint_type = self.LEFT_JOIN
    #     #
    #     #         if join.dest in join.src._meta.rel_class and join.src.isForeignKey(join.src._meta.rel_class[join.dest]):
    #     #             clause1 = "%s.%s"%(join.src._meta.table_name, join.src._meta.rel_class[join.dest].name)
    #     #             clause2 = "%s.%s"%(join.dest._meta.table_name, join.src._meta.rel_class[join.dest].reference.name)
    #     #
    #     #         elif join.src in join.dest._meta.rel_class and join.dest.isForeignKey(join.dest._meta.rel_class[join.src]):
    #     #             clause1 = "%s.%s"%(join.src._meta.table_name, join.dest._meta.rel_class[join.src].reference.name)
    #     #             clause2 = "%s.%s"%(join.dest._meta.table_name, join.dest._meta.rel_class[join.src].name)
    #     #
    #     #         else:
    #     #             raise Exception("Logic error")
    #     #
    #     #         joint += "%s %s on (%s = %s) "%(joint_type, join.dest._meta.table_name, clause1, clause2)
    #
    #     where=''
    #     if queryInstance._where:
    #         i = 0
    #         for value in queryInstance._where:
    #             if i == 0:
    #                 con = "WHERE "
    #             else:
    #                 con = " AND "
    #             where += "%s %s.%s %s '%s'"%(con, queryInstance.model_class._meta.table_name, value.lhs.name, value.op, value.rhs)
    #             i+=1
    #
    #     end = ";"
    #     if queryInstance._delete:
    #         queryType = "DELETE"
    #         if queryInstance.model_class._meta.primary_key:
    #             end = " RETURNING id;"
    #     else:
    #         queryType = "SELECT %s" %(target)
    #
    #     query = '%s FROM %s %s %s%s' %(queryType, queryInstance.model_class._meta.table_name, joint, where, end)
    #     # print(query)
    #     return query
