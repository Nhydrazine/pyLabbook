import os, sys, re, shutil;
import numpy as np, pandas as pd;
# CORE FUNCTIONS
sheet_formats = ['xlsx','csv'];

def test(msg): print(str(msg));

def write_dataframe(ffn, format, df, sheet="Sheet1", overwrite=False):
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
#return df.copy().fillna(np.nan).replace("",np.nan);

def makepath(path, on_exists='ignore'):
    # available on_exists options are 'ignore' or 'raise'
    if os.path.isdir(path):
        if on_exists=='raise':
            raise Exception(str(path) + " already exists");
        elif on_exists=='ignore':
            return False;
    else:
        os.makedirs(path);
        return True;

def rmfile(ffn):
    os.remove(ffn);

def rmpath(path, require_empty=True):
    if require_empty: os.rmdir(path);
    else: shutil.rmtree(path, ignore_errors=False);

def ispath(path):
    return os.path.isdir(path);

def isfile(ffn):
    return os.path.isfile(ffn);

def validID(i):
    rx = re.compile(r'^[A-Z,a-z,0-9,\-,\_]+$');
    if not rx.match(i): return False;
    else: return True;

def listDirs(path):
    if not ispath(path): return pd.DataFrame(columns=['experiment_id']);
    return pd.DataFrame({'experiment_id': next(os.walk( path ) )[1]});

def copyfile(src,dst):
    shutil.copyfile(src, dst);



# PROPERTIES AND THINGS ########################################################

# > Definition, link between SQLITE3 data types and python data types
# This is done in the SQL engine file

# FILE SYSTEM OPERATIONS #######################################################

# > Load spreadsheet file of varying formats and return as pd.DataFrame
#   caller will have to load multiple and append if spread across experiments

# > Store pd.DataFrame to a file of given format
#   caller has to split DataFrame by experiment ID for different files...

# > Delete file(s)

# > Create path

# DATABASE OPERATIONS ##########################################################
# All database routines will return a list of SQRs that can be executed by the caller later.  This is how transactions will be implemented.  This will be true for all functions EXCEPT the two selecting functions.  The selecting functions will simply return the results directly, as a pandas.DataFrame.

# > Select sets given multiple LOCS and return as dataframe

# > Select sams given multiple LOCS and return as dataframe

# > Insert/Update sets from DataFrame (delete/insert, overwrite options)

# > Insert/Update samples from DataFrame (delete/insert, overwrite option)

# > Delete sets given LOCS

# > Delete samples given LOCS

# > Connect to Database (uses the SQL function below?)

# > Close/disconnect from Database (NO, SPECIFIC, SO PUT IN SQL BELOW)

# > Create set table if not exist

# > Create sample table if not exist

# > Execute SQR (transaction)
