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
parser.add_argument(    '-lp',
                        action='append',
                        nargs='+',
                        default=[],
);
parser.add_argument(    '--base',
                        default="export",
                        type=str,
                        help=("Export file(s) base name"),
);
parser.add_argument(    '--format',
                        default="xlsx",
                        type=str,
);
parser.add_argument(    '-s',
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
lp_objects = pd.DataFrame(lp_objects);

# load sets and samples
allsets = {};
allsams = {};
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
    orig_setcols = sets.columns.tolist();
    sets['labbook_id'] = lp['labbook_id'];
    sets['protocol_id'] = lp['protocol_id'];
    sets = sets[['labbook_id','protocol_id']+orig_setcols];

    try: sams = lp['pr'].selectSamsWhere(wheres);
    except Exception as e:
        print(  "Error loading sampless from "+lp(lp['lb'], lp['pr'])+
                ": "+str(e));
        sys.exit();
    orig_samcols = sams.columns.tolist();
    sams['labbook_id'] = lp['labbook_id'];
    sams['protocol_id'] = lp['protocol_id'];
    sams = sams[['labbook_id','protocol_id']+orig_samcols];

    # accumulate
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
        print(  lpe(lp['lb'], lp['pr'], eid)+" ("+
                ansi.br_cyan+str(len(sets))+ansi.clear+"/"+
                ansi.cyan+str(len(sams))+ansi.clear+")"
        );
print();

# export
if args.format=='xlsx':
    # single file xlsx output
    if args.s:
        outfile = args.base+".xlsx";
        xw = pd.ExcelWriter(outfile);
        print("Writing to "+outfile+": ");
        for protocol_id in allsets.keys():
            print(  "\t"+ansi.cyan+"@"+ansi.magenta+
                    protocol_id+ansi.clear+": ", end="", flush=True);
            protocol_sets = pd.concat(allsets[protocol_id]);
            protocol_sams = pd.concat(allsams[protocol_id]);
            protocol_sets.to_excel(
                xw,
                protocol_id+"_SETS",
                index=False,
            );
            protocol_sams.to_excel(
                xw,
                protocol_id+"_SAMS",
                index=False,
            );
            print(ansi.green+"OK"+ansi.clear);
        xw.save();
        xw.close();
        print("Done.");
        sys.exit();
    else:
        for protocol_id in allsets.keys():
            outfile = args.base+"_"+protocol_id+".xlsx";
            xw = pd.ExcelWriter(outfile);
            print(  "Writing "+ansi.cyan+"@"+ansi.magenta+protocol_id+
                    ansi.clear+" to "+outfile+": ", end="", flush=True);
            protocol_sets = pd.concat(allsets[protocol_id]);
            protocol_sams = pd.concat(allsams[protocol_id]);
            protocol_sets.to_excel(
                xw,
                protocol_id+"_SETS",
                index=False,
                header=True,
            );
            protocol_sams.to_excel(
                xw,
                protocol_id+"_SAMS",
                index=False,
                header=True,
            );
            xw.save();
            xw.close();
            print(ansi.green+"OK"+ansi.clear);
        print("Done.");
        sys.exit();
elif args.format=='csv':
        for protocol_id in allsets.keys():
            outfile_sets = args.base+"_"+protocol_id+"_SETS"+".csv";
            outfile_sams = args.base+"_"+protocol_id+"_SAMPLES"+".csv";
            print(  "Writing "+ansi.cyan+"@"+ansi.magenta+protocol_id+
                    ansi.green+" SETS "+ansi.clear, end="", flush=True);
            protocol_sets = pd.concat(allsets[protocol_id]);
            print("("+ansi.cyan+str(len(protocol_sets))+ansi.clear+") to "+
                outfile_sets+": ", end="", flush=True);
            protocol_sets.to_csv(outfile_sets, index=False, header=True);
            print(ansi.green+"OK"+ansi.clear);

            print(  "Writing "+ansi.cyan+"@"+ansi.magenta+protocol_id+
                    ansi.green+" SAMLES "+ansi.clear, end="", flush=True);
            protocol_sams = pd.concat(allsams[protocol_id]);
            print("("+ansi.cyan+str(len(protocol_sams))+ansi.clear+") to "+
                outfile_sams+": ", end="", flush=True);
            protocol_sams.to_csv(outfile_sams, index=False, header=True);
            print(ansi.green+"OK"+ansi.clear);
        print("Done.");
        sys.exit();
else:
    print("Unrecognized file format.");
    sys.exit();
