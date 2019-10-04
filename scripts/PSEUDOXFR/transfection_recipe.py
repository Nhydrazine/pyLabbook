import sys, os;
import numpy as np, pandas as pd;
################################################################################
# find pyLabbook root for importing
plbRoot=os.path.abspath(
    os.path.join(
        os.path.dirname( sys.argv[0] ),
        '..',
        '..',
    )
);
myroot = os.path.dirname( sys.argv[0] );
sys.path.append( os.path.join(plbRoot,'python') );
# import labbook and protocol
import pyLabbook.labbooks.LabData;
import pyLabbook.protocols.PSEUDOXFR;
################################################################################
################################################################################
# instantiate and initialize labbook and protocol
lb = pyLabbook.labbooks.LabData.initialize( plbRoot );
pr = pyLabbook.protocols.PSEUDOXFR.initialize( lb );

# specify experiments to calculate recipes for
eids = pd.DataFrame({
    'experiment_id' : ['20180625','20180709'],
});

# connect to database and get sets
pr.connect();
sets = pr.selectSetsWhere(eids);
# calculate and format recipes using custom pyProtocol extension functions
sams, recipes = pr.formatBioT_TransfectionRecipes(sets);
# store sample data
pr.storeSams(sams, method='killreplace');
# disconnect
pr.disconnect();

# write to local file for printing
output_file = os.path.join(myroot, "transfection_recipe_output.csv");
print("Writing to "+output_file);
recipes.to_csv( output_file, index=False );
print("done");
#
