import sys, os;
import numpy as np, pandas as pd;
import argparse;
################################################################################
root = sys.path[0];
plbRoot = os.path.normpath(os.path.join(root,'..'));
plbPythonRoot = os.path.join(plbRoot,'python');
plbProtocolRoot = os.path.join(plbPythonRoot,'pyLabbook','protocols');
plbLabbookRoot = os.path.join(plbPythonRoot,'pyLabbook','labbooks');
################################################################################
sys.path.append(plbPythonRoot);
try: import pyLabbook.core as plbCore;
except Exception as e:
    print("Can't import pyLabbook modules: "+str(e)+"...");
    sys.exit();
################################################################################
def usage():
          #####################################################################
    return ('''
    python experiments.py [COMMAND] [SOURCE] [id] [id] [id]...

    Performs an action (COMMAND) on a space separated series of experiment ids
    (id) that belong to a labbook and protocol (SOURCE).

    example:

       python experiments.py myLabbook@someProtocol store EXP1 EXP2

    Will store repository data for experiments EXP1 and EXP2 in labbook
    myLabbook and protocol someProtocol into the labbook's database.

    SOURCE                      is formatted as LABBOOK_ID@PROTOCOL_ID
    COMMAND                     can be any of the following:
       store .................. stores data from repository files into the
                                labbook database.
       restore ................ restores repository files using records from
                                the database.
       initialize ............. initializes repository path/files for
                                experiment ids.
       drop ................... deletes all experiment records from database
                                (sets and samples).
       delete_files ........... deletes repository set and sample files.
       delete_path ............ deletes repository path for experiment
                                including all files contianed in the path.
    ''');

################################################################################
parser = argparse.ArgumentParser(usage=usage());
parser.add_argument(    'command',
                        type=str,
);
parser.add_argument(    'source',
                        type=str,
);
parser.add_argument(    'arguments',
                        nargs='+',
                        default=[],
);
parser.add_argument(    '-o',
                        action='store_true',
                        default=False,
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
    raise Exception(    "Error: maximum attempts for an acceptable reponse was"+
                        "reached.");
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
    raise Exception(    "Error: maximum attempts for an acceptable reponse was"+
                        "reached.");
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
def store(labbook, protocol, cargs):
    """Store repository records into database for a list of experiment ids
    (cargs)."""
    # parse and verify experiment ids
    validate_eids(cargs);
    # confirm ids
    print("About to store repository files using database for experiments: ");
    print("\n".join([lpe(labbook, protocol, eid) for eid in cargs]));
    try:
        if prompt("Proceed", ['y','n'], default='y')=='n':
            print("Okay, exiting...");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.  Exiting...");
        sys.exit();
    print();
    # check for initialized repository
    remove_eids = {};
    for eid in cargs:
        if not protocol.experimentPathExists(eid):
            remove_eids[eid] = "not initialized";
        else:
            if not protocol.setFileExists(eid):
                remove_eids[eid] = "no set file";
    if len(remove_eids.keys())>0:
        printwarn("The following experiments will be skipped:");
        print("\n".join([
            lpe(labbook, protocol, eid)+": "+remove_eids[eid]
            for eid in remove_eids.keys()
        ]));
        print("Continuing...");
        print();
    cargs = [ eid for eid in cargs if not eid in remove_eids.keys() ];

    if len(cargs)<1:
        print("No experiments to work on...");
        print("Exiting.");
        sys.exit();

    # now check for empty set files
    empty_eids = [];
    for eid in cargs:
        sets = protocol.loadSetFile([eid]);
        if len(sets)<1:
            empty_eids.append(eid);
    if len(empty_eids)>0:
        printwarn("The following experiments are empty:");
        print("\n".join([
            lpe(labbook, protocol, eid) for eid in empty_eids
        ]));
        print("if you continue, the database records will be deleted.");
        try:
            if prompt("Proceed", ['y','n'], default='n')=='n':
                print("Okay, exiting...");
                sys.exit();
        except Exception as e:
            print("Sorry, I didn't understand that.  Exiting...");
            sys.exit();
        print();
    # check for database
    protocol.connect();
    protocol.createTables(); # if necessary
    if not args.o:
        wheres = pd.DataFrame({'experiment_id': cargs});
        sets = protocol.selectSetsWhere(wheres);
        existing_eids = [];
        for eid in cargs:
            if eid in sets['experiment_id'].tolist():
                existing_eids.append(eid);
        if len(existing_eids)>0:
            printwarn("The following experiments have database records:");
            print("\n".join([
                (
                    lpe(labbook, protocol, eid)+" ("+ansi.cyan+
                    str(len(sets[sets['experiment_id']==eid]))+
                    ansi.clear+" sets)"
                ) for eid in existing_eids
            ]));
            print("if you continue these records will be overwritten...");
            try:
                if prompt("Proceed", ['y','n'], default='n')=='n':
                    print("Okay, exiting...");
                    protocol.disconnect();
                    sys.exit();
            except Exception as e:
                print("Sorry, I didn't understand that.  Exiting...");
                protocol.disconnect();
                sys.exit();
            args.o = True;
    print();
    # go!
    errs = 0;
    for eid in cargs:
        print(lpe(labbook, protocol, eid), end="", flush=True);
        try: sets = protocol.loadSetFile([eid]);
        except Exception as e:
            errs += 1;
            print(": "+ansi.red+"ERROR LOADING SET FILE"+ansi.clear);
            print(str(e));
            print();
            continue;
        try: sams = protocol.loadSamFile([eid]);
        except Exception as e:
            errs += 1;
            print(": "+ansi.red+"ERROR LOADING SAMPLE FILE"+ansi.clear);
            print(str(e));
            print();
            continue;
        print(  " ("+ansi.br_cyan+str(len(sets))+ansi.clear+"/"+
                ansi.cyan+str(len(sams))+ansi.clear+"): ", end='', flush=True);
        try: protocol.storeSetsAndSamples(sets, sams, method='killreplace');
        except Exception as e:
            errs += 1;
            print(ansi.red+"ERROR"+ansi.clear);
            print(str(e));
            print();
            continue;
        print(ansi.green+"OK"+ansi.clear);
    protocol.disconnect();
    if errs==0:
        print("Success!");
    else:
        print("I did what I could...");
#------------------------------------------------------------------------------#
def restore(labbook, protocol, cargs):
    """Restore repository files from database for a list of experiment ids
    (cargs)."""
    # parse and verify experiment ids
    validate_eids(cargs);
    # confirm ids
    print("About to restore repository files using database for experiments: ");
    print("\n".join([lpe(labbook, protocol, eid) for eid in cargs]));
    try:
        if prompt("Proceed", ['y','n'], default='y')=='n':
            print("Okay, exiting...");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.  Exiting...");
        sys.exit();
    print();
    # check for existing repository if overwrite off
    if not args.o:
        existing_eids = [];
        for eid in cargs:
            if os.path.isfile(protocol.setFile(eid)):
                existing_eids.append(eid);
        if len(existing_eids)>0:
            printwarn("The following experiments have repository files:");
            print("\n".join([
                lpe(labbook, protocol, eid)
                for eid in existing_eids
            ]));
            print("if you continue, any data in these files will be "+
                "replaced...");
            try:
                if prompt("Proceed", ['y','n'], default='n')=='n':
                    print("Okay, exiting...");
                    sys.exit();
            except Exception as e:
                print("Sorry, I didn't understand that.  Exiting...");
                sys.exit();
        # turn overwite on
        args.o = True;
    print();
    # check database
    protocol.connect();
    wheres = pd.DataFrame({'experiment_id': cargs});
    sets = protocol.selectSetsWhere(wheres);
    empty_experiments = [];
    for eid in cargs:
        if len(sets[sets['experiment_id']==eid])<1:
            empty_experiments.append(eid);
    if len(empty_experiments)>0:
        printwarn("The following experiments have no database records:");
        print("\n".join([
            "\n".join(lpe(labbook, protocol, eid) for eid in empty_experiments)
        ]));
        print(  "you can "+
                "["+ansi.br_green+"Q"+ansi.clear+"]uit, "+
                "["+ansi.br_green+"S"+ansi.clear+"]kip these experiments or "+
                "["+ansi.br_green+"O"+ansi.clear+"]verwrite these repository "+
                "data...");
        try:
            rsp = prompt("what would you like to do",
                ['q','s','o'],
                default='q');
        except Exception as e:
            print("Sorry, I didn't understand that.  Exiting...");
            protocol.disconnect();
            sys.exit();
        if rsp=='q':
            print("Okay, exiting...");
            sys.exit();
        elif rsp=='s':
            print("Removing them from the list...");
            cargs = [ eid for eid in cargs if not eid in empty_experiments ];
        elif rsp=='o':
            print(ansi.red+"Will replace repository records with database "+
                "records."+ansi.clear);
            args.o = True;
    print();
    # okay, ready to go
    errs = 0;
    for eid in cargs:
        # make full path if not exist
        if not os.path.isdir( protocol.experimentPath(eid) ):
            plbCore.makepath( protocol.experimentPath(eid) );
        set_ss = sets[sets['experiment_id']==eid];
        wheres = pd.DataFrame({'experiment_id': [eid]});
        sams = protocol.selectSamsWhere(wheres);
        print(  lpe(labbook, protocol, eid)+" "+
                "("+ansi.br_cyan+str(len(set_ss))+ansi.clear+"/"+
                ansi.cyan+str(len(sams))+ansi.clear+"): ", end="", flush=True);
        try:
            protocol.writeSets(set_ss, eid);
        except Exception as e:
            errs+=1;
            print(ansi.red+"ERROR"+ansi.clear);
            print("Error writing set file: "+str(e));
            print();
            continue;
        try:
            protocol.writeSams(sams, eid);
        except Exception as e:
            errs+=1;
            print(ansi.red+"ERROR"+ansi.clear);
            print("Error writing sample file: "+str(e));
            print();
            continue;
        print(ansi.green+"OK"+ansi.clear);
    if errs==0:
        print("Success!");
    else:
        print("I did what I could...");
#------------------------------------------------------------------------------#
def initialize(labbook, protocol, cargs):
    """Initialize experiment ids from a list of experiment ids (cargs)."""
    # parse and verify experiment ids
    validate_eids(cargs);
    #confirm ids
    print("About to initialize the following experiment ids:");
    print("\n".join([lpe(labbook, protocol, eid) for eid in cargs]));
    try:
        if prompt("Proceed", ['y','n'], default='y')=='n':
            print("Okay, exiting...");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.  Exiting...");
        sys.exit();
    print();
    # check if repositories exist
    if not args.o:
        protocol.createFileStructure(); # if necessary
        existing_experiments = [];
        for eid in cargs:
            if protocol.experimentPathExists(eid):
                existing_experiments.append(eid);
        if len(existing_experiments)>0:
            print("The following experiments already have repository paths:");
            print("\n".join([
                lpe(labbook,protocol,eid)
                for eid in existing_experiments
            ]));
            try:
                if prompt("Should I overwrite",['y','n'],default='n')=='n':
                    print("Okay, exiting...");
                    sys.exit();
                print(ansi.red+"Okay, will overwrite these "+
                "experiments..."+ansi.clear);
            except Exception as e:
                print("Sorry, I didn't understand that.  Exiting...");
                sys.exit();
        args.o = True;
        print();
    # check if database exists
    protocol.connect();
    protocol.createTables() # if necessary
    wheres = pd.DataFrame({'experiment_id': cargs});
    sets = protocol.selectSetsWhere(wheres);
    if len(sets)>0:
        print("("+ansi.br_magenta+"WARNING"+ansi.clear+") the following "+
            "experiments have database records:");
        print("\n".join([
            lpe(labbook, protocol, eid)
            for eid in sets['experiment_id'].unique()
        ]));
        print("if you continue the database and repository will be out of "+
            "sync...");
        try:
            if prompt("Continue",['y','n'],default='n')=='n':
                print("Okay, exiting...");
                sys.exit();
        except Exception as e:
            print("Sorry, I didn't understand that.  Exiting...");
            sys.exit();
        print();
    # initialize
    success = [];
    for eid in cargs:
        try:
            print(lpe(labbook,protocol,eid)+": ", end="", flush=True);
            protocol.initializeExperiment(eid, overwrite=args.o);
            success.append(eid);
            print(ansi.green+"OK"+ansi.clear);
        except Exception as e:
            print(ansi.red+"Error -> "+ansi.clear+str(e));
            # remove experiments that could be initialized?
            sys.exit();
    print("Success!");
#------------------------------------------------------------------------------#
def delete_path(labbook, protocol, cargs):
    validate_eids(cargs);
    #confirm ids
    print(  "About to delete repository paths for the following "+
            "experiment ids:");
    print("\n".join([lpe(labbook, protocol, eid) for eid in cargs]));
    try:
        if prompt("Proceed", ['y','n'], default='y')=='n':
            print("Okay, exiting...");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.  Exiting...");
        sys.exit();
    print();
    # confirm one more time
    printwarn(ansi.red+"This will remove ALL files and folders in these "+
            "repositories, including raw data files and subfolders...");
    try:
        if prompt("Are you really really sure", ['y','n'], default='n')=='n':
            print("Phew...  That would have been awful!");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.  Exiting...");
        sys.exit();
    errs = 0;
    for eid in cargs:
        print(lpe(labbook,protocol,eid)+": ", end="", flush=True);
        try: protocol.deleteExperimentPath(eid);
        except Exception as e:
            errs += 1;
            print(ansi.red+"ERROR"+ansi.clear);
            print(str(e));
            print();
            continue;
        print(ansi.green+"OK"+ansi.clear);
    if errs==0:
        print("Success!");
    else:
        print("I did what I could...");
#------------------------------------------------------------------------------#
def delete_files(labbook, protocol, cargs):
    validate_eids(cargs);
    #confirm ids
    print(  "About to delete repository set/sample files for the following "+
            "experiment ids:");
    print("\n".join([lpe(labbook, protocol, eid) for eid in cargs]));
    try:
        if prompt("Proceed", ['y','n'], default='y')=='n':
            print("Okay, exiting...");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.  Exiting...");
        sys.exit();
    print();
    errs = 0;
    for eid in cargs:
        print(lpe(labbook,protocol,eid)+": ", end="", flush=True);
        if os.path.isfile( protocol.samFile(eid) ):
            try: os.remove( protocol.samFile(eid) );
            except Exception as e:
                errs += 1;
                print(ansi.red+"ERROR DELETING SAMPLE FILE"+ansi.clear);
                print(str(e));
                print();
                continue;
        if os.path.isfile( protocol.setFile(eid) ):
            try: os.remove( protocol.setFile(eid) );
            except Exception as e:
                errs += 1;
                print(ansi.red+"ERROR DELETING SET FILE"+ansi.clear);
                print(str(e));
                print();
                continue;
        print(ansi.green+"OK"+ansi.clear);
    if errs==0:
        print("Success!");
    else:
        print("I did what I could...");
#------------------------------------------------------------------------------#
def drop(labbook, protocol, cargs):
    validate_eids(cargs);
    #confirm ids
    print(  "About to delete database set/sample records files for the "+
            "following experiment ids:");
    print("\n".join([lpe(labbook, protocol, eid) for eid in cargs]));
    try:
        if prompt("Proceed", ['y','n'], default='y')=='n':
            print("Okay, exiting...");
            sys.exit();
    except Exception as e:
        print("Sorry, I didn't understand that.  Exiting...");
        sys.exit();
    print();
    errs = 0;
    protocol.connect();
    for eid in cargs:
        wheres = pd.DataFrame({'experiment_id': [eid]});
        print(lpe(labbook,protocol,eid)+": ", end="", flush=True);
        try: protocol.deleteSetsAndSamplesWhere(wheres);
        except Exception as e:
            errs += 1;
            print(ansi.red+"ERROR"+ansi.clear);
            print(str(e));
            print();
            continue;
        print(ansi.green+"OK"+ansi.clear);
    protocol.disconnect();
    if errs==0:
        print("Success!");
    else:
        print("I did what I could...");
#------------------------------------------------------------------------------#





################################################################################
# Argument Processing
################################################################################
# dict of available commands mapped to their function refs
command_map = {
    'store'             : store,
    'restore'           : restore,
    'initialize'        : initialize,
    'delete_path'       : delete_path,
    'delete_files'      : delete_files,
    'drop'              : drop,
};
# validate command
if not args.command in command_map.keys():
    print("Unrecognized command '"+args.command+"'...");
    sys.exit();
# validate source format
if not '@' in args.source:
    print("Source should be formatted as labbook_id@protocol_id.");
    sys.exit();
source_parse = args.source.split('@');
if len(source_parse)!=2:
    print("Source should be formatted as labbook_id@protocol_id.");
    sys.exit();
labbook_id, protocol_id = source_parse[0:2];
if not plbCore.validID(labbook_id):
    print("labbook '"+labbook_id+"' has invalid characters.");
    sys.exit();
if not plbCore.validID(protocol_id):
    print("labbook '"+protocol_id+"' has invalid characters.");
    sys.exit();
# check for source labbook and protocol modules
protocol_module = protocol_id+'.py';
labbook_module = labbook_id+'.py';
if not os.path.isfile( os.path.join( plbLabbookRoot, labbook_module ) ):
    print("Can't find labbook module file "+labbook_module+".");
    sys.exit();
if not os.path.isfile( os.path.join( plbProtocolRoot, protocol_module ) ):
    print("Can't find protocol module file "+protocol_module+".");
    sys.exit();
# import and initialize source
try: labbook = plbCore.import_initialize_labbook( labbook_id, plbRoot );
except Exception as e:
    print("Error initializing "+labbook_id+": "+str(e));
    sys.exit();
try: protocol = plbCore.import_initialize_protocol( protocol_id, labbook );
except Exception as e:
    print("Error initializing "+protocol_id+": "+str(e));
    sys.exit();
# call command
command_map[args.command](labbook, protocol, args.arguments);

#
