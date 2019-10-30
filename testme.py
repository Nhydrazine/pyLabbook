core_modules = {
    "re"        : [],
    "shutil"    : [],
    "numpy"     : [],
    "sqlite3"   : [],
    "xlrd"      : [],
    "openpyxl"  : [],
    "pandas"    : [0,24],
};
# pandas 0.24.0 or above is now REQUIRED due to NULL string problems with
# loading Excel files.  See https://github.com/pandas-dev/pandas/issues/20377

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
def printtest(module, len=40):
    print((module+ansi.dk_gray+" ").ljust(len,'.')+ansi.clear+' ',
        end='',flush=True);
def printok(): print(ansi.green+"OK"+ansi.clear);
def printerr(err):
    print(ansi.br_red+"ERROR"+" "+ansi.clear+err);
def printmissing(module):
    print(ansi.red+" Install the "+ansi.br_red+module+ansi.red+" module."+ansi.clear);
# python #######################################################################
print("Checking core modules and python");
printtest("sys");
try: import sys;
except Exception as e:
    printerr(str(e));
    sys.exit();
printok();

# python version
printtest("python");
if sys.version_info[0]<3 and sys.version_info[1]<6 and sys.version[2]<5:
    print(ansi.red+"Python 3.6.5+ is required."+ansi.clear);
    sys.exit();
print(ansi.green+'.'.join([str(v) for v in sys.version_info[0:3]])+ansi.clear);

printtest("os");
try: import os;
except Exception as e:
    printerr(str(e));
    sys.exit();
printok();

printtest("importlib");
try: import importlib;
except Exception as e:
    printerr(str(e));
    sys.exit();
printok();

# everyone #####################################################################
def test_module_import(name):
    try:
        importlib.import_module(name);
    except Exception as e:
        return str(e);
    return None;

# test core modules ############################################################
def test_modules(mods):
    errs = 0;
    for k in mods.keys():
        printtest(k);
        err = test_module_import(k);
        if err:
            printerr(err);
            errs+=1;
            continue;
        else:
            # version required?
            if len(mods[k])>0:
                vsp = sys.modules[k].__version__.split('.');
                bad_version = False;
                for i,v in enumerate(mods[k]):
                    if v!=None:
                        if int(vsp[i])<int(mods[k][i]):
                            bad_version = True;
                            break;
                if bad_version:
                    print(  ansi.red+'.'.join(vsp)+ansi.clear+
                            " - version "+'.'.join([str(v) for v in mods[k]])+" or above"+
                            " is required."
                    );
                    errs += 1;
                    continue;
                else:
                    print(  ansi.green+'.'.join(vsp)+ansi.clear);
            else: print(ansi.green+"OK"+ansi.clear);
    return errs;

errs = 0;
errs += test_modules( core_modules );

# manager ######################################################################
print();
print("Checking for manager modules");

try:
    printtest("tkinter");
    import tkinter as tk;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("tkinter.messagebox");
    from tkinter import messagebox;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("tkinter.scrolledtext");
    from tkinter import scrolledtext;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("tkinter.filedialog");
    from tkinter import filedialog;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("tkinter.ttk");
    from tkinter import ttk;
    printok();
except Exception as e:
    printerr(str(e));

# manager widgets ##############################################################
print();
print("Checking for manager widgets");
try:
    printtest("guiWidgets");
    import guiWidgets;
    printok();
except Exception as e:
    printerr(str(e));

w = {};
tkerrs = [];
skip=False;
try: w['tk'] = tk.Tk();
except Exception as e:
    tkerrs.append("can't instantiate Tk: "+str(e));
    skip=True;
if not skip:
    try:
        printtest("ttk.Frame");
        w['frame'] = ttk.Frame(w['tk']);
        printok();
    except Exception as e: printerr(str(e));
    try:
        printtest("ttk.Label");
        w['label'] = ttk.Label(w['tk']);
        printok();
    except Exception as e: printerr(str(e));
    try:
        printtest("ttk.Entry");
        w['entry'] = ttk.Entry(w['tk']);
        printok();
    except Exception as e: printerr(str(e));
    try:
        printtest("ttk.Button");
        w['button'] = ttk.Button(w['tk']);
        printok();
    except Exception as e: printerr(str(e));
    try:
        printtest("ttk.CheckButton");
        w['checkbutton'] = ttk.Checkbutton(w['tk']);
        printok();
    except Exception as e: printerr(str(e));
    try:
        printtest("ttk.Combobox");
        w['combobox'] = ttk.Combobox(w['tk']);
        printok();
    except Exception as e: printerr(str(e));
    try:
        printtest("ttk.Treeview");
        w['treeview'] = ttk.Treeview(w['tk']);
        printok();
    except Exception as e: printerr(str(e));

# pyLabbook structure ##########################################################
plbRoot = os.path.abspath( os.path.dirname( sys.argv[0] ) );
print();
print("Checking pyLabbook distribution at "+ansi.cyan+plbRoot+ansi.clear);

plbPythonRoot = os.path.join( plbRoot, 'python' );
plbLabbookRoot = os.path.join( plbPythonRoot, 'pyLabbook', 'labbooks' );
plbProtocolRoot = os.path.join( plbPythonRoot, 'PyLabbook', 'protocols' );
plbDatabases = os.path.join( plbRoot, 'databases' );
plbRepositories = os.path.join( plbRoot, 'repositories' );
plbExports = os.path.join( plbRoot, 'exports' );
plbImports = os.path.join( plbRoot, 'imports' );

printtest(plbLabbookRoot, len=70);
if not os.path.isdir(plbLabbookRoot): printerr(" MISSING");
else: printok();
printtest(plbProtocolRoot, len=70);
if not os.path.isdir(plbProtocolRoot): printerr(" MISSING");
else: printok();
printtest(plbDatabases, len=70);
if not os.path.isdir(plbDatabases): printerr(" MISSING");
else: printok();
printtest(plbRepositories, len=70);
if not os.path.isdir(plbRepositories): printerr(" MISSING");
else: printok();
printtest(plbExports, len=70);
if not os.path.isdir(plbExports): printerr(" MISSING");
else: printok();
printtest(plbImports, len=70);
if not os.path.isdir(plbImports): print(" MISSING");
else: printok();

plbPyLabbookClass = os.path.join(plbPythonRoot,"pyLabbook","pyLabbook.py");
plbPyProtocolClass = os.path.join(plbPythonRoot,"pyLabbook","pyProtocol.py");
plbPyLabbookCore = os.path.join(plbPythonRoot,"pyLabbook","core.py");
plbOps = os.path.join(plbPythonRoot,"operations.py");

printtest(plbPyLabbookClass, len=70);
if not os.path.isfile(plbPyLabbookClass): printerr(" MISSING");
else: printok();

printtest(plbPyLabbookCore, len=70);
if not os.path.isfile(plbPyLabbookCore): printerr(" MISSING");
else: printok();

printtest(plbOps, len=70);
if not os.path.isfile(plbOps): printerr(" MISSING");
else: printok();

# pyLabbook imports ############################################################
print();
print("Checking pyLabbook modules and classes");
sys.path.append( plbPythonRoot );
try:
    printtest("pyLabbook");
    import pyLabbook;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("pyLabbook.pyLabbook");
    from pyLabbook import pyLabbook;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("pyLabbook.pyProtocol");
    from pyLabbook import pyProtocol;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("pyLabbook.core");
    from pyLabbook import core;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("pyLabbook.SQLEngines.engine");
    from pyLabbook.SQLEngines import engine;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("pyLabbook.SQLEngines.manager");
    from pyLabbook.SQLEngines import manager;
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("SQLITE3 engine");
    sql = manager.loadSQLEngine('SQLITE3');
    printok();
except Exception as e:
    printerr(str(e));

# pyLabbook functions
print();
print("Testing pyLabbook system");

try:
    printtest("Instantiating labbook");
    lb = pyLabbook(
        id              = 'testLabbook',
        root            = plbRoot,
        repositoryPath  = os.path.join(plbRepositories,'testLabbook'),
        sheetFormat     = 'csv',
        databasePath    = 'databases',
        databaseFile    = 'testLabbook.sqlite3',
        databaseFormat  = 'SQLITE3',
    );
    printok();
except Exception as e: printerr(str(e));

try:
    lb_modfile = os.path.join(plbLabbookRoot,'testLabbook.py');
    printtest("Serializing");
    with open(lb_modfile,'w') as fh:
        fh.write(lb.exportSerialized());
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("Importing");
    lb = core.import_initialize_labbook('testLabbook', plbRoot);
    print(ansi.green+lb.id+ansi.clear);
except Exception as e:
    printerr(str(e));

try:
    printtest("Repository");
    lb.createFileStructure();
    if not os.path.isdir( os.path.join(lb.root, lb.repositoryPath) ):
        raise Exception("Not found");
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("Creating sample protocol");
    pr = pyProtocol(lb);
    pr.PROTOCOLID = 'testProtocol';
    pr.addSetColumn(
        name          = "set_name",
        type          = "TEXT",
        notnull       = False,
        unique        = False,
        description   = "name of the set",
        default       = None,
        primary_key   = False,
    );
    pr.addSamColumn(
        name          = "sam_name",
        type          = "TEXT",
        notnull       = False,
        unique        = False,
        description   = "name of the sample",
        default       = None,
        primary_key   = False,
    );
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("Serializing");
    pr_modfile = os.path.join(plbProtocolRoot,'testProtocol.py');
    with open(pr_modfile, 'w') as fh:
        fh.write(pr.exportSerialized());
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("Importing");
    pr = core.import_initialize_protocol('testProtocol', lb);
    print(ansi.green+pr.PROTOCOLID+ansi.clear);
except Exception as e:
    printerr(str(e));

try:
    printtest("Database");
    pr.connect();
    pr.disconnect();
    printok();
except Exception as e:
    printerr(str(e));

try:
    printtest("Cleaning up");
    lb.deleteFileStructure(require_empty=False);
    os.remove( lb_modfile );
    os.remove( pr_modfile );
    printok();
except Exception as e:
    printerr(str(e));

# versionerrors ################################################################
################################################################################
print("Done");
