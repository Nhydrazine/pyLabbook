"""
pyLabbook script for processing and fitting time of addition entry kinetics data
associated with the protocol described by Webb et al.
Author: Nicholas E. Webb

This script is intended to work within the pyLabbook data management system, which is free and open source.  To use:
    1.  Make a folder called TOAD96W in the scripts folder of your pyLabbook
        distribution

    2.  Copy this script to that location

    3.  Be sure you have the TOAD96W.py protocol module in the protocol modules
        folder of your pyLabbook distribution
        (python/pyLabbook/protocols)

    4.  Run this script from the command line by specifying a labbook id that
        contains TOAD96W protocol data and specify any number of space
        separated experiment ids using the --eids option

    This will output either as sqlite database (by default) or excel
    spreadsheet (if you use --format xlsx) containing the following:

        TOAD96W_SAMPLES
            original samples data if -x is not used
        TOAD96W_SETS
            original set data if -x is not used
        TOAD96W_SAMPLES_PROCESSED
            processed/worked up sample data
        TOAD96W_SETS_PROCESED
            processed/worked up set data
        TOAD96W_SAMPLES_DELTA
            change in infection values for samples
        TOAD96W_FITS
            lognormal fits and additional metrics for each set

"""
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
import sys, os, sqlite3, argparse, re;
import numpy as np, pandas as pd;
################################################################################
# SETUP PATH INFORMATION FOR IMPORTS ###########################################
################################################################################
# path of this script
myroot = os.path.dirname( sys.argv[0] );
# get absolute pyLabbook root using relative path
# >>>> CHANGE THIS IF YOUR PYLABBOOK ROOT IS ELSEWHERE <<<<<<<<<<<<<<<<<<<<<<<<<
plbRoot=os.path.abspath(os.path.join(myroot,'..','..')); #<<<<<<<<<<<<<<<<<<<<<<
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# get path to pyLabbook python folder relative to plbRoot
plbPythonRoot = os.path.join(plbRoot,'python');
# append to import paths
sys.path.append(plbPythonRoot);
# import core pyLabbook module so we can use pyLabbook importers
import pyLabbook.core as core;
################################################################################
# commandline arguments
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
                        default="TOAD96W_workup",
);
parser.add_argument(    '--format',
                        help=("optional format for results file, 'sqlite' or "+
                            "'xlsx'.  Default is 'sqlite'"),
                        default='sqlite',
);
parser.add_argument(    '-x',
                        help=("excludes original SET and SAMPLE data from "+
                            "output file, just outputs the workups."),
                        action="store_true",
                        default=False,
);
parser.add_argument(    '-novarianceformula',
                        help=("do not use variance formula to propagate error "+
                            "among replicates.  Instead, calculate curves for "+
                            "each replicate separately then average them.  "+
                            "This results in slightly smaller error bars."),
                        action="store_true",
                        default=False,
);
parser.add_argument(    '-silent',
                        help=("do not print progress to screen."),
                        action="store_true",
                        default=False,
);
args = parser.parse_args();
################################################################################
# ARGUMENT VALIDATION ##########################################################
################################################################################
# validate format argument
if not args.format in ['sqlite','xlsx']:
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
usevariance = True;
if args.novarianceformula: usevariance = False;
verbose = True;
if args.silent: verbose = False;
################################################################################
# IMPORT AND INSTANTIATE LABBOOK/PROTOCOL FROM PYLABBOOK #######################
################################################################################
if verbose: print("Connecting...");
# instantiate and initialize labbook using pyLabbook.core importer
lb = core.import_initialize_labbook(args.labbook_id, plbRoot);
# instantiate and initialize protocol using pyLabbook.core importer
pr = core.import_initialize_protocol('TOAD96W', lb);
################################################################################
# GET REQUESTED DATA ###########################################################
################################################################################
if verbose: print("Loading data...");
pr.connect();

# normal selection
# if '_ALL_' in args.eids:
#     args.eids = pr.selectAllExperimentIDs()['experiment_id'].values;
# wheres = pd.DataFrame({'experiment_id': args.eids});
# sets = pr.selectSetsWhere(wheres);
# sams = pr.selectSamsWhere(wheres);

# custom selection for export of kinetic manuscript data
# get all experiment ids for appropriate sets
wheres = "WHERE cell_type='TZM-BL' and temperature=37";
sets = pr.selectSetsWith(wheres);
wheres = sets[['experiment_id','set_id']];
sams = pr.selectSamsWhere(wheres);

pr.disconnect();
################################################################################
# USE PROTOCOL MODULE METHODS TO PROCESS AND FIT DATA ##########################
################################################################################
if verbose: print("Processing...");
# these are the only lines here that have anyting to do with the actual data...
# process samples (subtract, normalize etc...)
processed_sets, processed_sams = pr.workup(
                                    sets,
                                    sams,
                                    varianceFormula=usevariance,
                                    verbose=verbose
                                );
# calculate change in infection values
delta = pr.workup_delta(processed_sams, verbose=verbose);
if verbose: print("Fitting...");
# run lognormal fitting
fits = pr.ln_fit(processed_sets, processed_sams, verbose=verbose);
# get metrics from lognormal parameter fits (DURATION, DELAY etc...)
fits = pr.ln_metrics(fits);
################################################################################
# OUTPUT RESULTS ###############################################################
################################################################################
tables = {
    'delta'             : 'TOAD96W_SAMPLES_DELTA',
    'sets'              : 'TOAD96W_SETS',
    'samples'           : 'TOAD96W_SAMPLES',
    'processed_samples' : 'TOAD96W_SAMPLES_PROCESSED',
    'processed_sets'    : 'TOAD96W_SETS_PROCESSED',
    'fits'              : 'TOAD06W_FITS',
};
# output
outfile = os.path.join(myroot, args.out+"."+args.format);
# remove file if exists
if os.path.isfile(outfile):
    os.remove(outfile);
if verbose: print("Writing to "+outfile+"...");
# output
if args.format=="sqlite":
    dbc = sqlite3.connect(outfile);
    if args.x==False:
        sets.to_sql(
            tables['sets'],
            dbc,
            if_exists='replace',
            index=False );
        sams.to_sql(
            tables['samples'],
            dbc,
            if_exists='replace',
            index=False
        );
    processed_sets.to_sql(
        tables['processed_sets'],
        dbc,
        if_exists='replace',
        index=False );
    processed_sams.to_sql(
        tables['processed_samples'],
        dbc,
        if_exists='replace',
        index=False
    );
    delta.to_sql(
        tables['delta'],
        dbc,
        if_exists='replace',
        index=False
    );
    fits.to_sql(
        tables['fits'],
        dbc,
        if_exists='replace',
        index=False
    );
    dbc.commit();
    dbc.close();
elif args.format=='xlsx':
    xw = pd.ExcelWriter(outfile);
    if args.x==False:
        sets.to_excel(
            xw,
            tables['sets'],
            index=False
        );
        sams.to_excel(
            xw,
            tables['samples'],
            index=False
        );
    processed_sets.to_excel(
        xw,
        tables['processed_sets'],
        index=False
    );
    processed_sams.to_excel(
        xw,
        tables['processed_samples'],
        index=False
    );
    delta.to_excel(
        xw,
        tables['delta'],
        index=False
    );
    fits.to_excel(
        xw,
        tables['fits'],
        index=False
    );
    xw.save();
    xw.close();
else:
    if verbose:
        print("No method for format "+str(args.format)+", no data written...");
        sys.exit();
    else:
        raise Exception("No method for format "+str(args.format)+", no data written...");
if verbose: print("Done!");
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
