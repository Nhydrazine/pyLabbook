# Creating Protocols

## Sample Protocol
The following is a protocol python file for the protocol `someProtocol` stored in python/pyLabbook/protocols/someProtocol.py:

```
# import parent/base pyProtocol class
from pyLabbook import pyProtocol;

# define class called initialize, as extension of pyProtocol class
class initialize(pyProtocol):

  # define setup method which customizes this protocol
  # s is a copy of this protocol's instance
  def setup(s):

    # specify protocol ID, matches file base name by convention
    s.PROTOCOLID = "someProtocol";

    # specify field for set table
    s.addSetColumn(
      name        = "subject",
      type        = "TEXT",
      notnull     = True,
      unique      = False,
      description = "id or name of the subject being tested",
      default     = None,
      primary_key = False,
    );

    # specify field for sample table
    s.addSamColumn(
      name        = "value",
      type        = "REAL",
      notnull     = True,
      unique      = False,
      description = "measured value",
      default     = None,
      primary_key = False,
    );
```

Each set and sample column is defined using the addSetColumn() and addSamColumn() methods.  Columns are specified with the following keyword properties:

* **name**: the name of the field.  A-Z, a-z, 0-9, _ and - are allowed characters.
* **type**: data type for column - 'TEXT' (string of any length), 'REAL' (floating point), 'INTEGER', 'NUMERIC' (resembles 'REAL') or 'DATE' (resembles 'TEXT').
* **notnull**: True if field can contain unspecified `null` values, False if this field must always contain a value for every row.
* **unique**: True if only unique values are allowed for this column, False to allow repeated values across rows, for this column.
* **description**: a text description of the column and/or its values.
* **primary_key**: should this column be included as a primary key in the compound keys that already exist (experiment_id, set_id, sample_id, replicate, as necessary)?  True or False.  If you're not sure what a compound primary key is, use False.

## Extending With Custom Methods
You can add a custom method to your protocol by simply `def`ining it in the same way that the `setup()` method is defined in the sample protocol above.  For example:

```
# import parent/base pyProtocol class
from pyLabbook import pyProtocol;

# define class called initialize, as extension of pyProtocol class
class initialize(pyProtocol):

  # define setup method which customizes this protocol
  # s is a copy of this protocol's instance
  def setup(s):

    # specify protocol ID, matches file base name by convention
    s.PROTOCOLID = "someProtocol";

    # specify field for set table
    s.addSetColumn(
      name        = "subject",
      type        = "TEXT",
      notnull     = True,
      unique      = False,
      description = "id or name of the subject being tested",
      default     = None,
      primary_key = False,
    );

    # specify field for sample table
    s.addSamColumn(
      name        = "value",
      type        = "REAL",
      notnull     = True,
      unique      = False,
      description = "measured value",
      default     = None,
      primary_key = False,
    );

  # MY CUSTOM METHOD
  def customMethod(s,other,arguments):
    # connect to database
    s.connect();

    # do some stuff here

    # disconnect fmo database
    s.disconnect();

    return None;

```

As always, `s` is a copy of the protocol instance and includes all of the methods of the parental `pyLabbook.pyProtocol` class, including database/repository accessor methods.  

You may assume that a **labbook is linked** to your protocol when your custom methods are called.  

You will **not know whether the database has been connected** to or not.  It is convention to open the database connection at the beginning of a custom method, and close it at the end or on errors.

Call your custom method in python scripts that you create.  The scripts folder is specifically intended to house these scripts.
