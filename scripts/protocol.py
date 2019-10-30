import sys, os;
import numpy as np, pandas as pd;
import argparse;
################################################################################
root = sys.path[0];
plbRoot = os.path.normpath(os.path.join(root,'..'));
plbPythonRoot = os.path.join(plbRoot,'python');
plbProtocolRoot = os.path.join(plbPythonRoot,'pyLabbook','protocols');
plbLabbookRoot = os.path.join(plbPythonRoot,'pyLabbook','labbooks');
plbRepositoryRoot_REL = 'repositories';
plbDatabaseRoot_REL = 'databases';
################################################################################
sys.path.append(plbPythonRoot);
try: import pyLabbook.core as plbCore;
except Exception as e:
    print("Can't import pyLabbook core: "+str(e)+"...");
    sys.exit();
try: from pyLabbook import pyLabbook, pyProtocol;
except Exception as e:
    print("Can't import pyLabbook modules: "+str(e)+"...");
    sys.exit();
################################################################################
def usage():
    return ('''
    python protocol.py [COMMAND] [PROTOCOL_ID]


    Performs an action [COMMAND] on a protocol with [PROTOCOL_ID].

    [COMMAND]                   Can be any of the following:
        initialize ............ Initializes set and sample description files for
                                a new protocol [PROTOCOL_ID].  These are csv
                                formatted spreadsheets created in the current
                                folder.  Each row in the SET_DESC and SAMPLE_
                                DESC spreadsheets represents a database column
                                and the headers are column options.  Fill out
                                these forms and use the "create" option to
                                make a protocol module.  See section on column
                                options below for a description of how to fill
                                out these forms.
        create ................ Constructs a protocol module for [PROTOCOL_ID]
                                using SET_DESC and SAMPLE_DESC forms created
                                by "initialize" command.
        delete ................ Deletes the protocol module for [PROTOCOL_ID],
                                note that to access any data for this protocol
                                the module will have to be recreated exactly.

    [PROTOCOL_ID]               Any valid protocol id.

    Example:

        python protocol.py initialize myProtocol

    will generate myProtocol_SET_DESC.csv and myProtocol_SAMPLE_DESC.csv files
    that you fill out to describe the SET and SAMPLE tables for myProtocol.
    Once these forms are completed run:

        python protocol.py create myProtocol

    to create the protocol module for myProtocol.

    COLUMN OPTIONS (filling out SET and SAMPLE description forms)

        Fill out the SET_DESC and SAMPLE_DESC csv files using the following
        under each column header in the files:

        name .................. Name for the table column, no spaces or special
                                characters.
        type .................. Data type for column.  Valid options are TEXT,
                                INTEGER, REAL, NUMERIC, DATE.
        notnull ............... Is a value always required? TRUE or FALSE.
        unique ................ Does every value in this column have to be
                                unique? TRUE or FALSE.
        description ........... A text descripton of your column.
        default ............... Default value to use if no value supplied, if
                                applicable.
        primary_key ........... Include column in table's compound primary key?
                                TRUE of FALSE.  If unsure, use FALSE.

    ''');
################################################################################
parser = argparse.ArgumentParser(usage=usage());
parser.add_argument(    'command',
                        type=str,
);
parser.add_argument(    'protocol',
                        type=str,
);
args = parser.parse_args();
################################################################################
# Prompts
################################################################################
class ansi:
    black       = "\033[0;30m";
    red         = "\033[0;31m";
    green       = "\033[0;32m";
    brown       = "\033[0;33m";
    blue        = "\033[0;34m";
    magenta     = "\033[0;35m";
    cyan        = "\033[0;36m";
    br_gray     = "\033[0;37m";
    dk_gray     = "\033[1;30m";
    br_red      = "\033[1;31m";
    br_green    = "\033[1;32m";
    yellow      = "\033[1;33m";
    br_blue     = "\033[1;34m";
    br_magenta  = "\033[1;35m";
    br_cyan     = "\033[1;36m";
    br_white    = "\033[1;37m";
    bold        = "\033[1m";
    faint       = "\033[2m";
    italic      = "\033[3m";
    underline   = "\033[4m";
    blink       = "\033[5m";
    invert      = "\033[7m";
    clear       = "\033[0m";
def prompt_yesno(msg, default='y', tries=3):
    pt = "[";
    if default=="y": pt += ansi.green+"Y"+ansi.clear;
    else: pt += "y";
    pt += "/";
    if default=="n": pt += ansi.green+"N"+ansi.clear;
    else: pt += "n";
    pt += "] ?";
    for current_try in range(0,tries):
        print(msg+" "+pt+" ", end='', flush=True);
        response = input();
        if 'Y' in response.upper() and 'N' not in response.upper():
            return True;
        if 'N' in response.upper() and 'Y' not in response.upper():
            return False;
    raise Exception("Error: maximum attempts for an acceptable reponse was reached.");
def prompt(msg, options, default="", tries=3,tag=ansi.br_blue+"-> "+ansi.clear):
    ptopts = [];
    for opt in options:
        if opt==default: ptopts.append(ansi.green+opt.upper()+ansi.clear);
        else: ptopts.append(opt);
    for current_try in range(0,tries):
        print(tag+msg+" ["+'/'.join(ptopts)+"] ? ", end="", flush=True);
        response = input().replace("\n","");
        if response=="" and default!="": return default;
        if response in options: return response.lower();
    raise Exception("Error: maximum attempts for an acceptable reponse was reached.");
def printwarn(msg): print("("+ansi.br_magenta+"WARNING"+ansi.clear+") "+msg);
################################################################################
def validate_eids(eids):
    if len(eids)<1:
        print("No experiment ids found, nothing to do.");
        sys.exit();
    for eid in eids:
        if not plbCore.validID(eid):
            print("Experiment id '"+eid+"' contains invalid characters.");
            sys.exit();
def lpe(labbook, protocol, experiment_id):
    return str(ansi.magenta+labbook.id+ansi.cyan+'@'+ansi.magenta+
                protocol.PROTOCOLID+' '+ansi.green+experiment_id+ansi.clear);
################################################################################
# Command Functions
################################################################################
def initialize(protocol_id):
    # verify id
    if not plbCore.validID(protocol_id):
        print("'"+protocol_id+"' contains invalid characters");
        sys.exit();
    # check for no module
    modfile = protocol_id+".py";
    modffn = os.path.join(plbProtocolRoot,modfile);
    if os.path.isfile(modffn):
        print("There is already a module for "+protocol_id+"...");
        print("Exiting.");
        sys.exit();
    # dummy labbook object
    try:
        dummy_labbook = pyLabbook(
            id="dummy",
            root=plbRoot,
            repositoryPath=plbRoot,
            sheetFormat='csv',
            databasePath=plbRoot,
            databaseFile="temp.sqlite3",
            databaseFormat='SQLITE3',
        );
    except Exception as e:
        print("Error initializing placeholder pyLabbook: "+str(e));
        sys.exit();
    # initialize empty protocol
    try: protocol = pyProtocol( dummy_labbook );
    except Exception as e:
        print("Error initializing empty pyProtocol: "+str(e));
        sys.exit();
    # get empty set and sample descriptions
    set_desc = pd.DataFrame( columns=protocol.setDesc().columns );
    sam_desc = pd.DataFrame( columns=protocol.samDesc().columns );
    # save csv format only
    outfile_setdesc = os.path.join(root, protocol_id+"_SET_DESC.csv");
    outfile_samdesc = os.path.join(root, protocol_id+"_SAMPLE_DESC.csv");

    if os.path.isfile(outfile_setdesc):
        print(  "There is already a set description called "+
                outfile_setdesc+"...");
        sys.exit();
    print(  "Writing to "+ansi.green+outfile_setdesc+ansi.clear+
            ": ", end='', flush=True);
    try: set_desc.to_csv(outfile_setdesc, index=False, header=True);
    except Exception as e:
        print(ansi.red+"ERROR"+ansi.clear);
        print(str(e));
        sys.exit();
    print(ansi.green+"OK"+ansi.clear);

    if os.path.isfile(outfile_samdesc):
        print(  "There is already a set description called "+
                outfile_samdesc+"...");
        sys.exit();
    print(  "Writing to "+ansi.green+outfile_samdesc+ansi.clear+
            ": ", end='', flush=True);
    try: sam_desc.to_csv(outfile_samdesc, index=False, header=True);
    except Exception as e:
        print(ansi.red+"ERROR"+ansi.clear);
        print(str(e));
        sys.exit();
    print(ansi.green+"OK"+ansi.clear);

    print("Fill out these forms and use the "+ansi.br_cyan+"create"+
            ansi.clear+" command to create "+protocol_id+".");
#------------------------------------------------------------------------------#
def create(protocol_id):
    # verify id
    if not plbCore.validID(protocol_id):
        print("'"+protocol_id+"' contains invalid characters");
        sys.exit();
    # check set/sam description files
    file_setdesc = os.path.join(root, protocol_id+"_SET_DESC.csv");
    file_samdesc = os.path.join(root, protocol_id+"_SAMPLE_DESC.csv");

    print(  "Checking for "+ansi.green+file_setdesc+ansi.clear+": ",
            end='', flush=True);
    if not os.path.isfile(file_setdesc):
        print(ansi.red+"NOT FOUND"+ansi.clear);
        sys.exit();
    print(ansi.green+"OK"+ansi.clear);

    print(  "Checking for "+ansi.green+file_samdesc+ansi.clear+": ",
            end='', flush=True);
    if not os.path.isfile(file_samdesc):
        print(ansi.red+"NOT FOUND"+ansi.clear);
        sys.exit();
    print(ansi.green+"OK"+ansi.clear);

    # check for existing module file
    modfile = protocol_id+".py";
    modffn = os.path.join(plbProtocolRoot,modfile);
    if os.path.isfile(modffn):
        print("There is already a module for "+protocol_id+"...");
        print("Exiting.");
        sys.exit();

    # load and check records
    setdesc = pd.read_csv(file_setdesc, index_col=None, header=0);
    samdesc = pd.read_csv(file_samdesc, index_col=None, header=0);
    if len(setdesc)==0:
        print("Set description is empty...  Nothing to do.");
        sys.exit();
    # empty sample description is okay.

    # dummy labbook object
    try:
        dummy_labbook = pyLabbook(
            id="dummy",
            root=plbRoot,
            repositoryPath=plbRoot,
            sheetFormat='csv',
            databasePath=plbRoot,
            databaseFile="temp.sqlite3",
            databaseFormat='SQLITE3',
        );
    except Exception as e:
        print("Error initializing placeholder pyLabbook: "+str(e));
        sys.exit();

    # initialize empty protocol
    try: protocol = pyProtocol( dummy_labbook );
    except Exception as e:
        print("Error initializing empty pyProtocol: "+str(e));
        sys.exit();

    protocol.PROTOCOLID = protocol_id;

    # confirm set/sample description columns
    desc_columns = pd.Series(
        protocol.setDesc().columns.sort_values().tolist()
    );

    if not (
        pd.Series(setdesc.columns.sort_values().tolist()) ==
        desc_columns
    ).all():
        print("Set description file contains invalid or missing columns...");
        print("Exiting.");
        sys.exit();

    if not (
        pd.Series(samdesc.columns.sort_values().tolist()) ==
        desc_columns
    ).all():
        print("Sample description file contains invalid or missing columns...");
        print("Exiting.");
        sys.exit();


    # TODO: need a more universal way to deal with these casting issues
    # a little data formatting and type enforcement
    for df in [setdesc, samdesc]:
        # preliminary casting
        df['notnull'] = df['notnull'].astype(str);
        df['unique'] = df['unique'].astype(str);
        df['primary_key'] = df['primary_key'].astype(str);
        for i,r in df.iterrows():
            # casting for more complicated issues... --> np.nan's...
            # set all pd.null's to "" and let SQL engine figure it out.
            if pd.isnull(r['default']): df.loc[i,'default'] = "";
            # convert ALL string values manually to avoid "nan"
            # TODO: more elegant solution for this...
            for strcol in ['description','name','type']:
                if pd.isnull(r[strcol]): df.loc[i,strcol] = "";
            # true/false
            for boolcol in ['notnull','unique','primary_key']:
                if str(r[boolcol]).upper()=="TRUE" or r[boolcol]=="1":
                    df.loc[i, boolcol] = True;
                elif str(r[boolcol]).upper()=="FALSE" or r[boolcol]=="0":
                    df.loc[i, boolcol] = False;
                else:
                    print("Invalid boolean identifier: "+r[boolcol]+".");
                    sys.exit();
        # last minute formatting
        df['type'] = df['type'].str.upper();

    # build protocol
    protocol.id = protocol_id;
    for table in ['set','sam']:
        if table=='set':
            df = setdesc;
            addColumn = protocol.addSetColumn;
            print("Building set description:");
        if table=='sam':
            df = samdesc;
            addColumn = protocol.addSamColumn;
            print("Building sample description:");
        if len(df)<1:
            print("\tNo columns to process...");
            continue;
        for i,r in df.iterrows():
            # build keyword args and use addSetColumn
            kwa = {};
            for k in desc_columns:
                # special case for default
                if k=='default' and r[k]=='': kwa[k] = None;
                # otherwise just map
                else: kwa[k] = r[k];
            print(  "\t"+ansi.magenta+str(r['name'])+ansi.clear+": ",
                    end='', flush=True);
            try: addColumn(**kwa);
            except Exception as e:
                print(ansi.red+"ERROR"+ansi.clear);
                print(str(e));
                sys.exit();
            print(ansi.green+"OK"+ansi.clear);
    print("Serializing...");
    serialized = protocol.exportSerialized();
    print("Writing to "+ansi.green+modffn+ansi.clear+": ", end="", flush=True);
    try:
        with open(modffn, 'w') as fh:
            fh.write(serialized);
    except Exception as e:
        print(ansi.red+"ERROR"+ansi.clear);
        print(str(e));
        sys.exit();
    print(ansi.green+"OK"+ansi.clear);
    print("Done.");

#------------------------------------------------------------------------------#
def delete(protocol_id):
    # verify id
    if not plbCore.validID(protocol_id):
        print("'"+protocol_id+"' contains invalid characters");
        sys.exit();
    # check for no module
    modfile = protocol_id+".py";
    modffn = os.path.join(plbProtocolRoot,modfile);
    if not os.path.isfile(modffn):
        print("Can't find a module for "+protocol_id+"...");
        print("Exiting.");
        sys.exit();
    # warn user
    printwarn(  "Without a module file for "+protocol_id+" you will "+
                ansi.br_red+"NOT"+ansi.clear+" be able to access any of its "+
                "data in any labbook.");
    printwarn(  "You will have to recreate this module exactly, to access "+
                "those data.");
    try:
        rsp = prompt(
            "Are you really sure you want to do this",['y','n'], default='n');
        if rsp=='n':
            print("Phew! That was close...");
            sys.exit();
    except Exception as e:
        print("Sorry, I don't understand that...");
        sys.exit();

    # one more time
    try:
        rsp = prompt(
            "Seriously",['y','n'], default='n');
        if rsp=='n':
            print("Wow! That was really close...");
            sys.exit();
    except Exception as e:
        print("Sorry, I don't understand that...");
        sys.exit();

    print(  ansi.red+"DELETING PROTOCOL MODULE "+ansi.br_red+protocol_id+
            ansi.red+"..."+ansi.clear);
    try: plbCore.rmfile( modffn );
    except Exception as e:
        print("Error deleting "+modffn+": "+str(e));
        sys.exit();
    print("Successfully deleted "+modffn+".");
    print("Done");

#------------------------------------------------------------------------------#





################################################################################
# Argument Processing
################################################################################
# dict of available commands mapped to their function refs
command_map = {
    'initialize'        : initialize,
    'create'            : create,
    'delete'            : delete,
};
# validate command
if not args.command in command_map.keys():
    print("Unrecognized command '"+args.command+"'...");
    sys.exit();
# validate labbook
if not plbCore.validID(args.protocol):
    print("'"+args.protocol+"' contains invalid characters");
    sys.exit();
# call command
command_map[args.command](args.protocol);





















#
