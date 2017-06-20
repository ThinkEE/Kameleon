# Kameleon

Kameleon is a small async ORM built over Twisted.

* Small ORM
* Written in python with support for versions 2.6+
* Built-in support for Postgresql

## Examples

### Layout

```
from twisted.internet.defer import inlineCallbacks, returnValue

import databases
from model import fields, Model, BaseModel

db_name = "ORMdatabase" # Database name

user = "user" # User name

password = "password" # Password

DATABASE = databases.PostgresqlDatabase(db_name, user=user, password=password)

__all__ = ["Test1"]

class Test1(Model):
    class Meta:
        database = DATABASE

    code = fields.CharField(max_length=50)
    user_id = fields.IntegerField()
```

### Usage

```
test1s = yield (baseModels.Test1.all()
              .where((baseModels.Test1.code == "code1") | (baseModels.Test1.code == "code2"), baseModels.Test1.user_id == 1 ).execute())

if test1s[0]:
    for test in test1s:
        print(test.dictValues)
```
## Installation

### Set up the environment

* Virtualenv
  * Install virtualenv
  * Create virtualenv `virtualenv Kameleon`
  * Go to environment `cd Kameleon`
  * Activate it `source bin/activate`

* Clone [repository](https://github.com/ThinkEE/Kameleon.git) `git clone https://github.com/ThinkEE/Kameleon.git`
* Go to folder `cd Kameleon`

### Install dependencies

* Run `pip install -r requirements.txt`

### Run code

You can run the templates in order to test it `python run_templates.py`
There are two different commands you can us:
  * `python run_templates.py --reset` Resets the Database
  * `python run_templates.py --create` Creates tables
