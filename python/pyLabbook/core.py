import os, sys, re, shutil, importlib;
import numpy as np, pandas as pd;
"""pyLabbook.core functions primarily serve as an interface to filesystem operations but also include functions that are intended to be globally used and not specifically associated with a labbook or protocol."""

# acceptable sheet formats
sheet_formats = ['xlsx','csv'];

def import_initialize_protocol(protocol_id, labbook):
    """Import and initialize a protocol with given labbook.

    Parameters
    ----------
    protocol_id : str
        Id of the protocol to import and initialize.
    labbook : pyLabbook.pyLabbook object
        Labbook to initialize the protocol with.

    Returns
    -------
    pyLabbook.pyProtocol object
        An initialized instance of the request protocol linked to the specified
        labbook.

    """
    # validate labbook object
    if not ispath(labbook.root):
        raise Exception("Root for labbook doesn't appear to exist.");
    if not validID(protocol_id):
        raise Exception(str(protocol_id)+" is invalid.");
    mp = '.'.join(['pyLabbook','protocols',protocol_id]);
    try: import_module_path(mp);
    except Exception as e:
        raise Exception("Could't import "+mp+": "+str(e));
    try: return call_module(mp).initialize(labbook);
    except Exception as e:
        raise Exception("Couldn't initialize "+mp+": "+str(e));
    return None;

def import_initialize_labbook(labbook_id, root):
    """Imports and initialize a labbook.

    Parameters
    ----------
    labbook_id : str
        id of the labbook to import and initialize.
    root : str
        Path to pyLabbook root

    Returns
    -------
    pyLabbook.pyLabbook object
        An initialized instance of the appropriate pyLabbook object.

    """
    if not validID(labbook_id):
        raise Exception(str(labbook_id)+" is invalid");
    mp = '.'.join(['pyLabbook','labbooks',labbook_id]);
    try: import_module_path(mp);
    except Exception as e:
        raise Exception("Could't import "+mp+": "+str(e));
    try: return call_module(mp).initialize(root);
    except Exception as e:
        raise Exception("Couldn't initialize "+mp+": "+str(e));
    return None;

def import_module_path(modpath):
    """Imports a module defined by modpath if not already imported."""
    if modpath not in sys.modules:
        importlib.import_module(modpath);
        return True;
    else:
        return False;

def call_module(modpath):
    """Returns an instance of a module defined by modpath."""
    return sys.modules[modpath];

def write_dataframe(ffn, format, df, sheet="Sheet1", overwrite=False):
    """Writes a pandas.DataFrame to a file with given format.

    Parameters
    ----------
    ffn : str
        Full path and name of file to output to.
    format : str
        'xlsx' or 'csv' format.
    df : pandas.DataFrame
        Data to write.
    sheet : str
        Name of sheet in output file (for xlsx).  Default is "Sheet1"
    overwrite : bool
        Overwrite if file exists? (True), default is False.

    Returns
    -------
    None

    """
    if not overwrite:
        if os.path.isfile(ffn):
            raise Exception("Can't overwrite " + str(ffn));
    if format=='xlsx':
        # use pandas ExcelWriter
        xw = pd.ExcelWriter(ffn);
        df.to_excel(xw, sheet, index=False, na_rep='');
        xw.save();
        xw.close();
    elif format=='csv':
        # use pandas to_csv
        df.to_csv(ffn, index=False);
    else:
        raise Exception("Unrecognized format " + str(format));

def load_dataframe(ffn, format, sheet="Sheet1"):
    """Loads a spreadsheet file into a pandas.DataFrame.

    Parameters
    ----------
    ffn : str
        Full path and name of spreadsheet file to import
    format : str
        'xlsx' or 'csv' for file format.
    sheet : str
        Name of sheet to import (for xlsx).  Default "Sheet1".

    Returns
    -------
    pandas.DataFrame
        The spreadsheet data.

    """
    if not os.path.isfile(ffn):
        raise Exception("Can't find " + str(ffn));
    if format=='xlsx':
        # use pandas ExcelFile
        xl = pd.ExcelFile(ffn);
        if sheet not in xl.sheet_names:
            xl.close();
            raise Exception(
                "Can't find sheet " + str(sheet) + " in file " + str(ffn));
        df = xl.parse(sheet, index_col=None);
        return df;
    elif format=='csv':
        df = pd.read_csv(ffn, index_col=None);
        return df;
    else:
        raise Exception("Unrecognized format " + str(format));

def makepath(path, on_exists='ignore'):
    """Make a folder path and it's containing tree if necessary.

    Parameters
    ----------
    path : str
        Full path to create
    on_exists : bool
        'ignore' if path already exists, or 'raise' an error.

    Returns
    -------
    bool
        True if created or False if exists and ignored.

    """
    if os.path.isdir(path):
        if on_exists=='raise':
            raise Exception(str(path) + " already exists");
        elif on_exists=='ignore':
            return False;
    else:
        os.makedirs(path);
        return True;

def rmfile(ffn):
    """Remove a full path/filename."""
    os.remove(ffn);

def rmpath(path, require_empty=True):
    """Remove a complete folder path.  Use require_empty to raise if files
    exist."""
    if require_empty: os.rmdir(path);
    else: shutil.rmtree(path, ignore_errors=False);

def ispath(path):
    """Is path an existing directory? True or False."""
    return os.path.isdir(path);

def isfile(ffn):
    """Is ffn an existing file? True or False."""
    return os.path.isfile(ffn);

def validID(i):
    """Is i a valid labbook, protocol, or experiment id? True or False."""
    rx = re.compile(r'^[A-Z,a-z,0-9,\-,\_]+$');
    if not rx.match(i): return False;
    else: return True;

def listDirs(path):
    """Lists all the folders contained at path.  Returns a pandas.DataFrame
    of folders under the column 'experiment_id'.  This is primarily used to
    list experiments in a repository.  MAKE THIS MORE CLEAR."""
    if not ispath(path): return pd.DataFrame(columns=['experiment_id']);
    return pd.DataFrame({'experiment_id': next(os.walk( path ) )[1]});

def copyfile(src,dst):
    """Copies the file src to dst."""
    shutil.copyfile(src, dst);
