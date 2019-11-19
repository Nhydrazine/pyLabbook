# pyLabbook Project

The goal of the pyLabbook project is to provide free, transparent and open source tools that scientists can use to manage and process their data.  

pyLabbook achieves this goal as a python-based, minimal data management system (mDMS).  This system is designed to be extended by individual scientists and small to medium sized laboratories with data structures and methods that are relevant their research.

There are three levels of extension that involve different levels of programming skills:

1. The **manager interface** allows non-python users to use pyLabbook as a customizable DMS, where you can:
  * define custom data structures
  * use pyLabbook to help plan and structure your experiments
  * store and retrieve your data
  * transfer and export your data


2. For users who know some python, the core **pyLabbook** and **pyProtocol** modules can be extended to add custom properties and methods to data structures that:
  * perform recipe calculations
  * workup your data
  * perform model fitting and analysis
  * generate batch reports on data
  * interact with other data structures


3. For users who know python and are used to working with databases, the **SQLEngine** class can be extended with complex database operations and queries.

# Usage

## What You Need
You need python 3.6+ and the python packages numpy, pandas, xlrd, openpyxl and sqlite3.  To use the manager GUI you will also need tkinter, which is included by most contemporary python installers.

## How to Download pyLabbook
We will provide a download link at some point.  Presently, you can download pyLabbook by cloning this repository.  If your python version and modules are up to date, you can immediately start using pyLabbook.

## Testing pyLabbook
Run the **testme.py** script by:
1. Open a terminal window
2. Go to the folder containing your pyLabbook distribution using `cd`
3. run the test script with `python testme.py`

The output will tell you whether your python and modules are sufficient.

## How to Use pyLabbook
### Manager GUI
The tkinter-based manager interface **manager.py** provides a simple way to use the basic DMS functionality of pyLabbook.  Run from the command line by:

1. Open a terminal window
2. Go to the folder containing your pyLabbook distribution using `cd`
3. Run the manager script with `python manager.py`

More detailed instructions are available in the manager documentation.

### Command-line Functions
The **scripts** folder contains python scripts that can be run from the command-line to perform various DMS related operations.  To extend this functionality, modify the existing scripts, use them as a template, or create your own.

The **scripts** folder is also intended for other command-line scripts that activating report generators and other **pyProtocol** customizations.

## How to Extend pyLabbook

### Core Design
pyLabbook is composed of two objects **labbooks** (the `pyLabbook.pyLabbook` class) and **protocols** (the `pyLabbook.pyProtocol` class).  Labbooks specify *where the data is located* on a hard drive and involve both a **database**, for long term storage and bulk access, and a **spreadsheet repository**, for short-term access and data entry.  Protocols specify *the structure of the data* through table column definitions that are used to define the labbook databases and spreadsheets.  This design allows data to be fluidly transferred, organized, and reorganized across labbooks without losing its fundamental structure.

A **protocol** represents the information input/output of an experimental procedure as a table.  The `pyLabbook.pyProtocol` class includes a minimal architecture that is necessary to maintain essential relationships and identities in your data.  This minimal architecture is extended by adding table column definitions that are specific to the protocol.

The **minimal architecture** of a protocol involves four hierarchical id columns that reflect the way experiments are organized.  These id's are always formatted as string values and allow A-Z, a-z, 0-9, _ and - but not spaces.  The meaning of these id's are given in the context of a standard dose-effect experiment, where the effect of a drug is measured across a range of concentrations.

* **experiment_id** is the highest level within a protocol and identifies the experiment that was performed.  In the context of a dose-effect protocol, an experiment may involve measuring multiple dose-effect curves under various conditions.

* **set_id** identifies a cohesive group of measurements.  In the context of a dose-effect protocol, a set includes all of the measurements for a single dose-effect curve.  These measurements are related by a common set of experimental conditions.

* **sample_id** identifies individual measurements.  In the context of a dose-effect protocol, each measurement on a dose-effect curve is a sample.

* **replicate** can be used to distinguish between replicate measurements of a single sample.

These id's are used to **store protocol data** across two tables: a **set table** that describes the experimental conditions of each set, and a **sample table** that contains experimental measurements.  This design ensures that complex and possibly dense information that describes experimental conditions is not duplicated across a large volume of measurements.

The **minimal architecture** of the `pyLabbook.pyProtocol` class consists of a **set table** that is keyed by experiment_id and set_id, and a **sample table** that is keyed by experiment_id, set_id, sample_id and replicate number.  Sets and samples are linked by shared experiment_id/set_id values.  This creates the following constraints:

1. **For a protocol, every experiment id must be unique**.  I recommend using a date, followed by a number of letter if multiple experiments are performed on the same day.  I recommend YYYYMMDD format because it is sortable and isn't autoformatted by spreadsheet software.

2. **For an experiment, every set id must be unique**.  You may repeat set id's across experiments, but all set id's associated with a specific experiment id must be distinct.  A simple sequential numeric scheme will work.

3. **For a set, every sample id must be unique**.  A sequential numeric scheme works here too.

4. **For a sample, every replicate number must be unique**.  Numeric works.  If you don't perform multiple measurements on a sample then use `1` for all samples.

Experiment id's are specified when initializing a new experiment, while set, sample and replicate id's are specified during data entry.  

## Create a Labbook by Extending pyLabbook.pyLabbook
Labbooks specify where data is stored and incldue a database, for long-term storage and bulk access, as well as a spreadsheet repository for data entry and temporary access.  A labbook is an instance of the `pyLabbook.pyLabbook` class where the folder/path properties are specific to the labbook instance.

Labbooks are stored in the **python/pyLabbook/labbooks/** folder.  An example labbook, called myLabbook.py, is shown:


```
# import pyLabbook class
from pyLabbook import pyLabbook;

# define an initialization function that takes the path of
# pyLabbook distribution as argument (root)
def initialize(root):

  # create instance of pyLabbook with specific values
  plb = pyLabbook(

    # id must match the file base name (without .py extension)
    id="myLabbook",

    # root path of pyLabbook distribution
    root=root,

    # path to spreadsheet repository fodler
    repositoryPath="repositories/myLabbook",

    # format for spreadsheets, "csv" or "xlsx" only for now
    sheetFormat="csv",

    # path to database file
    databasePath="databases",

    # name of database file including extension
    databaseFile="myLabbook.sqlite3",

    # format for database file, currently only "SQLITE3"
    databaseFormat="SQLITE3",
	);

  # return the modified pyLabbook instance
	return plb;
```

It is convention to name the repository path and database file after the labbook id, and to name the labbook id after the name of the python file for the labbook.  This convention will help keep your data and repositories organized.

Labbooks can also be created using the manager interface, which automatically generates to associated pyLabbook python file.

### Create a Protocol by Extending pyLabbook.pyProtocol
Protocols are extensions of the `pyLabbook.pyProtocol` class that, at the very least, specify table columns.  Protocols are stored in the **python/pyLabbook/protocols** folder.

The following is an example protocol that specifies one column for its set table, and one column for its sample table, called myProtocol.py:

```
# import pyProtocol class
from pyLabbook import pyProtocol;

# define a class called initialize, that extends pyProtocol
class initialize(pyProtocol):

  # define a setup function that specifies table columns
  # argument s is a reference to this protocol object.
  def setup(s):

    # set the ID of this protocol, named after file base
    s.PROTOCOLID = "myProtocol";

    # add a column to set table using addSetColumn() method
    # of this protocol
    s.addSetColumn(

      # name of the field
      name        = "subject",

      # data type for field
      type        = "TEXT",

      # can the field be empty? (True or False)
      notnull     = True,

      # does the field always have to contain a unique value?
      unique      = False,

      # describe the field
      description = "id of the subject being experimented on",

      # default value for field, if no value supplied
      default     = None,

      # is the field a primary key? (compounded with others)
      primary_key = False,
    );

    # add a column to sample table usins addSamColumn() method
    # of this protocol
    s.addSamColumn(
      name        = "value", # name of field
      type        = "REAL",  # REAL is a number
      notnull     = True,    # must always have a value
      unique      = False,   # doesn't need to be unique
      description = "measured value",
      default     = None,    # no default
      primary_key = False,   # not a primary key
    );
```

The `addSetColumn()` and `addSamColumn()` methods require you to specify all properties of each field:

* **name**: the name of the field, restricted to A-Z, a-z, 0-9, _ and -, no spaces.
* **type**: the data type for field.  "TEXT", "REAL", "INTEGER", "NUMBER" and "DATE" are currently available.  There is no difference between "REAL" and "NUMBER".
* **notnull**: True or False - can the field be empty?
* **unique**: True or False - does the field value need to be unique among all other values in this field?
* **description**: A brief description of the field and its contents.
* **primary_key**: True or False - include this field in compound primary key that already exists?  Use False if you're not sure what a compound primary key is.

Protocols can also be created using the manager interface, which automatically generates the associated pyProtocol python file.

# Python Programming Interface
The `pyLabbook.pyLabbook` and `pyLabbook.pyProtocol` classes also carry methods and properties that are used to locate, retrieve, store and manipulate your data.  These methods and properties create an interface that allows you to build python scripts that work with your data, without having to worry about the details of database queries and formatting.  To access these methods you will need to import the labbook(s) and protocol(s) you want to work with, and initialize them.  The following is a minimal example that connects a labbook and protocol.

```
import sys;

# specify path to pyLabbook distribution folder
pyLabbookRoot = os.path.join('path','to','pyLabbook','distribution');

# specify path to pyLabbok python folder
pyLabbookPythonRoot = os.path.join( pyLabbookRoot, 'python' );

# add pyLabbook python folder to your import path
sys.path.append(pyLabbookPythonRoot);

# import your labbook and protocol
import pyLabbook.labbooks.myLabbook;
import pyLabbook.protocols.myProtocol;

# initialize your labbook to your pyLabbook distribution using pyLabbookRoot
labbook = pyLabbook.labbooks.myLabbook.initialize(pyLabbookRoot);

# initialize protocol using the labbook
protocol = pyLabbook.protocols.myProtocol.initialize(labbook);

# connect protocol to labbook's database
protocol.connect();

# create protocol tables in labbook's database if not there already
protocol.createTables();

# do some stuff
# do more stuff

# disconnect protocol from database
protocol.disconnect();

# end
```

See the `pyLabbook.pyLabbook` and `pyLabbook.pyProtocol` classes for documentation on the methods that are available and how to use them.  See the examples documentation or python scripts in the **scripts/** folder for examples and additional information.

# Contribution
We welcome contributions! Documentation of standards are currently being developed.



.
