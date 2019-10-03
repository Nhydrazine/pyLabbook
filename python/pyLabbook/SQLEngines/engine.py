import sys, os;
import numpy as np, pandas as pd;
################################################################################
# vvv THIS IS NOW HANDLED BY SQLEngines.manager vvv
#def loadSQLModule(format):
#    if format=='SQLITE':
#        return sqlite();
###   (TO ADD YOUR OWN SQL CLASS)
##   if format=='YOURFORMATNAME':
##       return yoursqlclass();
#    else:
#        raise Exception("Can't find SQL class for " + str(format) + ".");
################################################################################

################################################################################
# parent sql class, extend this.
class SQLEngine():
    def __init__(s):
        s.dmap = {
            'TEXT'      : {'py': str,   'db': 'TEXT'},
            'NUMERIC'   : {'py': float, 'db': 'NUMERIC'},
            'DATE'      : {'py': str,   'db': 'TEXT'},
            'INTEGER'   : {'py': int,   'db': 'INTEGER'},
            'REAL'      : {'py': float, 'db': 'REAL'},
        };
        s.dbh = None; # database handle
        s.ops = ['='];
        return;
    ############################################################################
    def sqr(s, sql, val, exe):
        """Returns a list containing a list of SQL, values and execution mode for database operations.  This is called an sqr.  An sqr serves as a queue of database operations that can be wrapped inside a ROLLBACK'able transaction.  A queue of database operations is a sum of sqrs, which is a list containing several SQL, value, execution mode lists.

        Parameters
        ----------
        sql : str
            The SQL code to be executed
        val : str, list or dict
            Values to accompany the SQL, such as values to be inserted.
        exe : str
            Execution mode or type.  For example, SQLITE3 accepts 'execute' and 'executemany'

        Returns
        -------
        list
            An sqr.  A list containing a single list of sql, val and exe.

        Example
        -------
        >>> from pyLabbook.SQLEngines.engine import SQLEngine;
        >>> import pyLabbook.SQLEngines.manager as manager;
        >>> sql = pyLabbook.SQLEngines.SQLITE3.engine();
        >>> queue = sql.sqr("SELECT * FROM TABLE", None, 'execute');
        >>> queue += sql.sqr("INSERT INTO TABLE VALUES (?,?)", ['value1','value2'],'execute');
        >>> queue += sql.sqr("INSERT INTO TABLE (col1, col1) VALUES (?,?)", [['row1val1','row1val2'],['row2val1','row2val2']],'executemany');
        """
        return [ [ sql, val, exe ] ];

    def printsqr(s, sqr):
        """displays the SQL from an sqr queue.

        Parameters
        ----------
        sqr : list
            A queue of sqrs (list of lists of [sql, values, execution mode]).

        Returns
        -------
        None

        """
        print( '\n'.join([ s[0] for s in sqr ]) );

    ############################################################################
    def connect(s,dbfile):
        """Connect to Database.

        Parameters
        ----------
        dbfile : str
            Full path and name of database file to connect to.

        Returns
        -------
        None

        """
        raise Exception("Method not defined.");

    def disconnect(s,commit=True):
        """Disconnect from database with explicit commit or not.

        Parameters
        ----------
        commit : boolean
            Explicitly commit before disconnecting (True or False).  If false,
            will explicitly rollback.

        Returns
        -------
        None

        """
        return;

    def rollback(s):
        return;

    def execute(s,dbh,sqr,transaction=True):
        """Execute a queue of sqrs.

        Parameters
        ----------
        dbh : database handle
            Database handle.
        sqr : list
            A queue of sqrs (list of lists of [sql, values, execution mode]).
        transaction : boolean
            If True, execute entire queue as a single transaction and rollback on error.

        Returns
        -------
        None

        """
        raise Exception("Method not defined.");

    def execute_select(s,sqr):
        """Execute a single element queue of sqrs with data to return (e.g. a queue to only one SELECT statement sqr).

        Parameters
        ----------
        sqr : list
            A queue of a single sqr (list of list of [sql, values, execution mode]) where the SQL is a SELECT statement that retreives data.

        Returns
        -------
        pandas.DataFrame
            A DataFrame of the results.

        """
        raise Exception("Method not defined.");

    ############################################################################
    def vq(s,v,delim='"'):
        """Value quote.  Quotes a value using delim.  This is used for string value quoting in SQL statements.  Raises Exception when value contains the delimeter.  This is primarily used by CREATE TABLE statement generators but may be used to quote INSERT values or WHERE clauses etc...

        Parameters
        ----------
        v : scalar
            Description of parameter `v`.
        delim : str
            The character(s) to quote the value with.

        Returns
        -------
        str
            The value quoted using delim.

        """
        if delim=="" or delim==None: return str(v);
        if delim not in str(v): return str(delim) + str(v) + str(delim);
        else: raise Exception("String contains delimeter " + str(delim));

    def hq(s,h,delim='`'):
        """Header quote.  Quotes a value using the quote delimeter for field names, table names etc... in SQL statements (typically a backtick).  This is used primarily by CREATE TABLE statement generators.  Raises Exception when field name contains delimeter.

        Parameters
        ----------
        h : str
            The field name.
        delim : str
            The delimeter to use, default is \` (backtick).

        Returns
        -------
        str
            The quoted value.

        """
        return s.vq(h,delim=delim);

    ############################################################################
    def buildwheres(s,data,desc):
        raise Exception("Method not defined.");

    ############################################################################
    def create_table(s,name,desc):
        raise Exception("Method not defined.");

    def drop_table(s,name):
        raise Exception("Method not defined.");

    def insert(s,name,data,desc,method='none'):
        raise Exception("Method not defined.");

    def delete(s,name,data,desc):
        raise Exception("Method not defined.");

    def select(s,name,data,desc):
        raise Exception("Method not defined.");

    def select_sql(s,sql):
        raise Exception("Method not defined.");

    def selectwith(s,name,withsql,desc):
        raise Exception("Method not defined.");
    def select_unique_experiment_ids(s,name):
        raise Exception("Method not defined.");
    def count_experiments_sets(s, name, data):
        raise Exception("Method not defined.");
    ############################################################################
    def cast(s,v,t,delim='"'):
        """Casts a value to the appropriate data type and quotes if applicable."""
        # Return None for null pandas types
        if pd.isnull(v):
            return None;
        if t in list(s.dmap.keys()):
            # cast value by passing it to the native python datatype function reference in dmap.
            try: cast_value = s.dmap[t]['py'](v);
            except:
                cast_value = None;
                raise Exception("cannot cast "+str(v)+
                    " as "+str(s.dmap[t]['py']));
            # if it's a string-type instance then quote it
            if isinstance(cast_value,str): return s.vq(cast_value, delim=delim);
            else: return cast_value;
        else: raise Exception("Unknown data type " + str(t) + ".");

    def nativetype(s,data,desc):
        """Converts a table data from a pandas.DataFrame into a list of lists of native python data types using a description DataFrame of the table."""
        # list of lists of converted values
        values = [];
        # get just the name and type for fields
        field_types = desc[['name','type']];
        # for every row in the data
        for i,r in data.iterrows():
            # initialize a list for this row of converted values
            value_row = [];
            # for every field that we know about
            for fi,fr in field_types.iterrows():
                # add the converted value to row list
                value_row.append(s.cast( r[fr['name']], fr['type'], delim="" ));
            # when done with a row, add it to the list of lists
            values.append(value_row);
        # return the converted list of lists
        return values;
################################################################################
    def select_experiment_report(s,settab,samtab):
        raise Exception("Method not defined.");
################################################################################





















################################################################################
