import os, sys;
import numpy as np, pandas as pd;
from pyLabbook import pyLabbook, pyProtocol;
import pyLabbook.core as core;
rootpath = os.path.abspath(os.path.join(
        os.path.dirname(sys.argv[0]),
        '..'
));
labbookroot = os.path.join( rootpath, 'python', 'pyLabbook', 'labbooks' );
protocolroot = os.path.join( rootpath, 'python', 'pyLabbook', 'protocols' );
################################################################################
# create a labbook #############################################################
################################################################################
def createLabbook(
    destinationpath = None,
    destinationfile = None,
    overwrite       = False,
    labbook_object  = None,
    # id              = None,
    # root            = None,
    # repositoryPath  = None,
    # sheetFormat     = None,
    # databasePath    = None,
    # databaseFile    = None,
    # databaseFormat  = None
):
    if labbook_object==None: raise Exception("invalid labbook object");
    # try:
    #     plb = pyLabbook(
    #         id              = id,
    #         root            = root,
    #         repositoryPath  = repositoryPath,
    #         sheetFormat     = sheetFormat,
    #         databasePath    = databasePath,
    #         databaseFile    = databaseFile,
    #         databaseFormat  = databaseFormat
    #     );
    # except: raise;
    if not os.path.isdir(destinationpath): core.makepath(destinationpath);
    if os.path.isfile( os.path.join( destinationpath, destinationfile ) ):
        if not overwrite:
            raise Exception("file " + os.path.join( destinationpath, destinationfile ) + " already exists.");
    print("Writing to " + os.path.join( destinationpath, destinationfile ));
    with open(os.path.join( destinationpath, destinationfile ),'w') as fh:
        fh.write( labbook_object.exportSerialized() );
    # now make structure
    labbook_object.createFileStructure();
    return True;
# # RUN ##########################################################################
# bookid = "bookID";
# labbookroot = os.path.join( rootpath, 'python', 'pyLabbook', 'labbooks' );
# createLabbook(
#     destinationpath = labbookroot,
#     destinationfile = str(bookid) + ".py",
#     overwrite       = True,
#     id              = "bookID",
#     root            = rootpath,
#     repositoryPath  = "repositories/bookID",
#     sheetFormat     = "xlsx",
#     databasePath    = "databases",
#     databaseFile    = "bookID.sqlite3",
#     databaseFormat  = "SQLITE3",
# );
# # TEST #########################################################################
# import pyLabbook.labbooks.bookID;
# lb = pyLabbook.labbooks.bookID.initialize(rootpath);
# lb.createFileStructure();
################################################################################
# create a protocol ############################################################
################################################################################
def createProtocol(
    destinationpath = None,
    destinationfile = None,
    overwrite       = False,
    pyprotocol_object = None,
    # id              = None,
    # setdesc         = pd.DataFrame(),
    # samdesc         = pd.DataFrame(),
):
    if pyprotocol_object==None: raise Exception("invalid protocol object");
    # plb = pyLabbook.pyLabbook(
    #     id              = "temp",
    #     root            = rootpath,
    #     repositoryPath  = "repositories",
    #     sheetFormat     = "xlsx",
    #     databasePath    = "databases",
    #     databaseFile    = "temp.sqlite3",
    #     databaseFormat  = "SQLITE3",
    # );
    # proto = pyLabbook.pyProtocol(plb);
    # proto.PROTOCOLID = id;
    # for i,r in setdesc.iterrows():
    #     proto.addSetColumn(
    #         name        = r['name'],
    #         type        = r['type'],
    #         notnull     = r['notnull'],
    #         unique      = r['unique'],
    #         description = r['description'],
    #         default     = r['default'],
    #         primary_key = r['primary_key'],
    #     );
    # for i,r in samdesc.iterrows():
    #     proto.addSamColumn(
    #         name        = r['name'],
    #         type        = r['type'],
    #         notnull     = r['notnull'],
    #         unique      = r['unique'],
    #         description = r['description'],
    #         default     = r['default'],
    #         primary_key = r['primary_key'],
    #     );

    if not os.path.isdir(destinationpath): core.makepath(destinationpath);
    if os.path.isfile( os.path.join( destinationpath, destinationfile ) ):
        if not overwrite:
            raise Exception("file " + os.path.join( destinationpath, destinationfile ) + " already exists.");
    print("Writing to " + os.path.join( destinationpath, destinationfile ));
    with open(os.path.join( destinationpath, destinationfile ),'w') as fh:
        fh.write( pyprotocol_object.exportSerialized() );
    return;
# RUN ##########################################################################
# pid = "TestProtocol";
# setdesc = pd.DataFrame([
#     ['inhibitor_name','TEXT',True,False,"",None,False],
#     ['inhibitor_id','TEXT',True,False,"",None,False],
# ], columns=[
#     'name',
#     'type',
#     'notnull',
#     'unique',
#     'description',
#     'default',
#     'primary_key'
# ]);
# createProtocol(
#     destinationpath = protocolroot,
#     destinationfile = str(pid) + ".py",
#     overwrite       = True,
#     id              = str(pid),
#     setdesc         = setdesc,
# );
# # TEST #########################################################################
# import pyLabbook.protocols.TestProtocol;
# p = pyLabbook.protocols.TestProtocol.initialize(lb);
# p.createFileStructure();
# p.initializeExperiment('20190101', overwrite=True);
# p.initializeExperiment('20190102', overwrite=True);
# p.initializeExperiment('20190103', overwrite=True);
################################################################################

################################################################################
# GET LIST OF LABBOOKS AND PROTOCOLS ###########################################
################################################################################
def listPyFiles(root):
    pyfiles = [];
    for f in os.listdir(root):
        name, ext = os.path.splitext(f);
        if ext=='.py' and name[0]!='_' and name[0]!='.': pyfiles.append(name);
    return pyfiles;
def listLabbooks(labbookroot): return listPyFiles(labbookroot);
def listProtocols(protocolroot): return listPyFiles(protocolroot);

# print(listLabbooks());
# print(listProtocols());
################################################################################
# GET LIST OF EXPERIMENTS FOR PROTOCOL/LABBOOK #################################
################################################################################
#import pyLabbook.labbooks.Inhibitor20190101;
#import pyLabbook.protocols.InhibitorProduction;
# ilb = pyLabbook.labbooks.Inhibitor20190101.initialize(rootpath);
# ip = pyLabbook.protocols.InhibitorProduction.initialize(ilb);
# ip.connect();
# print(ip.selectAllExperimentIDs());
# print(ip.listExperimentFolders());
# ip.disconnect();










#
