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
    print("                                                                   ")
    sys.exit();
################################################################################
parser = argparse.ArgumentParser();
parser.add_argument(    'destination',
                        type=str,
);
parser.add_argument(    '-lp',
                        action='append',
                        nargs='+',
                        default=[],
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
def lp(labbook, protocol):
    return str(ansi.magenta+labbook.id+ansi.cyan+'@'+ansi.magenta+
                protocol.PROTOCOLID+ansi.clear);
################################################################################
# Argument Processing
################################################################################
# process destination labbook
if not plbCore.validID(args.destination):
    print("Labbook id '"+args.destination+"' contains invalid characters.");
    sys.exit();
d_lb_file = os.path.join(plbLabbookRoot, args.destination+".py");
if not os.path.isfile(d_lb_file):
    print("Can't find "+d_lb_file+".");
    sys.exit();
try: d_labbook = plbCore.import_initialize_labbook(args.destination, plbRoot);
except Exception as e:
    print("Can't import module "+file+".");
    sys.exit();
# protocol objects initialized to destination labbook, keyed by protocol_id
d_protocols = {};

# process items
items = [];
for item_list in args.lp:
    if '@' not in item_list[0]:
        print("Invalid labbook_id@protocol_id format.");
        sys.exit();
    labbook_id, protocol_id = item_list[0].split('@');
    if not plbCore.validID(labbook_id):
        print("Labbook id '"+labbook_id+"' contains invalid characters.");
        sys.exit();
    if not plbCore.validID(protocol_id):
        print("Labbook id '"+protocol_id+"' contains invalid characters.");
        sys.exit();
    for esid in item_list[1:]:
        if '.' in esid:
            eid, sid = esid.split('.');
        else:
            eid = esid;
            sid = None;
        if not plbCore.validID(eid):
            print("Experiment id '"+eid+"' contains invalid characters.");
            sys.exit();
        if sid!="" and not plbCore.validID(eid):
            print("Set id '"+sid+"' contains invalid characters.");
            sys.exit();
        items.append(pd.Series({
            'labbook_id'        : labbook_id,
            'protocol_id'       : protocol_id,
            'experiment_id'     : eid,
            'set_id'            : sid
        }));
items = pd.DataFrame(items).drop_duplicates();
items = items[items['labbook_id']!=d_labbook.id];

# verify labbooks and protocols
labbooks = {};
# verify and import protocol modules
for pid in items['protocol_id'].unique():
    file = os.path.join(plbProtocolRoot, pid+".py");
    if not os.path.isfile(file):
        print("Can't find protocol module "+file+".");
        sys.exit();
    try: plbCore.import_protocol(pid);
    except Exception as e:
        print(str(e));
        sys.exit();

# verify labbooks and initialize labbook@protocol combos
lp_objects = [];
for lid in items['labbook_id'].unique():
    file = os.path.join(plbLabbookRoot, lid+".py");
    if not os.path.isfile(file):
        print("Can't find "+file+".");
        sys.exit();
    try: labbooks[id] = plbCore.import_initialize_labbook(lid, plbRoot);
    except Exception as e:
        print("Can't import module "+file+".");
        sys.exit();
    # subset and do protocols
    ss_lb = items[items['labbook_id']==lid];
    for pid in ss_lb['protocol_id'].unique():
        # initialize and store into row
        try: protocol = plbCore.initialize_protocol(pid, labbooks[id]);
        except Exception as e:
            print(str(e));
            sys.exit();
        row = pd.Series({
            'labbook_id': lid,
            'protocol_id': pid,
            'lb': labbooks[id],
            'pr': protocol,
        });
        lp_objects.append(row);
        # also initialize to destination and store
        try: d_protocols[pid] = plbCore.initialize_protocol(pid, d_labbook);
        except Exception as e:
            print(str(e));
            sys.exit();

lp_objects = pd.DataFrame(lp_objects);

# load sets and samples
print("Loading data from source(s)...");
allsets = {};
allsams = {};
all_experiments = {};
for i,lp in lp_objects.iterrows():
    ss_items = items[
        (items['labbook_id']==lp['labbook_id']) &
        (items['protocol_id']==lp['protocol_id'])
    ];
    wheres = ss_items[['experiment_id','set_id']];
    lp['pr'].connect();
    # select data and add labbook/protocol ids
    try: sets = lp['pr'].selectSetsWhere(wheres);
    except Exception as e:
        print("Error loading sets from "+lp(lp['lb'], lp['pr'])+": "+str(e));
        sys.exit();

    try: sams = lp['pr'].selectSamsWhere(wheres);
    except Exception as e:
        print(  "Error loading sampless from "+lp(lp['lb'], lp['pr'])+
                ": "+str(e));
        sys.exit();
    # accumulate
    if lp['protocol_id'] not in all_experiments.keys():
        all_experiments[lp['protocol_id']] = \
            list(sets['experiment_id'].unique());
    else:
        all_experiments[lp['protocol_id']] += \
            list(sets['experiment_id'].unique());

    if lp['protocol_id'] not in allsets.keys():
        allsets[lp['protocol_id']] = [sets];
    else:
        allsets[lp['protocol_id']].append(sets);

    if lp['protocol_id'] not in allsams.keys():
        allsams[lp['protocol_id']] = [sams];
    else:
        allsams[lp['protocol_id']].append(sams);
    lp['pr'].disconnect();

    for eid in sets['experiment_id'].unique():
        set_ss = sets[sets['experiment_id']==eid];
        sam_ss = sams[sams['experiment_id']==eid];
        print(  lpe(lp['lb'], lp['pr'], eid)+" ("+
                ansi.br_cyan+str(len(set_ss))+ansi.clear+"/"+
                ansi.cyan+str(len(sam_ss))+ansi.clear+")"
        );
print();

# check destination for existing protocol.experiments
existing_experiments = [];
for protocol_id in all_experiments.keys():
    wheres = pd.DataFrame({'experiment_id': all_experiments[protocol_id]});
    d_protocols[protocol_id].connect();
    d_protocols[protocol_id].createTables(); #if necessary
    exist_sets = d_protocols[protocol_id].selectSetsWhere(wheres);
    d_protocols[protocol_id].disconnect();
    if len(exist_sets)>0:
        for ex_eid in exist_sets['experiment_id'].unique():
            existing_experiments.append(pd.Series({
                'protocol_id': protocol_id,
                'experiment_id': ex_eid,
                'sets': len(exist_sets[exist_sets['experiment_id']==ex_eid]),
            }));
existing_experiments = pd.DataFrame(existing_experiments);

# ask user what to do with existing records
if len(existing_experiments)>0:
    printwarn(  "The following experiments already have records:");
    for i,r in existing_experiments.iterrows():
        print(  ansi.magenta+d_labbook.id+ansi.cyan+'@'+ansi.magenta+
                r['protocol_id']+' '+ansi.green+r['experiment_id']+
                ' '+ansi.clear+'('+ansi.br_cyan+str(r['sets'])+ansi.clear+')'
        );
    print(  "to maintain the integrity of your experiments, ALL of these "+
            "records must be deleted before I can continue...");
    try:
        if prompt("continue", ['y','n'], default='n')=='n':
            print("Okay, exiting...");
            sys.exit();
    except Exception as e:
        print("Sorry, I don't understand that...  Exiting.");
        sys.exit();
    print();

print("Transferring...");
# transfer
for protocol_id in allsets.keys():
    d_protocols[protocol_id].connect();
    print(  ansi.magenta+d_labbook.id+ansi.cyan+'@'+ansi.magenta+protocol_id+
            ansi.clear+" ", end='', flush=True);
    store_sets = pd.concat(allsets[protocol_id]);
    store_sams = pd.concat(allsams[protocol_id]);
    print(  "("+ansi.br_cyan+str(len(store_sets))+ansi.clear+"/"+
            ansi.cyan+str(len(store_sams))+ansi.clear+"): ",
            end='', flush=True);
    try:
        d_protocols[protocol_id].storeSetsAndSamples(
            store_sets,
            store_sams,
            method='killreplace',
        );
    except Exception as e:
        print(ansi.red+"ERROR"+ansi.clear);
        print(str(e));
        continue;
    d_protocols[protocol_id].disconnect();
    print(ansi.green+"OK"+ansi.clear);
print("Done.");
