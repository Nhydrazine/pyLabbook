import sys;
import sqlite3;
import numpy as np, pandas as pd;
from pyLabbook.SQLEngines.engine import SQLEngine;
# interits implementation from SQLEngines.engine.SQLEngine class
class engine(SQLEngine):
    def __init__(s):
        s.dbh = None;
        # data types map
        s.dmap = {
            'TEXT'      : {'py': str,   'db': 'TEXT'},
            'NUMERIC'   : {'py': float, 'db': 'NUMERIC'},
            'DATE'      : {'py': str,   'db': 'TEXT'},
            'INTEGER'   : {'py': int,   'db': 'INTEGER'},
            'REAL'      : {'py': float, 'db': 'REAL'},
        };
        # supported test operations
        s.ops = ['=','!=','>','>=','<','<=','like','in'];
    ############################################################################
    def connect(s,dbfile):
        """Connect to a sqlite3 database and store handle in s.dbh."""
        s.dbh = sqlite3.connect(dbfile);
        s.dbh.execute("PRAGMA foreign_keys=1"); # turn on foreign keys

    def disconnect(s,commit=True):
        """Disconnect from sqlite3 database."""
        if s.dbh==None: return;
        if commit: s.dbh.commit();
        else: s.dbh.rollback();
        s.dbh.close();
        s.dbh = None;

    def rollback(s):
        s.dbh.rollback();

    def execute(s,sqrs,transaction=True):
        """Executes a list of SQRs in a single transaction.  NOT FOR SELECTION."""
        # Get cursor from database handle
        c = s.dbh.cursor();
        try:
            # Initialize transaction if needed
            if transaction: c.execute("BEGIN TRANSACTION");
            # for every SQR statement
            for s in sqrs:
                # is it an execute type statement?
                if s[2]=='execute':
                    # execute with values if they are defined
                    if s[1]: c.execute(s[0], s[1]);
                    else: c.execute(s[0]);
                # is it an executemany statement?
                elif s[2]=='executemany':
                    # run with values, all executemany's should have values
                    c.executemany(s[0], s[1]);
                # otherwise break and rollback if transaction
                else:
                    if transaction: c.execute("ROLLBACK");
                    raise Exception("unrecognized database operation");
            # done running all SQRs, commit if in transaction
            if transaction: c.execute("COMMIT");
        # if there's an error anywhere along the way
        except:
            # rollback (undo) database if in transaction
            if transaction: c.execute("ROLLBACK");
            # propagate error back to caller
            raise;
        return;

    def execute_select(s,sqr):
        c = s.dbh.cursor();
        # execute with values if defined
        if sqr[0][1]!=None: c.execute(sqr[0][0], sqr[0][1]);
        else:
            try: c.execute(sqr[0][0]);
            except Exception as e:
                raise Exception(str(e) + "\n" + sqr[0][0]);
        df = pd.DataFrame(c.fetchall(), columns=[d[0] for d in c.description]);
        return df;
    ############################################################################
    def buildwheres(s,data,desc):
        ors = [];
        for i,r in data.iterrows():
            ands = [];
            ss = r.dropna();
            for i,v in ss.iteritems():
                ands.append(
                    s.hq(i) + "=" + str(s.cast(
                        v,
                        desc['type'][desc['name']==i].iloc[0],
                    ))
                );
            ors.append(' and '.join(ands));
        return "WHERE " + "(" + ") or (".join(ors) + ")";
    ############################################################################
    def buildselect_where(s,name,data,desc):
        """Builds where part of sql statement for dataframe (data) of columns ['andor','field','op','value'], value can be list, str, int, float, bool.  operation values are cast to native python types."""
        wlist = [];
        def tr_row(r):
            if r['andor']=='and': andor="and ";
            elif r['andor']=='or': andor="or ";
            elif r['andor']==None: andor="";
            else: raise Exception(
                str(r['andor'])+" is not a valid and/or argument");
            if r['op'] in s.ops:
                op = r['op'];
            else: raise Exception(str(r['op'])+" is not a valid operation");
            if type(r['value'])==type([]):
                vals = '(' + ','.join(['?' for v in r['value']]) + ')';
            elif type(r['value']) in [bool, int, float, str]:
                vals = '?';
            else: raise Exception("data type for value is not valid");
            return str(andor + r['field'] + " " + op + " " + vals);
        strows = [];
        rvalues = [];
        for i,r in data.iterrows():
            strows.append( tr_row(r) );
            fieldtype = desc['type'][desc['name']==r['field']].iloc[0];
            pytype = s.dmap[fieldtype]['py'];
            if type(r['value'])==type([]):
                rvalues = rvalues + [ pytype(v) for v in r['value'] ];
            else: rvalues.append(pytype(r['value']));
        return strows, rvalues;
    ############################################################################
    def buildselect(s,name,data,desc):
        """Builds full select where statement using dataframe of columns ['andor','field','op','value'], value can be list, str, int, float, bool.  Returns sqr."""
        sql = ("SELECT " + ','.join([s.hq(n) for n in desc['name']]) +" FROM " +
                str(name) + " WHERE ");
        where, rows = s.buildselect_where(name, data, desc);
        sql += "\n".join(where);
        return s.sqr(
            str(sql),
            rows,
            'execute'
        );
    ############################################################################
    def create_table(
        s,name,desc,
        mfk=pd.DataFrame(columns=['name','parent','references']),
        ifnotexist=True):
        """Returns SQR(s) for CREATE TABLE statement using a pandas.DataFrame description of the table."""
        #-----------------------------------------------------------------------
        def _ct_fieldline( r, vq=s.vq, hq=s.hq, dmap=s.dmap, cast=s.cast ):
            """Generates field line for CREATE TABLE statement."""
            line = [ hq(str(r['name'])) ];
            try: line.append( dmap[str(r['type'])]['db'] );
            except: raise;
            if r['primary_key']==0:
                if r['notnull']: line.append("NOT NULL");
                if r['unique']: line.append("UNIQUE");
            if not pd.isnull(r['default']):
                try:
                    line.append(
                        "DEFAULT " + str(cast(r['default'],r['type']))
                    );
                except: raise;
            return "\t".join(line);
        #-----------------------------------------------------------------------
        def _ct_primarykey( r, vq=s.vq, hq=s.hq, dmap=s.dmap, cast=s.cast ):
            """Generates primary key line for CREATE TABLE statement."""
            return str(hq(str(r['name'])));
        #-----------------------------------------------------------------------
        def _ct_foreignkey(df, vq=s.vq, hq=s.hq, dmap=s.dmap, cast=s.cast ):
            """Generates foreign key lines for CREATE TABLE statement."""
            return str(
                "FOREIGN KEY " +
                "(" + ','.join( [ hq(n) for n in df['name'] ] ) + ") " +
                "REFERENCES " + hq(df['parent'].iloc[0]) +
                "(" + ','.join( [ hq(n) for n in df['references'] ] ) + ")"
            );
        #-----------------------------------------------------------------------
        fields = [ _ct_fieldline(r) for i,r in desc.iterrows() ];
        pkeys = [ _ct_primarykey(r) for i,r in
                    desc[desc['primary_key']==1].iterrows() ];
        if len(mfk)>0:
            fkeys = [ _ct_foreignkey(mfk[mfk['parent']==par]) for par in
                        mfk['parent'].unique() ];
        else: fkeys = [];

        if ifnotexist: ifne = "IF NOT EXISTS";
        else: ifne = "";
        #-----------------------------------------------------------------------
        return s.sqr(
            str("\n".join([
                str("CREATE TABLE " + ifne + " " + s.hq(str(name)) + " ("),
                str("\t" + ",\n\t".join(fields + fkeys) + ","),
                str("\tPRIMARY KEY(" + ','.join(pkeys) + ")"),
                str(")"),
            ])), None, 'execute' );

    def drop_table(s,name):
        """Returns SQR(s) for dropping a table."""
        return s.sqr(
            "DROP TABLE IF EXISTS " + str(name),
            None,
            'execute'
        );

    def insert(s,name,data,desc,method='none'):
        """Returns SQR(s) for inserting a pandas.DataFrame into a table.  This also serves UPDATE functionalsity via. overwriting the existing data with overwrite=True."""
        # convert values DataFrame to list of lists of native python types
        values = s.nativetype( data, desc );

        # get list of field names in order
        fields = [ s.hq(f) for f in desc['name'] ];
        if method=='none': method_cmd = "";
        elif method=='ignore': method_cmd = 'OR IGNORE';
        elif method=='replace': method_cmd = 'OR REPLACE';
        else: method_cmd="";
        # build statement
        return s.sqr(
            str(
                "INSERT " + method_cmd + " INTO " + s.hq(name) +
                "(" + ','.join(fields) + ")\n" +
                "VALUES(" + ','.join(['?' for f in fields]) + ")"
            ),
            values,
            'executemany'
        );

    def delete(s,name,data,desc):
        """Returns SQR(s) for deleting data from a table.  The DataFrame passed should contain ONLY the primary keys of the rows to be deleted."""
        return s.sqr(
            str(
                "DELETE FROM " + s.hq(name) + "\n" +
                s.buildwheres(data, desc)
            ),
            None,
            'execute'
        );

    def select(s,name,data,desc):
        """Returns SQR(s) for selecting data from a table given a list of inclusive conditions in data (each row is a list of ANDS and rows are OR'd)."""
        return s.sqr(
            str(
                "SELECT " + ",".join([ s.hq(f) for f in desc['name'] ]) + " " +
                "FROM " + s.hq(name) + "\n" +
                s.buildwheres(data, desc)
            ),
            None,
            'execute'
        );

    def select_sql(s,sql):
        return s.sqr( str(sql), None, 'execute' );

    def selectwith(s,name,withsql,desc):
        """Returns 'SELECT [fields] FROM' part of SQL."""
        return s.sqr(
            str(
                "SELECT " + ",".join([ s.hq(f) for f in desc['name'] ]) + " " +
                "FROM " + s.hq(name) + "\n" + withsql
            ),
            None,
            'execute'
        );
    #--------------------------------------------------------------------------#
    def table_exists(s,name):
        """Returns true of table 'name' is in database"""
        return s.sqr(
            str(
                "SELECT count(name) from sqlite_master WHERE " +
                "type='table' and name='" + str(name) +"'"
            ),
            None,
            'execute'
        );
    def count_experiments_sets(s,name,data):
        """Returns a SQL that counts the number of distinct sets in a list of experiment ids."""
        return s.sqr(
            str(
                "SELECT experiment_id, count(distinct(set_id)) as sets FROM " +
                str(name) + "\n" +
                "WHERE experiment_id in (" +
                    ','.join([s.vq(v) for v in data['experiment_id']]) +
                ")\n" +
                "GROUP BY experiment_id"
            ),
            None,
            'execute'
        );

    def select_unique_experiment_ids(s,name):
        """Returns a pd.DataFrame of all unique experiment_ids."""
        return s.sqr(
            str(
                "SELECT distinct(experiment_id) FROM " + str(name)
            ),
            None,
            'execute'
        );
    def select_experiment_report(s,settab,samtab):
        """Returns unique experiment ids and count of sets/samples."""
        return s.sqr(
            "\n".join([
                "select",
                "   se.experiment_id,",
                "   count(distinct(se.set_id)) as sets,",
                "   count(sa.sample_id) as sams",
                "from " + str(settab) + " as se",
                "left join " + str(samtab) + " as sa",
                "   ON sa.experiment_id = se.experiment_id",
                "   AND sa.set_id = se.set_id",
                "group by se.experiment_id",
            ]),
            None,
            'execute'
        );

    ############################################################################
