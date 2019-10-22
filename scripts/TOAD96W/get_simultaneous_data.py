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
output_file = os.path.join(myroot,"simuldata.xlsx");
################################################################################
# instantiate labbook and protocol
lb = plbCore.import_initialize_labbook('AldrovandiLab', plbRoot);
pr = plbCore.import_initialize_protocol('TOAD96W', lb);
################################################################################
# custom view for grabbing simultaneous MVC/T20 esperiment ids as comma
# separated list in esid column.
SQL = """
select
    *
from (
    select
        experiment_id,
        set_id,
        group_concat(experiment_id || '.' || set_id,',') as esid_list,
        env,
        pseudo_id,
        inhibitor_id,
        group_concat(inhibitor_id,',') as inhibitor_list,
        count(env) as records
    from TOAD96W_SETS
    group by experiment_id || '!' || pseudo_id || '!' || substr(set_id,2,1)
)
where records=2
and (inhibitor_list='MVC,T20' or inhibitor_list='T20,MVC')
""";
################################################################################
print("Selecting...");
pr.connect();
# get esids for simultaneous MVC/T20 experiments
paired = pr.selectSQL(SQL);
paired['pairid'] =  paired['experiment_id'] + '!' + \
                    paired['pseudo_id'] + '!' + \
                    paired['set_id'].str[0:2];
paired['esids_aslist'] = paired['esid_list'].str.split(',');
# get flat list of all esids
flat_esids = pd.DataFrame({
    'esid': np.array( paired['esids_aslist'].tolist() ).flatten()
});
# split into paired experiment id and set id
flat_esids['experiment_id'], flat_esids['set_id'] = \
    flat_esids['esid'].str.split('.').str;
# build wheres
wheres = flat_esids[['experiment_id','set_id']];
# select sets and samples
sets = pr.selectSetsWhere(wheres);
sets['esid'] = sets['experiment_id'] + '.' + sets['set_id'];
sets['pairid'] =    sets['experiment_id'] + '!' + \
                    sets['pseudo_id'] + '!' + \
                    sets['set_id'].str[0:2];
sams = pr.selectSamsWhere(wheres);
sams['esid'] = sams['experiment_id'] + '.' + sams['set_id'];
pr.disconnect();
xw = pd.ExcelWriter(output_file);
paired.to_excel(xw,'paired',index=False);
sets.to_excel(xw,'sets',index=False);
sams.to_excel(xw,'sams',index=False);
xw.save();
xw.close();
print("Done.");
