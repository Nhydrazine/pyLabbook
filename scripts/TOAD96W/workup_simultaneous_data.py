################################################################################
import sys, os, re;
import numpy as np, pandas as pd;
import matplotlib.pyplot as plt;
import matplotlib as mpl;
from nicMods.graphing import plotPage;
import fitModels;
################################################################################
# set paths using my path relative
myroot = os.path.dirname( sys.argv[0] );
plbRoot = os.path.abspath( os.path.join( myroot,'..','..' ) );
plbPythonRoot = os.path.join( plbRoot,'python' );
sys.path.append( plbPythonRoot );
################################################################################
import pyLabbook.core as plbCore;
################################################################################
output_file = os.path.join( myroot, "simuldata_workup.xlsx" );
################################################################################
# instantiate labbook and protocol
lb = plbCore.import_initialize_labbook('AldrovandiLab', plbRoot);
pr = plbCore.import_initialize_protocol('TOAD96W', lb);
################################################################################
# load data
datafile = os.path.join(myroot,"simuldata.xlsx");
xl = pd.ExcelFile(datafile);
paired = xl.parse('paired', index=None);
sets = xl.parse('sets', index=None);
sams = xl.parse('sams', index=None);
xl.close();
################################################################################
# subset for workup
# paired = paired[paired['env']=='B24731_XPD_704'];
# use_esids = [];
# for elist in paired['esid_list']: use_esids += elist.split(',');
# sets = sets[sets['esid'].isin(use_esids)];
# sams = sams[sams['esid'].isin(use_esids)];
################################################################################
# workup
print("working up");
sets, sams = pr.workup(sets, sams, varianceFormula=True);

################################################################################
print("writing "+output_file);
xw = pd.ExcelWriter(output_file);
paired.to_excel(xw,'paired',index=False);
sets.to_excel(xw,'sets',index=False);
sams.to_excel(xw,'sams',index=False);
xw.save();
xw.close();
sys.exit();
