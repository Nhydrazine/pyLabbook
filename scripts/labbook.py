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
    print("Can't import pyLabbook modules: "+str(e)+"...");
    sys.exit();
try: from pyLabbook import pyLabbook, pyProtocol;
except Exception as e:
    print("Can't import pyLabbook modules: "+str(e)+"...");
    sys.exit();
################################################################################
def usage():
    return ('''
    python labbook.py [COMMAND] [LABBOOK_ID] [PROTOCOL_IDS]...
        --sheetformat [SHEETFORMAT] --dbformat [DBFORMAT] --dbfile [DBFILE]

    Performs an action [COMMAND] on a labbook with [LABBOOK_ID] and on
    [PROTOCOL_IDS].

    [COMMAND]                   Can be any of the following:
        create ................ Creates a labbook named [LABBOOK_ID] with a
                                spreadsheet repository formatted as indicated
                                by --sheetformat option, and a database file
                                formatted as indicated by --dbformat option.
        delete ................ Deletes the labbook named [LABBOOK_ID] along
                                with its entire repository and database files.
        drop .................. Drops tables for each protocol id in argument
                                [PROTOCOL_IDS] from [LABBOOK_ID]s database.
        remove ................ Removes all folders for each protocol in
                                [PROTOCOL_IDS] from [LABBOOK_ID]s repository.

    [LABBOOK_ID]                The id of the labbook to operate on.

    [PROTOCOL_IDs]              Optional space separated list of protocol ids
                                to operate on (where applicable).

    [SHEETFORMAT]               Any spreadsheet format identifier, currently
                                xlsx and csv are available.

    [DBFORMAT]                  Any database format identifier, currently only
                                SQLITE3 is available.

    [DBFILE]                    Optional path/name of an existing database file
                                to use as this labbook's database.

    example:

       python labbook.py create myLabbook --sheetformat xlsx

    will create a labbook called myLabbook with excel-formatted repository.

    ''');
################################################################################
parser = argparse.ArgumentParser(usage=usage());
parser.add_argument(    'command',
                        type=str,
);
parser.add_argument(    'labbook',
                        type=str,
);
parser.add_argument(    'ids',
                        nargs='*',
                        default=[],
);
parser.add_argument(    '-s', '--sheetformat',
                        type=str,
                        choices=['xlsx','csv'],
                        default='xlsx',
);
parser.add_argument(    '-d', '--dbformat',
                        type=str,
                        choices=['SQLITE3'],
                        default='SQLITE3',
);
parser.add_argument(    '-f', '--dbfile',
                        type=str,
                        default=""
);
# parser.add_argument(    'arguments',
#                         nargs='+',
#                         default=[],
# );
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
def create(labbook_id, ids):
    # verify
    if not plbCore.validID(args.labbook):
        print("'"+labbook_id+"' contains invalid characters");
        sys.exit();
    # does module exist already?
    modfile = labbook_id+".py";
    modffn = os.path.join(plbLabbookRoot, modfile);

    if os.path.isfile(modffn):
        printwarn("A module already exists for "+labbook_id+".");
        print("You can delete this labbook by using the delete command.");
        sys.exit();

    if args.dbfile!="":
        if not os.path.isfile(args.dbfile):
            print("Can't find database file "+args.dbfile+"...");
            sys.exit();

    try:
        labbook = pyLabbook(
            id = labbook_id,
            root = plbRoot,
            repositoryPath = os.path.join(plbRepositoryRoot_REL,labbook_id),
            sheetFormat = args.sheetformat,
            databasePath = plbDatabaseRoot_REL,
            databaseFile = labbook_id+".sqlite3",
            databaseFormat = args.dbformat,
        );
    except Exception as e:
        print("Error initializing: "+str(e));
        sys.exit();

    serialized = labbook.exportSerialized();
    with open(modffn, 'w') as fh:
        fh.write( labbook.exportSerialized() );
    # now try to import and create structure
    try: labbook = plbCore.import_initialize_labbook(labbook_id, plbRoot);
    except Exception as e:
        print("error importing: "+str(e));
        sys.exit();
    try: labbook.createFileStructure();
    except Exception as e:
        print("error creating repository: "+str(e));
        sys.exit();
    if args.dbfile!="":
        try:
            dstfile = os.path.join(
                plbRoot, labbook.databasePath, labbook.databaseFile
            );
            plbCore.copyfile( args.dbfile, dstfile );
        except Exception as e:
            print("error copying "+args.dbfile+": "+str(e));
            print("Labbook will be created with empty database.");
            print("You can copy "+args.dbfile+" manually to: \n"+dstfile);
    print("Created "+ansi.magenta+modffn+ansi.clear);
    print("Done.");
#------------------------------------------------------------------------------#
def delete(labbook_id, ids):
    # verify
    if not plbCore.validID(args.labbook):
        print("'"+labbook_id+"' contains invalid characters");
        sys.exit();
    # does module exist?
    modfile = labbook_id+".py";
    modffn = os.path.join(plbLabbookRoot, modfile);
    if not os.path.isfile(modffn):
        print("No module found for "+labbook_id+"...  Nothing to do.");
        sys.exit();
    # warn user
    printwarn(  ansi.red+"This action will delete all repository files and "+
                "databases belonging to "+labbook_id+"."+ansi.clear);
    try:
        if prompt("Are you really really sure", ['y','n'], default='n')=='n':
            print("Phew!  That would have been awful...");
            sys.exit();
    except Exception as e:
        print("Sorry, I don't understand that...  Exiting.");
        sys.exit();

    # confirm
    try:
        if prompt("Are you sure you're sure", ['y','n'], default='n')=='n':
            print("Phew!  That would have been awful...");
            sys.exit();
    except Exception as e:
        print("Sorry, I don't understand that...  Exiting.");
        sys.exit();

    # import and initialize and delete...
    try: labbook = plbCore.import_initialize_labbook(labbook_id, plbRoot);
    except Exception as e:
        print("can't import "+labbook_id+": "+str(e));
        sys.exit();

    print(  "Deleting "+ansi.magenta+labbook.id+ansi.clear+" repository: ",
            end='', flush=True);
    try: labbook.deleteFileStructure(require_empty=False);
    except Exception as e:
        print(ansi.red+"ERROR"+ansi.clear);
        print(str(e));
        sys.exit();
    print(ansi.green+"OK"+ansi.clear);

    print(  "Deleting "+ansi.magenta+modffn+ansi.clear+": ",
            end='', flush=True);
    try: os.remove(modffn);
    except Exception as e:
        print(ansi.red+"ERROR"+ansi.clear);
        print(str(e));
        sys.exit();
    print(ansi.green+"OK"+ansi.clear);

    print("Done.");
#------------------------------------------------------------------------------#
def drop(labbook_id, ids):
    if len(ids)<1:
        print("No protocol ids specified...  Nothing to do.");
        sys.exit();
    # validate ids
    if not plbCore.validID(args.labbook):
        print("'"+labbook_id+"' contains invalid characters");
        sys.exit();
    for pid in ids:
        if not plbCore.validID(pid):
            print("'"+pid+"' contains invalid characters");
            sys.exit();
    # warn user
    printwarn("About to drop the following protocol set/sample tables:");
    print(
        "\n".join([
        ansi.magenta+labbook_id+ansi.cyan+'@'+ansi.magenta+pid+ansi.clear
        for pid in ids])
    );
    print("This will delete all associated database records.");
    try:
        if prompt("is this what you want",['y','n'], default='n')=='n':
            print("Okay, exiting.");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.");
        sys.exit();
    # confirm
    try:
        if prompt("Are your really really sure",['y','n'], default='n')=='n':
            print("Okay, exiting.");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.");
        sys.exit();

    # initialize labbook and import protocols
    try:
        labbook = plbCore.import_initialize_labbook(labbook_id, plbRoot);
    except Exception as e:
        print("Error importing "+labbook_id+": "+str(e));
        sys.exit();
    print("Dropping protocol tables:");
    for pid in ids:
        print(  ansi.magenta+labbook.id+ansi.cyan+'@'+ansi.magenta+pid+
                ansi.clear+": ", end='', flush=True);
        try:
            protocol = plbCore.import_initialize_protocol(pid, labbook);
        except Exception as e:
            print(ansi.red+"ERROR"+ansi.clear);
            print("couldn't initialize: "+str(e));
            continue;

        protocol.connect();
        try:
            protocol.dropSetSampleTables();
        except Exception as e:
            print(ansi.red+"ERROR"+ansi.clear);
            print("Couldn't drop tables: "+str(e));
            continue;
        protocol.disconnect();
        print(ansi.green+"OK"+ansi.clear);

    print("Done.");
#------------------------------------------------------------------------------#
def remove(labbook_id, ids):
    if len(ids)<1:
        print("No protocol ids specified...  Nothing to do.");
        sys.exit();
    # validate ids
    if not plbCore.validID(args.labbook):
        print("'"+labbook_id+"' contains invalid characters");
        sys.exit();
    for pid in ids:
        if not plbCore.validID(pid):
            print("'"+pid+"' contains invalid characters");
            sys.exit();
    # warn user
    printwarn("About to remove repository paths for:");
    print(
        "\n".join([
        ansi.magenta+labbook_id+ansi.cyan+'@'+ansi.magenta+pid+ansi.clear
        for pid in ids])
    );
    print(  "This will delete ALL associated files and subfolders including +"
            "raw data files.");
    try:
        if prompt("is this what you want",['y','n'], default='n')=='n':
            print("Okay, exiting.");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.");
        sys.exit();
    # confirm
    try:
        if prompt("Are your really really sure",['y','n'], default='n')=='n':
            print("Okay, exiting.");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.");
        sys.exit();

    # initialize labbook and import protocols
    try:
        labbook = plbCore.import_initialize_labbook(labbook_id, plbRoot);
    except Exception as e:
        print("Error importing "+labbook_id+": "+str(e));
        sys.exit();
    print("Removing protocol paths:");
    for pid in ids:
        try:
            protocol = plbCore.import_initialize_protocol(pid, labbook);
        except Exception as e:
            print(ansi.red+"ERROR"+ansi.clear);
            print("couldn't initialize: "+str(e));
            continue;

        print("Deleting path "+ansi.green+protocol.protocolroot()+ansi.clear+
                ": ", end='', flush=True);
        try:
            plbCore.rmpath(protocol.protocolroot(), require_empty=False);
        except Exception as e:
            print(ansi.red+"ERROR"+ansi.clear);
            print("Couldn't delete: "+str(e));
            continue;
        print(ansi.green+"OK"+ansi.clear);

    print("Done.");

################################################################################
# Argument Processing
################################################################################
# dict of available commands mapped to their function refs
command_map = {
    'create'            : create,
    'delete'            : delete,
    'drop'              : drop,
    'remove'            : remove,
};
# validate command
if not args.command in command_map.keys():
    print("Unrecognized command '"+args.command+"'...");
    sys.exit();
# validate labbook
if not plbCore.validID(args.labbook):
    print("'"+args.labbook+"' contains invalid characters");
    sys.exit();
# call command
command_map[args.command](args.labbook, args.ids);





















#
