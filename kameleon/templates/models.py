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

import databases
from model import fields, Model, BaseModel
"""
------------------------------ Config Information  -----------------------------

All information relative to the Database used.

"""

# Database name
db_name = "ORMdatabase"

# User name
user = "user"

# Password
password = "password"

DATABASE = databases.PostgresqlDatabase(db_name, user=user, password=password)

"""
------------------------------ Exported Class  ---------------------------------

Models classes definitions

"""

__all__ = ["Test1", "Test2"]

class Test1(Model):
    class Meta:
        database = DATABASE

    code = fields.CharField(max_length=50)
    user_id = fields.IntegerField()

class Client2(Model):
    class Meta:
        database = DATABASE

    code = fields.CharField(max_length=50)
    user_id = fields.IntegerField()
