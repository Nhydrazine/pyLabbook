################################################################################
import sys, os, argparse, re;
import numpy as np, pandas as pd;
################################################################################
# path of this script
myroot = os.path.dirname( sys.argv[0] );
# get absolute pyLabbook root using relative path
plbRoot=os.path.abspath(os.path.join(myroot,'..','..'));
# get path to pyLabbook python folder
plbPythonRoot = os.path.join(plbRoot,'python');
# append to import paths
sys.path.append(plbPythonRoot);
# import core pyLabbook module (see below)
import pyLabbook.core as core;
# import the protocol
import pyLabbook.protocols.TOAD96W;
################################################################################
# parse commandline arguments
parser = argparse.ArgumentParser();
parser.add_argument(    'labbook_id',
                        help="id of the labbook to use",
                        type=str,
);
parser.add_argument(    '--eids',
                        help=("space separated list of experiment ids to "+
                            "calculate recipes for"),
                        default=[],
                        nargs="+",
);
parser.add_argument(    '--out',
                        help=("optional name for output file base name, "+
                            "default is transfection_recipe_output"),
                        default="transfection_recipe_output",
);
parser.add_argument(    '--format',
                        help=("optional format for recipe file, 'xlsx' or "+
                            "'csv'.  Default is 'csv'"),
                        default='csv',
);
args = parser.parse_args();
################################################################################
# validate arguments
# labbook id
rx = re.compile("^[A-Z,a-z,0-9,\_,\-]+$");
if not rx.match(args.labbook_id):
    print(args.labbook_id+" contains invalid characters.");
    sys.exit();
# format
if not args.format in ['csv','xlsx']:
    print("invalid format option.");
    sys.exit();
# experiment ids
if len(args.eids)<1:
    print("no experiment id's specified.");
    sys.exit();
################################################################################
# instantiate and initialize labbook using pyLabbook.core importer
# first, build a string that reflects the import path: pyLabbook.labbooks.[id]
labbook_modpath = '.'.join(['pyLabbook','labbooks',args.labbook_id]);
print("Importing and initializing "+labbook_modpath+"...");
# try to import if not already imported
try: core.import_module_path(labbook_modpath);
except Exception as e:
    print("Can't import "+args.labbook_id+": "+str(e));
    sys.exit();
# instantiate/initialize
try:
    lb = core.call_module(labbook_modpath).initialize( plbRoot );
except Exception as e:
    print("Can't initialize "+args.labbook_id+": "+str(e));
    sys.exit();
# the labbook instance is now stored in lb

print("Initializing protocol...");
# initialize the protocol
pr = pyLabbook.protocols.TOAD96W.initialize( lb );

pr.connect();
wheres = pd.DataFrame({'experiment_id': args.eids});
sets = pr.selectSetsWhere(wheres);
sams = pr.selectSamsWhere(wheres);
pr.disconnect();

pr.workup_merge(sets, sams);


print("ok");
