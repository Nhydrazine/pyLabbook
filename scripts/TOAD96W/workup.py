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
# validate format argument
if not args.format in ['csv','xlsx']:
    print("invalid format option.");
    sys.exit();
# validate experiment ids length
if len(args.eids)<1:
    print("no experiment id's specified.");
    sys.exit();
# validate experiment ids characters
for eid in args.eids:
    if not core.validID(eid):
        print("Invalid experiment id: "+str(eid));
        sys.exit();
################################################################################
# instantiate and initialize labbook using pyLabbook.core importer
lb = core.import_initialize_labbook(args.labbook_id, plbRoot);
# instantiate and initialize protocol using pyLabbook.core importer
pr = core.import_initialize_protocol('TOAD96W', lb);

# get sets and samples for requested experiment ids
pr.connect();
wheres = pd.DataFrame({'experiment_id': args.eids});
sets = pr.selectSetsWhere(wheres);
sams = pr.selectSamsWhere(wheres);
pr.disconnect();

# run workup method
pr.workup_merge(sets, sams);

print("ok");
