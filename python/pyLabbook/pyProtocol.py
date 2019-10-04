import os, sys, re;
import numpy as np, pandas as pd;
import pyLabbook.core as core; # LOAD CORE FUNCTIONS
from pyLabbook.SQLEngines.engine import SQLEngine;
import pyLabbook.SQLEngines.manager as manager; # import SQL engine manager
# This is a standard generic protocol class that can be extended
# So when making a new protocol, import pyProtocol.protocol and
# return an instance of pyProtocol.protocol with properly adjusted
# properties.  Methods should all be the same.

# allow add method to protocol by extending class, defining and returning.

class pyProtocol(object):
    """pyLabbook.pyProtocol base class for pyLabbook protocols.

    Parameters
    ----------
    plb : pyLabbook.pyLabbook object
        A pyLabbook.pyLabbook object.

    """
    def __init__(s,plb):
        if not os.path.isdir( os.path.join(plb.root, plb.repositoryPath) ):
            raise Exception("Can't find path " + os.path.join(plb.root, plb.repositoryPath) + "...");
        s.sql = SQLEngine();
        # initialize namespace for custom methods
        class empty(object):
            def __init__(s): return;
        s.c = empty();
        # store labbook info
        s.pyLabbook = plb;
        # IDMATCH REGULAR EXPRESSION PRECOMPILED
        s.idmatch = re.compile(r'^[A-Z,a-z,1-9][A-Z,a-z,0-9,\-,\_]+$');
        # PROTOCOL ID
        s.PROTOCOLID = "PROTOCOL";
        # DOCUMENTS FOLDER NAME
        s.DOCUMENTS_FOLDER = "documents";
        # EXPERIMENTS FOLDER NAME
        s.EXPERIMENTS_FOLDER = "experiments";
        # BASENAME FOR SET FILES
        s.SETFILEBASE = "SETS";
        s.SAMFILEBASE = "SAMPLES";
        # BASENAME FOR SET AND SAMPLE TABLES
        s.SETTABLEBASE = "SETS";
        s.SAMTABLEBASE = "SAMPLES";
        # NAME FOR SHEETS IF NECESSARU
        s.SETSHEET = "SETS";
        s.SAMSHEET = "SAMPLES";
        # SET DEFINITION
        # column names for set and sample description pandas.DataFrames
        s._descColumns = {
            # col name      # default value for add[Set/Sam]Field
            'name'          : None,
            'type'          : "TEXT",
            "notnull"       : False,
            "unique"        : False,
            "description"   : None,
            "default"       : None,
            "primary_key"   : False,
        };
        # default set description
        s._DEFAULT_SETDESC = pd.DataFrame([
            ['experiment_id','TEXT',True,False,'id of the experiment',
            None,True],
            ['set_id','TEXT',True,False,'id of the set',None,True],
        ], columns=list(s._descColumns.keys()));
        # default sample description
        s._DEFAULT_SAMDESC = pd.DataFrame([
            ['experiment_id','TEXT',True,False,'id of the experiment',
            None,True],
            ['set_id','TEXT',True,False,'id of the set',None,True],
            ['sample_id','TEXT',True,False,'id of the sample',None,True],
            ['replicate','TEXT',True,False,'id of the replicate',None,True],
        ], columns=list(s._descColumns.keys()));
        # working set description
        s._SETDESC = s._DEFAULT_SETDESC.copy();
        # working sample description
        s._SAMDESC = s._DEFAULT_SAMDESC.copy();
        # get sql engine object
        s.sql = manager.loadSQLEngine(s.pyLabbook.databaseFormat);
        s.setup();
    ############################################################################
    # SETUP
    ############################################################################
    def setup(s):
        """Setup extended table columns and perform other protocol-specific
        initialization.  Functionality is specified by protocols, in the
        protocol file (see python/pyLabbook/protocols/).

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        return;
    ############################################################################
    # SWITCH PYLABBOOKS
    ############################################################################
    def loadPyLabbook(s,plb):
        """Loads a new pyLabbook object.  All methods will now connect with
        resources assocaited with the supplied labbook object.

        Parameters
        ----------
        plb : pyLabbook.pyLabbook object
            The pyLabbook to connect to.

        Returns
        -------
        None

        """
        s.disconnect();         # disconnect
        s.sql = SQLEngine();    # reset database info
        if not os.path.isdir( os.path.join(plb.root, plb.repositoryPath) ):
            raise Exception("Can't find path " + os.path.join(plb.root, plb.repositoryPath) + "...");
        s.pyLabbook = plb;

    ############################################################################
    # CONNECT TO DATABASE
    ############################################################################
    def connect(s):
        """Connect to the database of the currently linked labbook.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        s.sql.connect(
            os.path.join(
                s.pyLabbook.root,
                s.pyLabbook.databasePath,
                s.pyLabbook.databaseFile
            )
        );

    def disconnect(s,commit=True):
        """Disconnect from the database of the currently linked labbook.

        Parameters
        ----------
        commit : boolean
            If true, explicitly runs commit before closing.  Some databases automatically commit when closing.

        Returns
        -------
        None

        """
        s.sql.disconnect(commit=commit);

    def rollback(s):
        """Rollback database activity.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        s.sql.rollback();
        s.sql.disconnect(commit=False);


    ############################################################################
    # ID validators
    ############################################################################
    def validID(s,id):
        """Validate characters in an id.

        Parameters
        ----------
        id : str
            The id to validate.

        Returns
        -------
        boolean
            True if valid, False if not.

        """
        if not s.idmatch.match(id):
            return False;
        else:
            return True;

    def testID(s,id):
        """Tests whether an id is valid or not, using validID.  Raises exception if not valid.

        Parameters
        ----------
        id : str
            The id to validate.

        Returns
        -------
        str
            The validated id cast as str.

        """
        """Crashes with invalid IDs."""
        if not s.validID(str(id)): raise Exception("Invalid ID: '" + str(id) + "',\nonly A-Z, a-z, 0-9 _ and _ are allowed.");
        else: return str(id);

    ############################################################################
    # DATABASE TABLENAMES
    ############################################################################
    def setTableName(s):
        """Get the name of set table for this protocol.

        Returns
        -------
        str
            Name of the set table for this protocol.

        """
        return '_'.join([s.PROTOCOLID, s.SETTABLEBASE]);

    def samTableName(s):
        """Get the name of sample table for this protocol.

        Returns
        -------
        type
            Description of returned object.

        """
        return '_'.join([s.PROTOCOLID, s.SAMTABLEBASE]);

    ############################################################################
    # FILESYSTEM ###############################################################
    ############################################################################
    # PATH GENERATORS
    def protocolroot(s):
        """Returns path to root of this protocol."""
        return os.path.join(
            s.pyLabbook.root,
            s.pyLabbook.repositoryPath,
            s.PROTOCOLID
        );

    def documentPath(s):
        """Returns path to documents folder of this protocol."""
        return os.path.join(s.protocolroot(), s.DOCUMENTS_FOLDER);

    def experimentsPath(s):
        """Returns path to folder containing all experiments."""
        return os.path.join(s.protocolroot(), s.EXPERIMENTS_FOLDER);

    def experimentPath(s, eid):
        """Returns path to a specific experiment."""
        eid = s.testID(eid);
        return os.path.join(s.experimentsPath(), eid);

    # SET AND SAMPLE FILES
    def setFileName(s, eid):
        """Returns the set filename for an experiment ID, with extension."""
        eid = s.testID(eid);
        return '_'.join([
            s.PROTOCOLID,
            eid,
            ''.join([
            s.SETFILEBASE,
            '.',
            s.pyLabbook.sheetFormat
            ])
        ]);

    def samFileName(s, eid):
        """Returns the sample filename for an experiment ID, with extension."""
        eid = s.testID(eid);
        return '_'.join([
            s.PROTOCOLID,
            eid,
            ''.join([
            s.SAMFILEBASE,
            '.',
            s.pyLabbook.sheetFormat
            ])
        ]);

    def setFile(s,eid):
        """Returns full setfile with path for experimetn ID, with extension."""
        eid = s.testID(eid);
        return os.path.join(
            s.experimentPath(eid),
            s.setFileName(eid)
        );

    def samFile(s,eid):
        """Returns full samplefile with path for experimetn ID, with extension."""
        eid = s.testID(eid);
        return os.path.join(
            s.experimentPath(eid),
            s.samFileName(eid)
        );
    ############################################################################
    # SET AND SAMPLE DEFINITIONS
    ############################################################################
    def setColumns(s):
        """Returns list of column headers for set."""
        return list(s._SETDESC['name']);

    def samColumns(s):
        """Returns list of column headers for sample."""
        return list(s._SAMDESC['name']);

    def setDesc(s):
        """Returns set table description pandas.DataFrame."""
        return s._SETDESC.copy();

    def samDesc(s):
        """Returns sample table description pandas.DataFrame."""
        return s._SAMDESC.copy();

    #---------------------------------------------------------------------------
    def _addSetSamColumn(s,setsam,**kwargs):
        """Generic for adding field to set (setsam='SET') or sample
        (setsam='SAM') tables."""
        # load valid properties from kwargs to pandas.Series
        r = pd.Series(s._descColumns);
        valid = r.index.tolist();
        for k in kwargs.keys():
            if k not in valid: raise Exception("Invalid keyword");
            r[k] = kwargs[k];
        # append to set or sample description pandas.DataFrame
        if setsam=='SET':
            s._SETDESC = s._SETDESC.append(r, ignore_index=True);
        elif setsam=='SAM':
            s._SAMDESC = s._SAMDESC.append(r, ignore_index=True);

    def addSetColumn(s,**kwargs):
        """Add a field to set description."""
        s._addSetSamColumn('SET',**kwargs);

    def addSamColumn(s,**kwargs):
        """Add a field to set description."""
        s._addSetSamColumn('SAM',**kwargs);

    ############################################################################
    # SETS AND SAMPLES
    ############################################################################
    def getEmptySets(s):
        """Returns an empty set pandas.DataFrame."""
        return pd.DataFrame( columns=s._SETDESC['name'] );

    def getEmptySams(s):
        """Returns an empty sample pandas.DataFrame."""
        return pd.DataFrame( columns=s._SAMDESC['name'] );

    #---------------------------------------------------------------------------
    def _loadSetSam(s,eids,setsam):
        """Generic for loading data from set (setsam='SET') or sample
        (setasm='SAM') files from a list-like of experiment ids (eids)."""
        bulk = [];
        for eid in eids:
            # setup and load each eid separately
            eid = s.testID(eid);
            if setsam=='SET':
                ffn = s.setFile(eid);
                sheet = s.SETSHEET;
                desc = s.setDesc();
                empty = s.getEmptySets();
            elif setsam=='SAM':
                ffn = s.samFile(eid);
                sheet = s.SAMSHEET;
                desc = s.samDesc();
                empty = s.getEmptySams();
            else: raise Exception("invalid setsam type.");
            # load
            df = core.load_dataframe(
                    ffn,
                    format=s.pyLabbook.sheetFormat,
                    sheet=sheet
            );
            df['experiment_id']=eid;
            bulk.append(df);

        # concatenate/finalize structure
        if len(bulk)>1: bulk = pd.concat(bulk, ignore_index=True);
        elif len(bulk)==1: bulk = bulk[0];
        else: bulk = empty;

        # data typing and replacements
        bulk = s._formatSetSamData(bulk, setsam);
        return bulk;

    def loadSetFile(s,eids):
        """Loads data from set files from a list-like of experient ids
        (eids)."""
        return s._loadSetSam(eids,'SET');

    def loadSamFile(s,eids):
        """Loads data from sample files from a list-like of experiment ids
        (eids)."""
        return s._loadSetSam(eids,'SAM');

    #---------------------------------------------------------------------------
    def _selectSetSamFullWhere(s, wheres, setsam):
        """Selects data from set (setsam='SET') or sample (setsam='SAM') table
        using custom WHERE clause specified by the wheres argument, which is a
        pandas.DataFrame with columns ['andor','field','op','value'].  Each row
        specifies a WHERE clause that is either 'and' or 'or' (column andor)
        and specifies the field (field column), the logical operation (op) and
        the value to compare with (value).  See pyton/pyLabbook/SQLEngines/
        SQLITE3.py function
        pyLabbook.SQLEngines.SQLITE3.engine.buildselect().  The order of each
        clause reflects the order of the rows in the wheres DataFrame.

        Results are returned as a pandas.DataFrame.

        Example
        -------
        >>> wheres = pd.DataFrame([
        >>>     [None, 'first', 'LIKE', 'jo%'],
        >>>     ['AND', 'last', '=', 'smith'],
        >>> ], columns=['andor','field','op','value']);

        will return the result of a query with:
        >>> WHERE first LIKE 'jo%'
        >>> AND last = 'smith'

        """

        if setsam=='SET':
            tablename = s.setTableName();
            desc = s.setDesc();
        elif setsam=='SAM':
            tablename = s.samTableName();
            desc = s.samDesc();
        else: raise Exception("invalid setsam");
        # build sqr using the wheres clauses
        sqr = s.sql.buildselect(
            tablename,
            wheres,
            desc
        );
        # execute
        return s.sql.execute_select(sqr);

    def selectSetsFullWhere(s, wheres):
        """Selects set data from database using more powerful logic
        specification.  See _selectSetSamFullWhere() for more detail."""
        return s._selectSetSamFullWhere(wheres, 'SET');

    def selectSamsFullWhere(s, wheres):
        """Selects sample data from database using more powerful logic
        specification.  See _selectSetSamFullWhere() for more detail."""
        return s._selectSetSamFullWhere(wheres, 'SAM');
    #---------------------------------------------------------------------------
    def _selectSetSamWhere(s,wheres,setsam):
        """Selects data from set (setsam='SET') or sample (setsam='SAM') table
        using custom WHERE clause specified by the wheres argument, which is
        a pandas.DataFrame.  The columns of the DataFrame are named after
        set or sample columns and each row is converted into a list of
        [column]=[value] clauses joined by AND, and the rows are joined by OR.

        Results are returned as a pandas.DataFrame.

        Example
        -------
        >>> wheres = pd.DataFrame([
        >>>     ['joe', None, 'smith'],
        >>>     ['jane', None None]
        >>> ], columns=['first','middle','last']);
        Will return the results of a query with:
        >>>     WHERE
        >>>     ((first="joe" and last="smith") OR
        >>>     (first="jane"))

        """
        # generic for both
        if setsam=='SET':
            tablename = s.setTableName();
            desc = s.setDesc();
        elif setsam=='SAM':
            tablename = s.samTableName();
            desc = s.samDesc();
        else: raise("Invalid setsam.");
        sqr = s.sql.select(
            tablename,
            wheres,
            desc
        );
        df = s.sql.execute_select(sqr);
        df = s._formatSetSamData(df, setsam);
        return df;

    def selectSetsWhere(s,wheres):
        """Selects sets from database with wheres clause.  See
        _selectSetSamWhere() for more detail."""
        return s._selectSetSamWhere(wheres,'SET');

    def selectSamsWhere(s,wheres):
        """Selects samples from database given locs.  See
        _selectSetSamWhere() for more detail."""
        return s._selectSetSamWhere(wheres,'SAM');

    #---------------------------------------------------------------------------
    def _selectSetSamWith(s,sql,setsam):
        """Selects data from set (setsam='SET') or sample (setsam='SAM') table
        using custom and direct WHERE clause (sql, the actual WHERE clause).
        Results are returned as a pandas.DataFrame."""
        if setsam=='SET':
            tablename = s.setTableName();
            desc = s.setDesc();
        elif setsam=='SAM':
            tablename = s.samTableName();
            desc = s.samDesc();
        else: raise("Invalid setsam.");
        sqr = s.sql.selectwith(
            tablename,
            sql,
            desc
        );
        df = s.sql.execute_select(sqr);
        df = s._formatSetSamData(df, setsam);
        return df;

    def selectSetsWith(s,sql):
        """Selects sets using custom direct WHERE clause (sql).  See
        _selectSetSamWith() for more detail."""
        return s._selectSetSamWith(sql, 'SET');

    def selectSamsWith(s,sql):
        """Selects samples using custom direct WHERE clause (sql).  See
        _selectSetSamWith() for more detail."""
        return s._selectSetSamWith(sql, 'SAM');

    #---------------------------------------------------------------------------
    def selectSQL(s,sql):
        """Returns the results of a select query (sql) with no formatting, no
        casting, no validation and no enforcement.  This can be used for complex
        select statements that involve table joins and/or may not even include
        tables for this protocol.  Results are returned as a
        pandas.DataFrame."""
        sqr = s.sql.select_sql(sql);
        return s.sql.execute_select(sqr);

    def executeSQL(s,sql,data=None,mode='execute'):
        """Executes a raw SQL query (sql) with or without data (e.g. insert).
        See pyLabbook.SQLEngines.engine.engine.sqr() for valid modes.  Returns
        None."""
        sqr = s.sql.sqr(str(sql), data, mode);
        s.sql.execute(sqr);
        return None;

    def selectAllExperimentIDs(s):
        """Returns a list of all experiment ids for this protocol in the linked
        labbook as a pandas.DataFrame with one 'experiment_id' column."""
        sqr = s.sql.select_unique_experiment_ids( s.setTableName() );
        return s.sql.execute_select(sqr);

    def countExperimentsSets(s, eids):
        """Returns a count of sets and samples for a list-like of experiment ids
        (eids) as a pandas.DataFrame with columns
        ['experiment_id','sets','sams']."""
        wheres = pd.DataFrame(columns=['experiment_id']);s
        wheres['experiment_id']=eids;
        sqr = s.sql.count_experiments_sets(s.setTableName(), wheres);
        return s.sql.execute_select(sqr);

    #---------------------------------------------------------------------------
    def _writeSetSam(s,df,setsam,eid="",overwrite=True,initialize=False):
        """Write set (setsam='SET') or sample (setsam='SAM') repository files
        from a pandas.DataFrame containing the data to write (df).  Overwrite if
        file exists (overwrite=True) and initialize experiment folders if they
        don't exist (initialize=True), otherwise raises exception.

        By default, will write to all experiment_id's specified in df.

        To write an empty DataFrame (e.g. when initializing an experiment) have
        df be an empty list-like and supply optional eid=[the experiment id to
        write empty file for].

        Returns None.

        """

        # generic for both
        if not s.checkFileStructure():
            s.createFileStructure();

        # get appropriate naming functions
        if setsam=='SET':
            ffn_func = s.setFile;
            sheet = s.SETSHEET;
            desc = s.setDesc();
            empty = s.getEmptySets();
        elif setsam=='SAM':
            ffn_func = s.samFile;
            sheet = s.SAMSHEET;
            desc = s.samDesc();
            empty = s.getEmptySams();
        else: raise Exception("invalid setsam type.");

        # test experiment ids
        if len(df)<1:
            eid_list = [eid];
            df = empty;
        else: eid_list = list(df['experiment_id'].unique());

        if len(eid_list)<1: raise Exception("No experiment IDs defined.");

        # check all eids first
        for eid in eid_list:
            eid = s.testID(eid);
            if not s.experimentPathExists(eid):
                if not initialize:
                    raise Exception("Can't find path " + s.experimentPath(eid));
                else:
                    s.createExperimentFolder(eid);
            if overwrite==False and core.isfile( ffn_func(eid) ):
                raise Exception("Overwrite off for " + ffn_func(eid));

        df = s._formatSetSamData(df, setsam);
        # now save each eid individually
        for eid in eid_list:
            eid = s.testID(eid);
            ss = df[df['experiment_id']==eid]; #get data for this eid
            core.write_dataframe(
                ffn_func(eid),
                s.pyLabbook.sheetFormat,
                ss[desc['name']].drop(labels='experiment_id', axis=1),
                sheet=sheet,
                overwrite=overwrite
            );

    def writeSets(s,setdf,eid="",overwrite=True,initialize=False):
        """Writes pandas.DataFrame to set file(s) using experiment IDs.  See
        _writeSetSam() for more detail."""
        s._writeSetSam(setdf,'SET',eid=eid, overwrite=overwrite,
            initialize=initialize);
        return;

    def writeSams(s,samdf,eid="",overwrite=True,initialize=False):
        """Writes pandas.DataFrame to sample file(s) using experiment IDs.  See
        _writeSetSam() for more detail."""
        s._writeSetSam(samdf,'SAM',eid=eid, overwrite=overwrite,
            initialize=initialize);
        return;

    #---------------------------------------------------------------------------
    def _storeSetSam(s,df,setsam,method='none'):
        """Store data (df, pandas.DataFrame) from set (setsam='SET') or sample
        (setsam='SAM') repository file to database of linked labbook.  Method
        'killreplace' attempts to delete all records associated with experient
        ids in df before insert.  Method 'none' will raise if records aleady
        exist in database.  Method 'ignore' will prevent overwriting records
        and method 'replace' will always overwrite.  Returns None."""
        if len(df)<1: return;
        if setsam=='SET':
            tablename = s.setTableName();
            desc = s.setDesc();
        elif setsam=='SAM':
            tablename = s.samTableName();
            desc = s.samDesc();
        else:
            raise Exception("invalid option");

        sqrs = [];
        if method=='killreplace':
            sqrs += s.sql.delete(
                tablename,
                pd.DataFrame({
                    'experiment_id': list(df['experiment_id'].unique()),
                }),
                pd.DataFrame(
                    [['experiment_id','TEXT']],
                    columns=['name','type']
                )
            );
        sqrs += s.sql.insert(
            tablename,
            df,
            desc,
            method=method,
        );
        s.sql.execute(sqrs);

    def storeSets(s,setdf,method='none'):
        """Stores pandas.DataFrame to set table.  See _storeSetSam() for
        more details."""
        s._storeSetSam(setdf,'SET',method=method);

    def storeSams(s,samdf,method='none'):
        """Stores pandas.DataFrame to sample table.  See _storeSetSam() for
        more details."""
        s._storeSetSam(samdf,'SAM',method=method);

    def storeSetsAndSamples(s, setdf, samdf, method='none', transaction=True):
        """Stores set data (setdf pandas.DataFrame) and sample data (samdf,
        pandas.DataFrame) together in a single transaction if requested
        (transaction=True).  The same method is used for both tables.  Returns
        None."""

        sqrs = [];
        if method=='killreplace':
            if len(samdf)>0:
                sqrs += s.sql.delete(
                    s.samTableName(),
                    pd.DataFrame(
                        [ samdf['experiment_id'].unique() ],
                        columns=['experiment_id']
                    ),
                    pd.DataFrame(
                        [['experiment_id','TEXT']],
                        columns=['name','type']
                    )
                );
            if len(setdf)>0:
                sqrs += s.sql.delete(
                    s.setTableName(),
                    pd.DataFrame(
                        [ setdf['experiment_id'].unique() ],
                        columns=['experiment_id']
                    ),
                    pd.DataFrame(
                        [['experiment_id','TEXT']],
                        columns=['name','type']
                    )
                );
        method='replace';
        if len(setdf)>0:
            sqrs += s.sql.insert(
                s.setTableName(),
                setdf,
                s.setDesc(),
                method=method,
            );
        if len(samdf)>0:
            sqrs += s.sql.insert(
                s.samTableName(),
                samdf,
                s.samDesc(),
                method=method,
            );
        s.sql.execute(sqrs, transaction=transaction);

    #---------------------------------------------------------------------------
    def _deleteSetSamWhere(s,wheres,setsam):
        """Deletes set (setsam='SET') or sample (setsam='SAM') records from database of linked labbook using basic WHERE clause (wheres, pandas.DataFrame) data.  See _selectSetSamWhere() for details on the
        format of the wheres DataFrame.  Returns None."""

        if setsam=='SET':
            tablename = s.setTableName();
            desc = s.setDesc();
        elif setsam=='SAM':
            tablename = s.samTableName();
            desc = s.samDesc();
        else: raise Exception("invalid setsam");
        sqr = s.sql.delete(
            tablename,
            wheres,
            desc
        );
        s.sql.execute(sqr);

    def deleteSetsWhere(s,wheres):
        """Deletes set records from database.  See _deleteSetSamWhere()."""
        s._deleteSetSamWhere(wheres,'SET');

    def deleteSamsWhere(s,wheres):
        """Deletes sample records from database.  See _deleteSetSamWhere()."""
        s._deleteSetSamWhere(wheres,'SAM');

    def deleteSetsAndSamplesWhere(s, wheres):
        """Deletes both set and samples using same WHERE logic as
        _deleteSetSamWhere() in a single transaction."""
        sqr_set = s.sql.delete(
            s.setTableName(),
            wheres,
            s.setDesc(),
        );
        sqr_sam = s.sql.delete(
            s.samTableName(),
            wheres,
            s.samDesc()
        );
        # delete samples first in accord with foreign keys
        s.sql.execute(sqr_sam + sqr_set);

    ############################################################################
    # PATH CREATORS AND CHECKERS FOR WHOLE PROTOCOL
    ############################################################################
    def createFileStructure(s):
        """Creates minimum requried file structure at root if needed."""
        # protocol folder
        if not core.ispath(s.protocolroot()):
            core.makepath(s.protocolroot());
        if not core.ispath(s.experimentsPath()):
            core.makepath(s.experimentsPath());
        if not core.ispath(s.documentPath()):
            core.makepath(s.documentPath());

    def checkFileStructure(s):
        """Returns True if minimum required file structure is present."""
        if not core.ispath(s.protocolroot()):
            return False;
        if not core.ispath(s.experimentsPath()):
            return False;
        if not core.ispath(s.documentPath()):
            return False;
        return True;

    def deleteFileStructure(s,require_empty=False):
        """Deletes entire file structure for protocol.  Can specify whether the
        structure should be empty (require_empty=True) for delete operation."""
        core.rmpath( s.protocolroot(), require_empty=require_empty );

    ############################################################################
    # DATABASE CREATORS AND CHECKERS FOR WHOLE PROTOCOL
    ############################################################################
    def createTables(s,ifnotexist=True):
        """Creates set and sample tables if they don't already exist."""
        sqr = s.sql.create_table(
            s.setTableName(),
            s.setDesc(),
            ifnotexist=True,
        );
        sqr += s.sql.create_table(
            s.samTableName(),
            s.samDesc(),
            mfk=pd.DataFrame([
                ['experiment_id',s.setTableName(),'experiment_id'],
                ['set_id',s.setTableName(),'set_id'],
            ],columns=['name','parent','references']),
            ifnotexist=ifnotexist,
        );
        s.sql.execute(sqr);

    ############################################################################
    # EXPERIMENTS
    ############################################################################
    def initializeExperiment(s,eid,overwrite=False):
        """Initialize an experiment with id eid, may overwrite if it exists
        (overwrite=True), which will delete all existing repository files for
        the experiment before writing over with empty ones, otherwise raises.
        INitialization means creating the repository folders and writing empty
        set and sample spreadsheet files.  Returns None."""

        eid = s.testID(eid);
        if not s.checkFileStructure():
            raise Exception("File structure is not yet valid.");

        # experiment folder
        if core.ispath(s.experimentPath(eid)):
            if overwrite:
                s.deleteExperimentPath(eid);
            else:
                raise Exception("Path " + s.experimentPath(eid) + " already exists");
        s.createExperimentFolder(eid);
        # write empty set and sample files
        s.writeSets( s.getEmptySets(), eid );
        s.writeSams( s.getEmptySams(), eid );

    def createExperimentFolder(s,eid):
        """Create repository folder for experiment eid."""
        eid = s.testID(eid);
        if not core.ispath( s.experimentPath(eid) ):
            core.makepath( s.experimentPath(eid) );

    def deleteExperimentPath(s,eid):
        """Delete the repository folder for experiment eid."""
        eid = s.testID(eid);
        if not core.ispath( s.experimentPath(eid) ):
            raise Exception("Can't find " + s.experimentPath(eid));
        core.rmpath( s.experimentPath(eid), require_empty=False );

    def experimentPathExists(s,eid):
        """Does the folder for experiment eid exist? True or False."""
        eid = s.testID(eid);
        return core.ispath( s.experimentPath(eid) );

    def setFileExists(s,eid):
        """Does the set file for experiment eid exist? True or False."""
        eid = s.testID(eid);
        return core.isfile( s.setFile(eid) );

    def samFileExists(s,eid):
        """Does the sample file for experiment eid exist? True or False."""
        eid = s.testID(eid);
        return core.isfile( s.samFile(eid) );

    def experimentFilesExist(s,eid):
        """Do both the set and sample files for experiment eid exist?
        True or False."""
        eid = s.testID(eid);
        if s.setFileExists(eid) or s.samFileExists(eid): return True;
        else: return False;

    def listExperimentFolders(s):
        """Returns a list of the folders in the root experiments folder
        for this protocol/labbook.  This is basically a list of the experiment
        ids that exist in the repository, however, other folders created by
        user may exist."""
        return core.listDirs( s.experimentsPath() );

################################################################################
    def _formatSetSamData(s,df,setsam):
        """Cleans and casts the values in a pandas.DataFrame (df) to conform
        with the set table (setsam='SET') or sample table (setsam='SAM') of this
        protocol.  Returns pandas.DataFrame of altered values."""

        df = df.copy();
        if setsam=='SET':
            desc = s.setDesc();
        elif setsam=='SAM':
            desc = s.samDesc();
        else:
            raise Exception("Invalid setsam");

        for i,r in desc[['name','type']].iterrows():
            t = s.sql.dmap[r['type']]['py'];
            # force type and handle NaN's
            if t==str:
                # string NaN converted to '' instead of 'nan'
                df[r['name']] = df[r['name']].fillna('').astype(t);
            else:
                # numeric NaN are okay
                try:
                    df[r['name']] = df[r['name']].fillna(np.nan).replace('',np.nan).astype(t);
                except: pass;
                # integer NaN are also not valid...
        return df;

    def formatSetData(s,df):
        """Cleans and casts pandas.DataFrame (df) to conform with set table.
        See _formatSetSamData() for more detail."""
        return s._formatSetSamData(df,'SET');

    def formatSamData(s,df):
        """Cleans and casts pandas.DataFrame (df) to conform with sample table.
        See _formatSetSamData() for more detail."""
        return s._formatSetSamData(df,'SAM');
################################################################################
    def exportSerialized(s):
        """Returns python code that creates the current instance as a basic
        extension of pyLabbook.pyProtocol.  This is used, for example, by the
        manager GUI which needs to generate protocol python files.  This only
        includes column specifications and does not incorporate methods that may
        have been added by the protocol's creator.  This is not intended, as the
        name might suggest, to return a true serialized version of this
        object.  Returns str of python code."""

        def qqc(v): return "\"" + str(v) + "\",";
        def qq(v): return "\"" + str(v) + "\"";

        buff = [
            "# pyProtocol specification generated by pyProtocol.py",
            "from pyLabbook import pyProtocol;",
            "class initialize(pyProtocol):",
            "\tdef setup(s):",
            "\t\ts.PROTOCOLID = " + qq(s.PROTOCOLID) + ";",
        ];

        def formatrow(r,setsam=None):
            if setsam=='SET': top = "\t\ts.addSetColumn(";
            elif setsam=='SAM': top = "\t\ts.addSamColumn(";
            else: raise Exception("invalid setsam for formatrow()");

            dt = s.sql.dmap[r['type']]['py'];
            if pd.isnull(r['default']): dv = "None";
            else:
                if dt==str: dv = qq(r['default']);  # quote if string type
                else: dv = r['default'];            # otherwise bare
            rb = [
                top,
                "\t\t\tname\t\t\t= " + qq(r['name']) + ",",
                "\t\t\ttype\t\t\t= " + qq(r['type']) + ",",
                "\t\t\tnotnull\t\t\t= " + str(r['notnull']) + ",",
                "\t\t\tunique\t\t\t= " + str(r['unique']) + ",",
                "\t\t\tdescription\t\t= " + qq(r['description']) + ",",
                "\t\t\tdefault\t\t\t= " + dv + ",",
                "\t\t\tprimary_key\t\t= " + str(r['primary_key']) + ",",
                "\t\t);",
            ];
            return rb;

        setdesc = s.setDesc();
        setdesc = setdesc[~setdesc['name'].isin(
            s._DEFAULT_SETDESC['name']
        )];
        samdesc = s.samDesc();
        samdesc = samdesc[~samdesc['name'].isin(
            s._DEFAULT_SAMDESC['name']
        )];

        for i,r in setdesc.iterrows():
            buff += formatrow(r,setsam='SET');
        for i,r in samdesc.iterrows():
            buff += formatrow(r,setsam='SAM');

        return "\n".join(buff);
################################################################################
    def setTableExists(s):
        """Does the set table for this protocol exist in labbook? True or
        False."""
        sqr = s.sql.table_exists( s.setTableName() );
        z = s.sql.execute_select(sqr);
        if z.iloc[0,0]==0: return False;
        else: return True;

    def samTableExists(s):
        """Does the sample table for this protocol exist in labbook? True or
        False."""
        sqr = s.sql.table_exists( s.samTableName() );
        z = s.sql.execute_select(sqr);
        if z.iloc[0,0]==0: return False;
        else: return True;

################################################################################
    def inspect(s):
        """Returns a basic report of the protocol's database and repository
        presence for the linked labbook as a pandas.DataFrame with columns
        'experiment_id' (all unique experiment ids), 'sets' (count of sets i
        experiment) and 'sams' (count of samples in experiment), 'database'
        (True if experiment is in database), 'repository' (True if repository
        path exists for experiment), 'setfile' (true if repsitory set file
        exists) and 'samfile' (true if repository sample file exists)."""

        # get experiment info from database
        sqr = s.sql.select_experiment_report(
            s.setTableName(),
            s.samTableName()
        );
        db_dat = pd.DataFrame(columns=['experiment_id','sets','sams']);
        if not s.setTableExists():
            if s.samTableExists():
                raise Exception("sample table is orphaned.");
        else: db_dat = s.sql.execute_select(sqr);
        # get experimemnt list from repository
        edirs = core.listDirs( s.experimentsPath() );
        # are they experiments with set/sample files?

        report_rows = [];
        for eid in edirs['experiment_id'].unique():
            r = pd.Series();
            r['experiment_id'] = str(eid);
            r['repository'] = True;
            if len(db_dat[db_dat['experiment_id']==str(eid)])>=1:
                ss = db_dat[db_dat['experiment_id']==str(eid)].iloc[0];
                r['database']=True;
                r['sets'] = ss['sets'];
                r['sams'] = ss['sams'];
            else:
                r['database']=False;
                r['sets']=0;
                r['sams']=0;
            if core.isfile( s.setFile(eid) ): r['setfile']=True;
            else: r['setfile']=False;
            if core.isfile( s.samFile(eid) ): r['samfile']=True;
            else: r['samfile']=False;
            report_rows.append(r);

        report = pd.DataFrame(columns=[
            'experiment_id',
            'repository',
            'database',
            'sets',
            'sams',
            'setfile',
            'samfile'
        ]);
        for i,r in db_dat[
            ~db_dat['experiment_id'].isin(edirs['experiment_id'])
        ].iterrows():
            nr = pd.Series();
            nr['experiment_id'] = str(r['experiment_id']);
            nr['repository'] = False;
            nr['database'] = True;
            nr['sets'] = r['sets'];
            nr['sams'] = r['sams'];
            nr['setfile'] = False;
            nr['samfile'] = False;
            report_rows.append(nr);
        if len(report_rows)>0: report = pd.DataFrame(report_rows);
        return pd.DataFrame(report);




################################################################################
################################################################################
