# python #######################################################################
try:
    import sys;
    print("sys ".ljust(40,'.')+" OK");
    print("python ".ljust(40,".")+" "+
        '.'.join([str(v) for v in sys.version_info[0:3]])
    );
    if sys.version_info[0]<3 and sys.version_info[1]<6 and sys.version[2]<5:
        print("python 3.6.5+ is required.");
        sys.exit();
except Exception as e:
    print("Can't import sys: "+str(e));
    sys.exit();
# everyone #####################################################################
versionerrors = [];
print();
print("Checking for Required Modules");
try:
    import os;
    print("os ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import os: "+str(e));

try:
    import re;
    print("re ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import re: "+str(e));

try:
    import shutil;
    print("shutil ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import shutil: "+str(e));

try:
    import numpy as np;
    print("numpy ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import numpy: "+str(e));

try:
    import pandas as pd;
    print("pandas ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import pandas: "+str(e));
vsp = pd.__version__.split('.');
if int(vsp[0])==0 and int(vsp[1])<24:
    versionerrors.append(
        "update pandas to version 0.24.0 or higher");

try:
    import sqlite3;
    print("sqlite3 ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import sqlite3: "+str(e));

try:
    import xlrd;
    print("xlrd ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import xlrd: "+str(e));

try:
    import openpyxl;
    print("openpyxl ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import openpyxl: "+str(e));

# manager ######################################################################
print();
print("Checking for Manager Modules");
try:
    import tkinter as tk;
    print("tkinter ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import tkinter: "+str(e));

try:
    from tkinter import messagebox;
    print("tkinter.messagebox ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import tkinter.messagebox: "+str(e));

try:
    from tkinter import scrolledtext;
    print("tkinter.scrolledtext ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import tkinter.scrolledtext: "+str(e));

try:
    from tkinter import filedialog;
    print("tkinter.filedialog ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import tkinter.filedialog: "+str(e));

try:
    from tkinter import ttk;
    print("tkinter.ttk ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import tkinter.ttk: "+str(e));

# manager widgets ##############################################################
print();
print("Checking for Manager Widgets");
try:
    import guiWidgets;
    print("guiWidgets ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import guiWidgets: "+str(e));

w = {};
tkerrs = [];
skip=False;
try: w['tk'] = tk.Tk();
except Exception as e:
    tkerrs.append("can't instantiate Tk: "+str(e));
    skip=True;
if not skip:
    try:
        w['frame'] = ttk.Frame(w['tk']);
        print("ttk.Frame ".ljust(40,'.')+" OK");
    except Exception as e: print("ttk.Frame ".ljust(40,'.')+" "+str(e));
    try:
        w['label'] = ttk.Label(w['tk']);
        print("ttk.Label ".ljust(40,'.')+" OK");
    except Exception as e: print("ttk.Label ".ljust(40,'.')+" "+str(e));
    try:
        w['entry'] = ttk.Entry(w['tk']);
        print("ttk.Entry ".ljust(40,'.')+" OK");
    except Exception as e: print("ttk.Entry ".ljust(40,'.')+" "+str(e));
    try:
        w['button'] = ttk.Button(w['tk']);
        print("ttk.Button ".ljust(40,'.')+" OK");
    except Exception as e: print("ttk.Button ".ljust(40,'.')+" "+str(e));
    try:
        w['checkbutton'] = ttk.Checkbutton(w['tk']);
        print("ttk.Checkbutton ".ljust(40,'.')+" OK");
    except Exception as e: print("ttk.Checkbutton ".ljust(40,'.')+" "+str(e));
    try:
        w['combobox'] = ttk.Combobox(w['tk']);
        print("ttk.Combobox ".ljust(40,'.')+" OK");
    except Exception as e: print("ttk.Combobox ".ljust(40,'.')+" "+str(e));
    try:
        w['treeview'] = ttk.Treeview(w['tk']);
        print("ttk.Treeview ".ljust(40,'.')+" OK");
    except Exception as e: print("ttk.Treeview ".ljust(40,'.')+" "+str(e));
# pyLabbook structure ##########################################################

plbRoot = os.path.abspath( os.path.dirname( sys.argv[0] ) );
print();
print("Checking pyLabbook distribution at "+plbRoot);
plbPythonRoot = os.path.join( plbRoot, 'python' );
plbLabbookRoot = os.path.join( plbPythonRoot, 'pyLabbook', 'labbooks' );
plbProtocolRoot = os.path.join( plbPythonRoot, 'PyLabbook', 'protocols' );
plbDatabases = os.path.join( plbRoot, 'databases' );
plbRepositories = os.path.join( plbRoot, 'repositories' );
plbExports = os.path.join( plbRoot, 'exports' );
plbImports = os.path.join( plbRoot, 'imports' );

print(plbLabbookRoot + " ", end='', flush=True);
if not os.path.isdir(plbLabbookRoot): print(" MISSING");
else: print(" OK");
print(plbProtocolRoot + " ", end='', flush=True);
if not os.path.isdir(plbProtocolRoot): print(" MISSING");
else: print(" OK");
print(plbDatabases + " ", end='', flush=True);
if not os.path.isdir(plbDatabases): print(" MISSING");
else: print(" OK");
print(plbRepositories + " ", end='', flush=True);
if not os.path.isdir(plbRepositories): print(" MISSING");
else: print(" OK");
print(plbExports + " ", end='', flush=True);
if not os.path.isdir(plbExports): print(" MISSING");
else: print(" OK");
print(plbImports + " ", end='', flush=True);
if not os.path.isdir(plbImports): print(" MISSING");
else: print(" OK");

plbPyLabbookClass = os.path.join(plbPythonRoot,"pyLabbook","pyLabbook.py");
plbPyProtocolClass = os.path.join(plbPythonRoot,"pyLabbook","pyProtocol.py");
plbPyLabbookCore = os.path.join(plbPythonRoot,"pyLabbook","core.py");
plbOps = os.path.join(plbPythonRoot,"operations.py");

print(plbPyLabbookClass + " ", end='', flush=True);
if not os.path.isfile(plbPyLabbookClass): print(" MISSING");
else: print(" OK");

print(plbPyLabbookClass + " ", end='', flush=True);
if not os.path.isfile(plbPyLabbookClass): print(" MISSING");
else: print(" OK");

print(plbPyLabbookCore + " ", end='', flush=True);
if not os.path.isfile(plbPyLabbookCore): print(" MISSING");
else: print(" OK");

print(plbPyLabbookCore + " ", end='', flush=True);
if not os.path.isfile(plbPyLabbookCore): print(" MISSING");
else: print(" OK");

print(plbOps + " ", end='', flush=True);
if not os.path.isfile(plbOps): print(" MISSING");
else: print(" OK");
# pyLabbook imports ############################################################
print();
print("Checking pyLabbook modules and classes");
sys.path.append( plbPythonRoot );
try:
    import pyLabbook;
    print("pyLabbook ".ljust(40,'.')+" "+
        '.'.join([str(v) for v in pyLabbook.__version__]));
except Exception as e:
    print("Can't import pyLabbook: "+str(e));

try:
    from pyLabbook import pyLabbook;
    print("pyLabbook.pyLabbook ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import pyLabbook.pyLabbook: "+str(e));

try:
    from pyLabbook import pyProtocol;
    print("pyLabbook.pyProtocol ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import pyLabbook.pyProtocol: "+str(e));

try:
    from pyLabbook import core;
    print("pyLabbook.core ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import pyLabbook.core: "+str(e));

try:
    from pyLabbook.SQLEngines import engine;
    print("pyLabbook.SQLEngines.engine ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import pyLabbook.SQLEngines.engine: "+str(e));

try:
    from pyLabbook.SQLEngines import manager;
    print("pyLabbook.SQLEngines.manager ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't import pyLabbook.SQLEngines.manager: "+str(e));

try:
    sql = manager.loadSQLEngine('SQLITE3');
    print("SQLITE3 engine ".ljust(40,'.')+" OK");
except Exception as e:
    print("Can't load SQLITE3 engine: "+str(e));

# versionerrors ################################################################
if len(versionerrors)>0:
    print("Warning: you may experience some odd behavior realted to:");
    print("--> " + "\n".join(versionerrors));
################################################################################
print("Done");
