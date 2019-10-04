"""Example script that calculates two-plasmid virus pseudotype transfection
recipes using the PSEUDOXFR protocol.  Recipes are output to a spreadsheet
file that can be printed and referenced during the transfection protocol."""
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
import pyLabbook.protocols.PSEUDOXFR;
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
                        help=("optional name for output file basedname, "+
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
pr = pyLabbook.protocols.PSEUDOXFR.initialize( lb );

print("Calcualting recipes...");
# specify experiments to calculate recipes for
eids = pd.DataFrame({'experiment_id' : args.eids});

# connect to database and get sets
pr.connect();
sets = pr.selectSetsWhere(eids);
# calculate and format recipes using custom pyProtocol extension functions
sams, recipes = pr.formatBioT_TransfectionRecipes(sets);
# store sample data
pr.storeSams(sams, method='killreplace');
# disconnect
pr.disconnect();

# build output file name
output_file = args.out;
if args.format=='csv': output_file += '.csv';
elif args.format=='xlsx': output_file += '.xlsx';
else: raise Exception("invalid format");

# write
print("Writing to "+output_file+"...");
if args.format=='csv':
    recipes.to_csv(output_file, index=False);
elif args.format=='xlsx':
    xw = pd.ExcelWriter(output_file);
    recipes.to_excel(xw, 'Sheet1', index=False);
    xw.save();
    xw.close();
################################################################################
