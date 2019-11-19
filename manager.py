#!/usr/bin/env python
import os, sys, importlib;
import threading;
import numpy as np, pandas as pd;
import tkinter as tk;
from tkinter import messagebox;
from tkinter import scrolledtext;
from tkinter import filedialog;
from tkinter import ttk;
import logging;
import guiWidgets as nw;

# print("numpy "+np.__version__);
# #print("tk "+tk.__version__);
# #print("ttk "+ttk.__version__);
# print("logging "+logging.__version__);

################################################################################
# TODO:
#   20190928.1 -----------------------------------------------------------------
#       multiple setViewers with different targets supported by creating local
#       labbook.protocol instances.  Would be nice to adjust so s.c_labbook and
#       s.c_protocol are not open instantiations but just names.  Instantiation
#       would occur locally for each operation (this would need to be adjusted
#       for all experiment panel operations).
#   20190928.2 -----------------------------------------------------------------
#       'in' logic for setViewer filter using comma separated values isn't
#       working.
#   20190928.3 URGENT > FIXED 20190928 -----------------------------------------
#       set viewer queue buttons are still operating with root.c_labbook and
#       root.c_protocol.  Needs to use its own copy of these.  rewally just need
#       to adjust appendsQueue (here) to include labbook and protocol ids in
#       esids dataframe argument.
#       > FIXED: updated appendsQueue to take a dataframe of labbook_id,
#       protocol_id, experiment_id and set_id as argument.  All calls have
#       been corrected.
#   20190928.4 URGENT ----------------------------------------------------------
#       confirm whether store procedure can be used to delete sets by excluding
#       them and storing, or whether this won't work.  Non-python/db people will
#       need a way of removing sets from the database.  You could use the queue?
#       For example, if using pyLabbook as an inventory system, user will need
#       a way to free locations when items get used up, so need to either clear
#       or delete record(s).
################################################################################
plbRoot = os.path.abspath( os.path.dirname( sys.argv[0] ) );
plbPythonRoot = os.path.join( plbRoot, 'python' );
plbLabbookRoot = os.path.join( plbPythonRoot, 'pyLabbook', 'labbooks' );
plbProtocolRoot = os.path.join( plbPythonRoot, 'pyLabbook', 'protocols' );
################################################################################
sys.path.append( plbPythonRoot );
#from guiObjects import *;
import operations as ops;
from pyLabbook import pyLabbook, pyProtocol;
from pyLabbook.SQLEngines import engine;
import pyLabbook.core as core;
dummy_labbook = pyLabbook(
    id="dummy",
    root=plbRoot,
    repositoryPath=plbRoot,
    sheetFormat='xlsx',
    databasePath=plbRoot,
    databaseFile="temp.sqlite3",
    databaseFormat='SQLITE3',
);
dummy_engine = engine.SQLEngine();
################################################################################
class pyLabbookManagerApp(tk.Tk):
    def __init__(s):

        tk.Tk.__init__(s);
        s.resizable(width=False, height=False);
        s.title("pyLabbook");
        s.container = ttk.Frame(s);
        s.container.pack(fill='both', expand=True);
        s.container2 = ttk.Frame(s);
        s.container2.pack();
        # styling
        s.style = ttk.Style();
        s.style.theme_use('default');
        s.bTrue = '\u25CF';
        s.bFalse = '\u25CB';
        s.c_labbook = None;
        s.c_protocol = None;
        s.q_labbook = None;
        s.glob = {};

        # widget grid
        padx = 10; # panel padding
        pady = 20; # panel padding
        s.wgrid = nw.widgetGrid(s.container2, nw.spec(name='grid'));
        s.wgrid.add(0, 0,
            nw.labbookPane(
                s.wgrid,
                    nw.spec(name='l_pane'),
                    columnspecs=[
                        nw.spec(name='id', label='ID')
                    ],
                    root=s
            ),
            packKWA={'padx':padx, 'pady': pady},
        );
        s.wgrid.add(1, 0,
            nw.protocolPane(
                s.wgrid,
                nw.spec(name='p_pane'),
                columnspecs=[
                    nw.spec(name='id', label='ID')
                ], root=s
            ),
            packKWA={'padx':padx, 'pady': pady},
        );
        s.wgrid.add(2, 0,
            nw.experimentPane(
                s.wgrid,
                nw.spec(name='e_pane'),
                root=s
            ),
            packKWA={'padx':padx, 'pady': pady},
        );
        s.wgrid.add(3, 0,
            nw.queuePane(
                s.wgrid,
                nw.spec(name='q_pane'),
                root=s
            ),
            packKWA={'padx':padx, 'pady': pady},
        );
        s.wgrid.make(0, 1,
            nw.spec(name='sep',
                widgetClass=ttk.Separator,
                createKWA={'orient': 'horizontal'},
                packKWA={'fill':'both'},
            ),
            packKWA={'columnspan':4, 'sticky':'nesw'}
        );
        s.wgrid.make(0, 2,
            nw.spec(name='logbox', default="test",
                widgetClass=scrolledtext.ScrolledText,
                packKWA={'fill':'both'},
                createKWA={'height': 10, 'state':'disabled'},
            ),
            packKWA={'columnspan':4,'sticky':'nesw','padx':padx,'pady':10},
        );
        s.wgrid.make(0, 3,
            nw.spec(name='bsp',
                widgetClass=ttk.Frame,
            ),
            packKWA={'columnspan':4,'sticky':'nesw','padx':padx,'pady':10},
        );

        # logging (debug, info, warn, error, critical)
        s.text_handler = nw.TextHandler( s.wgrid.widget('logbox').obj );
        s.logger = logging.getLogger();
        s.logger.setLevel(logging.DEBUG);
        s.logger.addHandler( s.text_handler );

        # pack
        s.wgrid.packWidgets();
        s.wgrid.pack(fill='both');

        # begin
        s.wgrid.widget('l_pane')._refreshList();
        s.wgrid.widget('p_pane')._refreshList();
        s.initializeLabbookPane();
        s.initializeProtocolPane();
        s.logger.info("pyLabbook Manager Interface 0.b.1");
        s.logger.info("---------------------------------");

        # pandas version warning
        try:
            pver = pd.__version__.split('.');
        except:
            s.logger.warn("Can't determine what version pf pandas is "+
                "installed.\nYou may experience odd issues with spreadsheet "+
                "exports from the queue panel.\nPlease ensure pandas "+
                +"version 0.24.0 or above.");
        if int(pver[1])<24:
            s.logger.warn("Your version of pandas is <0.24.0.\n"+
                "You may experience odd issues with spreadsheet exports "+
                "using the queue panel.\n"+
                "Please upgrade to 0.24.0 or above");
        # mainloop
        s.mainloop();
    ############################################################################
    def initializeLabbookPane(s): s.updateLabbookList();
    ############################################################################
    def initializeProtocolPane(s): s.updateProtocolList();
    ############################################################################
    def initializeExperimentPane(s): return;
    ############################################################################
    def updateLabbookList(s):
        """Update list of labbooks in labbook panel."""
        labbooks = pd.DataFrame(columns=['id']);
        labbooks['id'] = pd.Series(
            ops.listPyFiles(plbLabbookRoot)
        ).sort_values();
        s.wgrid.widget('l_pane').wgrid.widget('treebox').loadDataFrame(
            labbooks);
        # focus/highlight first item if there
        try:
            ltb = s.wgrid.widget('l_pane').wgrid.widget('treebox');
            f = ltb.obj.get_children()[0];
            ltb.obj.focus(f);
            ltb.obj.selection_set(f);
        except: pass;
    ############################################################################
    def updateProtocolList(s):
        """Update list of protocols in protocol panel."""
        protocols = pd.DataFrame(columns=['id']);
        protocols['id'] = pd.Series(
            ops.listPyFiles(plbProtocolRoot)).sort_values();
        s.wgrid.widget('p_pane').wgrid.widget('treebox').loadDataFrame(
            protocols);
        # focus first item if there
        try:
            ptb = s.wgrid.widget('p_pane').wgrid.widget('treebox');
            f = ltb.obj.get_children()[0];
            ptb.obj.focus(f);
            ptb.obj.selection_set(f);
        except: pass;
    ############################################################################
    def unSetExperimentLabbookProtocol(s):
        s.c_protocol.disconnect();
        s.c_protocol = None;
        s.c_labbooks = None;
        s.logger.info("Experiment panel untargeted.");
        s.wgrid.widget('e_pane').hgrid.widget('plb').var.set("");
        s.wgrid.widget('e_pane').wgrid.widget('treebox').clearAll();
    ############################################################################
    def setExperimentLabbookProtocol(s):
        """Target labbook/protocol to experiment panel."""
        labbook_treebox = s.wgrid.widget('l_pane').wgrid.widget('treebox');
        labbook_tix = labbook_treebox.obj.focus();
        labbook_id = labbook_treebox.row(labbook_tix)['id'];
        # get selected protocol id
        protocol_treebox = s.wgrid.widget('p_pane').wgrid.widget('treebox');
        protocol_tix = protocol_treebox.obj.focus();
        protocol_id = protocol_treebox.row(protocol_tix)['id'];
        # disconnect
        if s.c_protocol!=None:
            lbp = s.c_labbook.id+'.'+s.c_protocol.PROTOCOLID;
            try: s.c_protocol.disconnect();
            except Exception as e:
                messagebox.errormessage("Error","Error disconnecting from "+
                    lbp+": "+str(e));
        # import labbook
        try:
            lbmod = '.'.join(['pyLabbook','labbooks',labbook_id]);
            s.importModPath( lbmod );
        except Exception as e:
            messagebox.showerror("Error","Error importing "+lnmod+": "+str(e));
            return False;
        # try to initialize
        try: s.c_labbook = sys.modules[lbmod].initialize(plbRoot);
        except Exception as e:
            messagebox.showerror("Error","Error initializing "+lbmod+": "+
                str(e));
            return False;
        # import protocol
        try:
            pmod = '.'.join(['pyLabbook','protocols',protocol_id]);
            s.c_protocol = s.importModPath( pmod );
        except Exception as e:
            messagebox.showerror("Error","Error importing "+pmod+": "+str(e));
            return False;
        # try to initialize
        try: s.c_protocol = sys.modules[pmod].initialize(s.c_labbook);
        except Exception as e:
            messagebox.showerror("Error","Error initializing "+pmod+": "+
                str(e));
            return False;
        # don't connect to database
        # this is done when needed, to prevent thread clashes
        lbp = '.'.join([s.c_labbook.id,s.c_protocol.PROTOCOLID]);
        s.logger.info("Experiment panel targeted to "+lbp+".");
        s.updateExperimentList();
    ############################################################################
    def updateExperimentList(s):
        """Update experiments list in experiments panel."""
        if s.c_labbook==None or s.c_protocol==None: return;
        #
        lbp='.'.join([s.c_labbook.id, s.c_protocol.PROTOCOLID]);
        # connect to labbook sdatabase via. protocol
        s.c_protocol.disconnect();
        s.c_protocol.connect();
        # get inspector report from pyProtocol
        try: report  = s.c_protocol.inspect().sort_values(by='experiment_id');
        except Exception as e:
            # this exception usually means that protocol tables are missing
            s.logger.info("No experiments for "+lbp);
            # update experiment pane label
            s.wgrid.widget('e_pane').hgrid.widget('plb').var.set(lbp);
            s.wgrid.widget('e_pane').wgrid.widget('treebox').clearAll();
            return;
        # get column names from experiment panel
        ep_cols = [c.name for c in s.wgrid.widget('e_pane').columnspecs];
        # load report data into panel treebox
        s.wgrid.widget('e_pane').wgrid.widget('treebox').loadDataFrame(
            report[ep_cols]);
        # update experiment pane label
        s.wgrid.widget('e_pane').hgrid.widget('plb').var.set(lbp);
        # disconnect
        s.c_protocol.disconnect();
    ############################################################################
    def importModPath(s, mp):
        """Imports a module by path if not already imported."""
        if mp not in sys.modules: module = importlib.import_module(mp);
    ############################################################################
    def deleteProtocol(s):
        """Delete a protocol file."""
        pid = s.wgrid.widget('p_pane')._selectedItemID();
        lid = s.wgrid.widget('l_pane')._selectedItemID();
        warnmsg = (
            "!! Existing "+str(pid)+" data will be orphaned "+
            "and will have to be managed manually !!\n" +
            "Are you sure you want to delete "+str(pid)+"?");
        if messagebox.askyesno("Warning!", warnmsg, default='no'):
            ffn = os.path.join(plbProtocolRoot, pid + '.py');
            if not os.path.isfile(ffn):
                messagebox.showerror("Error!", "Couldn't find "+ffn+"...");
                return;
            try: core.rmfile(ffn);
            except Exception as e:
                messagebox.showerror("Error!", str(e));
                return;
            messagebox.showinfo("Success!", pid+" has been deleted.");
            if s.c_protocol!=None:
                if pid==s.c_protocol.PROTOCOLIDL:
                    s.unSetExperimentLabbookProtocol();
    ############################################################################
    def defineProtocol(s):
        """Launch protocol maker window."""
        pm = nw.protocolMaker(s, nw.spec(name='pm')).grab();
    ############################################################################
    def createProtocol(s,protocol_object):
        """Create a new protocol."""
        try:
            ops.createProtocol(
                destinationpath = plbProtocolRoot,
                destinationfile = str(protocol_object.PROTOCOLID) + ".py",
                overwrite = False,
                pyprotocol_object = protocol_object
            );
        except Exception as e:
            messagebox.showerror("Error","Error saving protocol: " + str(e));
            return False;
        # messagebox.showinfo("Success", "Protocol '" +
        #     str(protocol_object.PROTOCOLID) + "' successfully created.");
        s.logger.info("Created protocol "+protocol_object.PROTOCOLID+".");
        s.updateProtocolList();
        return True;
    ############################################################################
    def defineLabbook(s):
        """Launch labbook maker window."""
        lm = nw.labbookMaker(s, nw.spec(name='lm')).grab();
    ############################################################################
    def createLabbook(s,labbook_object, importdb=None):
        """Create a new labbook."""
        progress = nw.progressWindow(s);
        #----------------------------------------------------------------------#
        def create():
            progress.obj['value']=0;
            progress.var.set("Creating filestructure...");
            try:
                ops.createLabbook(
                    destinationpath = plbLabbookRoot,
                    destinationfile = labbook_object.id + '.py',
                    overwrite = False,
                    labbook_object = labbook_object);
            except Exception as e:
                progress.release();
                messagebox.showerror("Error","Error creating "+labbook_object.id+
                    ": "+str(e));
                return False;
            progress.obj['value']=50;
            # copy import database file if specified
            if importdb!='' and importdb!=None:
                progress.var.set("Copying database...");
                if not core.isfile(importdb):
                    messagebox.showerror("Can't find "+str(importdb)+"...");
                else:
                    try:
                        dst = os.path.join(
                                labbook_object.root,
                                labbook_object.databasePath,
                                labbook_object.databaseFile
                        );
                        core.copyfile(importdb, dst);
                    except Exception as e:
                        progress.release();
                        messagebox.showerror("Error importing database: "+str(e));
            progress.obj['value']=100;
            progress.var.set("Updating list...");
            s.updateLabbookList();
            s.logger.info("Created labbook "+labbook_object.id+".");
            progress.release();
        #----------------------------------------------------------------------#
        threading.Thread(target=create).start();
        return True;
    ############################################################################
    def importDataBase(s): return;
        # databases should be imported into labbooks with the following:
        #   1. import the database into a NEWLY CREATED labbook
        #   2. queue the experients/sets you want to transfer by protocol
        #   3. transfer the queue to your destination labbook
    ############################################################################
    def exportDataBase(s, labbook_id):
        """Export a labbook's database."""
        if labbook_id=='' or labbook_id==None: return False;

        # ask for destination
        dst = filedialog.asksaveasfilename(
            initialdir = os.path.join(plbRoot, 'exports'),
            title="Export "+labbook_id+" Database",
            filetypes=(("sqlite3 files","*.sqlite3"),("all files","*.*")),
            initialfile=labbook_id+".sqlite3",
        );
        if dst=='' or dst==None: return False;

        # go
        progress = nw.progressWindow(s);
        #----------------------------------------------------------------------#
        def export():
            progress.obj['value']=0;
            progress.var.set("Preparing "+labbook_id+"...");
            modpath = '.'.join(['pyLabbook','labbooks',str(labbook_id)]);
            # import if needed
            try: s.importModPath(modpath);
            except Exception as e:
                progress.release();
                messagebox.showerror("Error",
                    "Can't import "+str(labbook_id)+": "+str(e));
                return False;
            # instantiate
            try: labbook = sys.modules[modpath].initialize(plbRoot);
            except Exception as e:
                progress.release();
                messagebox.showerror("Error","Can't initialize "+str(labbook_id)+
                    ": " + str(e));
            # copy
            progress.obj['value']=50;
            progress.var.set("Copying database...");
            src = os.path.join(
                labbook.root,
                labbook.databasePath,
                labbook.databaseFile);
            if not core.isfile(src):
                progress.release();
                messagebox.showerror("Error","Can't find "+str(src)+"...");
                return False;
            else:
                try: core.copyfile(src, dst);
                except Exception as e:
                    progress.release();
                    messagebox.showerror("Error",str(e));
                    return False;
            progress.obj['value']=100;
            progress.release();
            s.logger.info("Exported "+str(src)+" to "+str(dst)+".");
            # messagebox.showinfo("Success","Exported "+str(src)+" to "+str(dst));
        #----------------------------------------------------------------------#
        threading.Thread(target=export).start();

    ############################################################################
    def importProtocol(s):
        """Import protocol."""
        # ask for file
        src = filedialog.askopenfilename(
            initialdir = os.path.join(plbRoot, 'imports'),
            title = "Import Protocol",
            filetypes = (("python files","*.py"),("all files","*.*"))
        );
        if src=='' or src==None: return;
        if not core.isfile(src):
            messagebox.showerror("Error","Can't find"+str(src));
            return False;
        # does the file already exist?
        src_fn = os.path.basename(src);
        src_pid, ext = os.path.splitext(src_fn);
        protocols = ops.listPyFiles( plbProtocolRoot );
        if src_pid in protocols:
            messagebox.showerror("Error","This protocol already exists.");
            return False;
        # copy file
        dst = os.path.join( plbProtocolRoot, src_pid+".py" );
        core.copyfile( src, dst );
        # try to import
        modpath = '.'.join(['pyLabbook','protocols',src_pid]);
        try: s.importModPath(modpath);
        except Exception as e:
            messagebox.showerror("Error","Can't import "+src_pid+": "+str(e));
            core.rmfile(dst);
            return False;
        # try to instantiate
        try: protocol = sys.modules[modpath].initialize(dummy_labbook);
        except Exception as e:
            messagebox.showerror("Error","Can't initialize "+str(protocol_id)+
                ": " + str(e));
            core.rmfile(dst);
            return False;
        # confirm basename matches protocol id
        if protocol.PROTOCOLID!=src_pid:
            messagebox.showerror("Protocol ID does not match filename.");
            core.rmfile(dst);
            return False;
        # additional tests?
        # messagebox.showinfo("Success","Imported "+src+" to "+dst);
        s.logger.info("Imported "+src+" to "+dst+".");
        s.updateProtocolList();
        return True;
    ############################################################################
    def exportProtocol(s, protocol_id):
        """Export protocol."""
        # import and instantiate to confirm validity
        modpath = '.'.join([ 'pyLabbook','protocols',protocol_id ]);
        try: s.importModPath(modpath);
        except Exception as e:
            messagebox.showerror("Error","Can't import "+str(protocol_id)+": "+
                str(e));
            return False;
        # initialize
        try: protocol = sys.modules[modpath].initialize(dummy_labbook);
        except Exception as e:
            messagebox.showerror("Error","Can't initialize "+str(protocol_id)+
                ": " + str(e));
            return False;
        # get destination
        dst = filedialog.askdirectory(
            initialdir = os.path.join(plbRoot, 'exports'),
            title="Export "+protocol_id,
            # filetypes=(("python files","*.py"),("all files","*.*")),
            # initialfile=protocol_id+".py",
        );
        if dst=='' or dst==None: return False;
        dst = os.path.join(dst, protocol_id+'.py');
        # copy
        src = os.path.join(plbProtocolRoot, protocol_id+'.py');
        if not os.path.isfile(src):
            messagebox.showerror("Error","Can't find "+src);
            return False;
        try: core.copyfile(src, dst);
        except Exception as e:
            messagebox.showerror("Error",str(e));
            return False;
        # messagebox.showinfo("Success","Exported "+src+" to "+dst);
        s.logger.info("Exported "+src+" to "+dst+".");
        return True;
    ############################################################################
    def deleteLabbook(s,labbook_id):
        """Delete a labbook."""
        if labbook_id=='': return False;
        # import
        modpath = '.'.join(['pyLabbook','labbooks',labbook_id]);
        # try to import it
        try: s.importModPath(modpath);
        except Exception as e:
            messagebox.showerror("Error","Can't import "+str(labbook_id)+": "+
                str(e));
            return False;
        # initialize
        try: labbook = sys.modules[modpath].initialize(plbRoot);
        except Exception as e:
            messagebox.showerror("Error","Can't initialize "+str(labbook_id)+
                ": " + str(e));
        # confirm delete
        if messagebox.askyesno("Warning","Deleting "+str(labbook.id)+
            " will remove all associated database and repository files.  Are you sure you want to continue?", default='no'
        ):
            modfile = os.path.join(plbLabbookRoot, labbook.id+'.py');
            try: labbook.deleteFileStructure(require_empty=False);
            except Exception as e:
                messagebox.showerror("Error",str(e));
                return False;
            s.logger.info("Labbook "+str(labbook.id)+" repository and "+
                "database deleted.");
            # messagebox.showinfo("Success!","Labbook "+labbook.id+" was "+
            #     "successfully deleted");
            try: core.rmfile(modfile);
            except Exception as e:
                messagebox.showerror("Error",str(e));
                return False;
            s.logger.info("Labbook "+str(labbook.id)+" module deleted.");
            # disconnect and unset experiment
            if s.c_labbook!=None:
                if s.c_labbook.id==labbook_id:
                    s.unSetExperimentLabbookProtocol();
            # disconnect and unset queue
            if s.q_labbook!=None:
                if s.q_labbook.id==labbook_id:
                    s.unSelectQueueLabbook();
            s.updateLabbookList();
            return True;
    ############################################################################
    def defineExperiment(s):
        """Launch experiment creator window."""
        if s.c_labbook==None or s.c_protocol==None:
            messagebox.showwarning("Warning","You need to select a labbook "+
                "and protocol to add the experiment to.");
            return;
        expid = tk.StringVar();
        espec = nw.spec(name='entry', default="", variable=expid);
        z = nw.popupEntry(s,
            mspec=nw.spec(name='message', default="Experiment ID:"),
            espec=espec,
            validator=core.validID,
        ).grab();
    ############################################################################
    def initializeExperiment(s, eid):
        """Initialize an experiment."""
        if s.c_labbook==None or s.c_protocol==None:
            messagebox.showwarning("Warning","You need to select a labbook "+
                "and protocol to add the experiment to.");
            return False;
        full = '.'.join([s.c_labbook.id, s.c_protocol.PROTOCOLID, eid]);
        try: s.c_protocol.createFileStructure();
        except Exception as e:
            messagebox.showerror("Error","Can't create filestructure for "+
                full+": "+str(e));
            return False;
        # connect
        s.c_protocol.connect();
        try: s.c_protocol.createTables(); #if necessary
        except Exception as e:
            messagebox.showerror("Error","Can't create tables "+str(e));
            return False;
        try:
            s.c_protocol.initializeExperiment(eid);
        except Exception as e:
            messagebox.showerror("Error",
                "Error initializing "+full+": "+str(e));
            return False;
        s.c_protocol.disconnect();
        s.updateExperimentList();
        s.logger.info("Initialized "+str(full)+".");
        return True;
    ############################################################################
    def dropExperimentIDS(s, eids):
        """Drop experiment IDs from database."""
        if s.c_labbook==None or s.c_protocol==None: return;
        progress = nw.progressWindow(s);
        def dropus():
            progress.obj['value']=0;
            progress.var.set("Preparing...");
            wheres = pd.DataFrame();
            wheres['experiment_id']=eids;
            progress.obj['value']=30;
            progress.var.set("Dropping...");
            s.c_protocol.connect();
            if len(wheres)<1:
                progress.release();
                return False;
            try: s.c_protocol.deleteSetsAndSamplesWhere(wheres);
            except Exception as e:
                s.c_protocol.disconnect();
                progress.release();
                messagebox.showerror("Error","Error deleting: "+str(e));
                return False;
            lp = '.'.join([s.c_labbook.id,s.c_protocol.PROTOCOLID]);
            s.logger.info("Dropped database records for "+lp+": "+
                ', '.join( str(eid) for eid in wheres['experiment_id'] )+
                ".");
            progress.obj['value']=100;
            progress.var.set("Updating list...");
            s.updateExperimentList();
            progress.release();
        threading.Thread(target=dropus).start();
    ############################################################################
    def deleteExperimentIDS(s, eids):
        """Delete experiments by id."""
        if s.c_labbook==None or s.c_protocol==None:
            messagebox.showwarning("Warning","You need to select a labbook "+
                "and protocol to add the experiment to.");
            return False;
        progress = nw.progressWindow(s);
        #----------------------------------------------------------------------#
        def deleteus(eids):
            total = len(eids);
            complete = 0;
            for eid in eids:
                lbp='.'.join([s.c_labbook.id,s.c_protocol.PROTOCOLID,eid]);
                progress.obj['value'] = int( (complete/total)*100 );
                progress.var.set(lbp);
                if s.c_protocol.experimentPathExists(eid):
                    try: s.c_protocol.deleteExperimentPath(eid);
                    except Exception as e:
                        s.logger.error("Error deleting repository "+lbp+
                            ":"+str(e));
                        continue;
                    s.logger.info("Deleted repository files for "+lbp+".");
                else:
                    s.logger.info("No repository for "+lbp);
                    continue;
                complete += 1;
            progress.obj['value'] = 100;
            progress.var.set("Updating list...");
            s.updateExperimentList();
            progress.release();
        #----------------------------------------------------------------------#
        threading.Thread(target=deleteus, args=[eids]).start();
    ############################################################################
    def storeExperimentIDS(s, eids):
        """Store experiment ids repository to database."""
        # to have list update on the fly need to pass rows relevant
        # to experiment pane.  This would prevent other callers from
        # storing via. this method.
        if s.c_labbook==None or s.c_protocol==None:
            messagebox.showwarning("Warning","You need to select a labbook "+
                "and protocol to add the experiment to.");
            return False;
        progress = nw.progressWindow(s);
        #----------------------------------------------------------------------#
        def store():
            s.c_protocol.connect();
            # create tables if necessary
            s.c_protocol.createTables();
            total = len(eids);
            complete = 0;
            for eid in eids:
                lbp = '.'.join([s.c_labbook.id, s.c_protocol.PROTOCOLID, eid]);
                progress.obj['value'] = int( (complete/total)*100 );
                progress.var.set(lbp);
                complete += 1;
                # repository
                if not s.c_protocol.experimentPathExists(eid):
                    s.logger.info("No repository for "+lbp);
                    continue; # skip
                if not s.c_protocol.setFileExists(eid):
                    s.logger.info("No set file for "+lbp);
                    continue; # skip
                # load
                try:
                    sets = s.c_protocol.loadSetFile([eid]);
                except Exception as e:
                    s.logger.error("Can't load set file for "+lbp+": "+str(e));
                    continue; # skip
                try:
                    sams = s.c_protocol.loadSamFile([eid]);
                except Exception as e:
                    s.logger.error("Can't load sample file for "+lbp+
                        ": "+str(e));
                    continue; # skip
                # handle empties
                if len(sets)==0:
                    s.logger.info("No sets to store for "+lbp);
                    continue; # skip
                if len(sams)==0: sams = s.c_protocol.getEmptySams();
                # store
                try:
                    s.c_protocol.storeSetsAndSamples(
                        sets, sams, method='killreplace', transaction=False);
                except Exception as e:
                    s.logger.error("Error storing "+lbp+": "+str(e)+
                        " - database rolled back.");
                    s.c_protocol.rollback();
                    s.updateExperimentList();
                    progress.release();
                    return False;
                s.logger.info("Stored "+lbp);
            progress.var.set("Updating list...");
            s.c_protocol.disconnect();
            s.updateExperimentList();
            progress.release();
        #----------------------------------------------------------------------#
        s.c_protocol.disconnect();
        threading.Thread(target=store).start();
    ############################################################################
    def restoreExperimentIDS(s, eids):
        """Restore experiment ids from database to repository."""
        if s.c_labbook==None or s.c_protocol==None:
            messagebox.showwarning("Warning","You need to select a labbook "+
                "and protocol to add the experiment to.");
            return False;
        lbp=s.c_labbook.id+'.'+s.c_protocol.PROTOCOLID;

        progress = nw.progressWindow(s);
        s.c_protocol.disconnect();
        #----------------------------------------------------------------------#
        def restore():
            s.c_protocol.connect();
            # get from database
            progress.obj['value']=0;
            progress.var.set("Retreiving data...");
            wheres = pd.DataFrame();
            wheres['experiment_id'] = eids;
            try: sets = s.c_protocol.selectSetsWhere(wheres);
            except Exception as e:
                progress.release();
                messagebox.showerror("Error","Error selecting sets from "+lbp+
                    ": "+str(e));
                return False;
            try: sams = s.c_protocol.selectSamsWhere(wheres);
            except Exception as e:
                progress.release();
                messagebox.showerror("Error","Error selecting samples from "+
                    lbp+": "+str(e));
                return False;
            # check
            progress.var.set("Checking...");
            dbtally = pd.DataFrame(columns=['eid','set','sam']);
            dbtally['eid'] = eids;
            set_ss = \
                dbtally[dbtally['eid'].isin(sets['experiment_id'].unique())];
            sam_ss = \
                dbtally[dbtally['eid'].isin(sams['experiment_id'].unique())];
            dbtally.loc[set_ss.index,'set'] = 1;
            dbtally.loc[sam_ss.index,'sam'] = 1;
            orphaned = dbtally[(dbtally['set']!=1)&(dbtally['sam']==1)];
            if len(orphaned)>0:
                if not messagebox.askyesno("Error","The following experiments "+
                    "have orphaned samples: "+
                    "\n".join(orphaned['experiment_id'])+"\n"+
                    "these experiments will be skipped until fixed.\n"+
                    "\n"
                    "Continue with the rest?", default='yes'
                ):
                    progress.release();
                    return False;
            update = dbtally[dbtally['set']==1];
            total = len(update);
            completed = 0;
            for i,r in update.iterrows():
                progress.obj['value'] = int( (completed/total)*100 );
                completed += 1;
                eid = r['eid'];
                progress.var.set(str(eid)+"...");
                llbp = lbp+"."+str(eid);
                # subset
                set_ss = sets[sets['experiment_id']==eid];
                if len(set_ss)<1: set_ss = s.c_protocol.getEmptySets();
                sam_ss = sams[sams['experiment_id']==eid];
                if len(sam_ss)<1: sam_ss = s.c_protocol.getEmptySams();
                # check repository
                # if not s.c_protocol.experimentPathExists(eid):
                #     s.logger.info("Initializing repository for "+llbp);
                # write
                write_eid = "";
                if len(set_ss)<1: write_eid = eid;
                try:
                    progress.var.set("Writing sets "+str(eid));
                    s.c_protocol.writeSets(set_ss,eid=write_eid, overwrite=True, initialize=True);
                except Exception as e:
                    s.logger.error("Error writing set file for "+llbp+
                        ": "+str(e));
                    continue; #skip

                write_eid = "";
                if len(sam_ss)<1: write_eid = eid;
                try:
                    s.c_protocol.writeSams(sam_ss, eid=write_eid,
                        overwrite=True);
                    progress.var.set("Writing samples "+str(eid));
                except Exception as e:
                    s.logger.error("Error writing sample file for "+llbp+
                        ": "+str(e));
                    continue; #skip
                s.logger.info("Restored "+llbp+".");
            progress.obj['value'] = 100;
            progress.var.set("Updating list...");
            s.c_protocol.disconnect();
            s.updateExperimentList();
            progress.release();
        #----------------------------------------------------------------------#
        threading.Thread(target=restore).start();
        return True;
    ############################################################################
    def inspectExperimentID(s,eid):
        """Open set viewer with experiment id."""
        lbpath = s.c_labbook.id+'.'+s.c_protocol.PROTOCOLID+'.'+eid;
        setdesc = s.c_protocol.setDesc();
        colspecs = [];
        def intformat(x):
            if x!=None and pd.notnull(x):
                try: return str(int(x));
                except: return "";
            else: return "";
        def floatformat(x):
            if x!=None and pd.notnull(x):
                try: return str(float(x));
                except: return "";
            else: return "";
        def boolformat(x):
            if x!=None:
                try:
                    if x==True: return 'Y';
                    else: return 'N';
                except: return "";
            else: return "";
        def strformat(x):
            if x!=None and pd.notnull(x): return str(x);
            else: return "";

        formatters = {
            str: lambda x: strformat(x),
            int: lambda x: intformat(x),
            float: lambda x: floatformat(x),
            bool: lambda x: boolformat(x),
        };

        # build column specs
        for i,r in setdesc.iterrows():
            typewidth = 100;
            type = s.c_protocol.sql.dmap[ r['type'] ]['py'];
            if dummy_engine.dmap[ r['type'] ]['py']==int: typewidth=40;
            elif dummy_engine.dmap[ r['type'] ]['py']==float: typewidth=50;
            elif dummy_engine.dmap[ r['type'] ]['py']==bool: typewidth=20;
            colspecs.append(nw.spec(
                name=r['name'],
                label=r['name'],
                width=typewidth,
                displayFormatter=formatters[ type ]
            ));

        # build wheres
        wheres = pd.DataFrame([[None,'experiment_id','=',eid]],
            columns=['andor','field','op','value']);

        # launch set viewer window
        # give set viewer separate instances of labbook and protocol so user
        # can have multiple set viewers with different targets.
        # this should be revised so that labbook/protocol are only truly
        # instantiated locally for each operation - no open
        # labbook/protocol instantiations as s.c_
        lmp = '.'.join(['pyLabbook','labbooks',s.c_labbook.id]);
        pmp = '.'.join(['pyLabbook','protocols',s.c_protocol.PROTOCOLID]);
        try: lbo = sys.modules[lmp].initialize(plbRoot);
        except Exception as e:
            messagebox.showerror("Error","Error initializing "+lmp+": "+str(e));
            return False;
        try: pro = sys.modules[pmp].initialize(lbo);
        except Exception as e:
            messagebox.showerror("Error","Error initializing "+pmp+": "+str(e));
            return False;
        nw.setViewer(
            s,
            lbpath,
            wheres,
            lbo,
            pro,
            columnspecs=colspecs,
        );
        return;
    ############################################################################
    def unSelectQueueLabbook(s):
        s.q_labbook=None;
        s.wgrid.widget('q_pane').selectedbook.set("");
        s.logger.info("Queue untargeted.");
    ############################################################################
    def selectQueueLabbook(s):
        """Target labbook to queue."""
        # get
        lbid = s.wgrid.widget('l_pane')._selectedItemID();
        if lbid=='': return;
        # try to activate
        mpath = '.'.join(['pyLabbook','labbooks',lbid]);
        try: s.importModPath(mpath);
        except Exception as e:
            messagebox.showerror("Error","Error importing labbook: "+str(e));
            return;
        try: s.q_labbook = sys.modules[mpath].initialize(plbRoot);
        except Exception as e:
            messagebox.showerror("Error","Error initializing labbook: "+str(e));
            return;
        s.wgrid.widget('q_pane').selectedbook.set(lbid);
        s.logger.info("Queue targeted to "+s.q_labbook.id+".");
    ############################################################################
    def appendsQueue(s,lpesids):
        """Append lpes ids to queue."""
        if s.c_labbook==None or s.c_protocol==None: return;
        lpesids = lpesids[[
            'labbook_id',
            'protocol_id',
            'experiment_id',
            'set_id'
        ]].copy();
#        esids['labbook_id'] = s.c_labbook.id;
#        esids['protocol_id'] = s.c_protocol.PROTOCOLID;
        lpesids['status'] = '';
        s.wgrid.widget('q_pane').obj.appendDataFrame(lpesids);
        s.logger.info("Added "+str(len(lpesids))+" records to queue");
    ############################################################################
    def _q_simplify_qdf(s, qdf, skiptargeted=True):
        """Simplifies queue list by removing duplicates and overlaps."""
        qdf = qdf.copy();
        # remove duplicates keep first
        qdf = qdf.drop_duplicates(
            subset=[
                'labbook_id',
                'protocol_id',
                'experiment_id',
                'set_id'
            ],
            keep='first'
        );
        # remove targeted if specified
        if skiptargeted==True:
            qdf = qdf[qdf['labbook_id']!=s.q_labbook.id];
        # remove overlaps
        drop_ix = [];
        _lpes = \
            qdf['labbook_id']+'~'+qdf['protocol_id']+'~'+qdf['experiment_id'];
        for lpe in _lpes.unique():
            ids = lpe.split('~');
            ss = qdf[
                (qdf['labbook_id']==ids[0])&
                (qdf['protocol_id']==ids[1])&
                (qdf['experiment_id']==ids[2])
            ];
            if '*' in ss['set_id'].tolist():
                drop_ix += ss[ss['set_id']!='*'].index.tolist();
        qdf = qdf.drop(labels=drop_ix, axis=0);
        # raise on conflicting experiment id's across multiple labbook.protocol
        # this is intended to maintain the integrity of experimental sets
        # raise or build interface to figure out what to do with them
        _pes = qdf['protocol_id']+'~'+qdf['experiment_id'];
        for pe in _pes.unique():
            ids = pe.split('~');
            # subset
            ss = qdf[
                (qdf['protocol_id']==ids[0])&
                (qdf['experiment_id']==ids[1])
            ];
            # how many unique labbooks?
            if len(ss['labbook_id'].unique())>1:
                # get list of clashing ids for reporting
                clashes =   ss['labbook_id']+'.'+ss['protocol_id']+'.'+\
                            ss['experiment_id']+'.'+ss['set_id'];
                raise Exception("clashing ids: "+
                    ', '.join(clashes));
        return qdf;
    ############################################################################
    def massImport(s, qdf, dst_lbo=None):
        """Imports and intializes a list of labbook and protocol combos."""
        # simplify
        objs = qdf[['labbook_id','protocol_id']].copy().drop_duplicates();
        # build/initialize rest of structure
        # labbook~protocol combo for uniqueness
        objs['lp'] = objs['labbook_id']+'~'+objs['protocol_id'];
        # labbook and protocol import namespaces
        objs['lmp'] = 'pyLabbook'+'.'+'labbooks'+'.'+objs['labbook_id'];
        objs['pmp'] = 'pyLabbook'+'.'+'protocols'+'.'+objs['protocol_id'];
        # actual initialized objects
        objs['lbo'] = None; # labbook objects
        objs['pro'] = None; # protocol objects initialized with rsp. labbook

        # handle destination if specified
        d_objs = pd.DataFrame(columns=objs.columns);
        if dst_lbo!=None:
            d_objs['protocol_id'] = objs['protocol_id'].unique();
            d_objs['labbook_id'] = dst_lbo.id;
            d_objs['lmp'] = 'pyLabbook'+'.'+'labbooks'+'.'+d_objs['labbook_id'];
            d_objs['pmp'] = 'pyLabbook'+'.'+'protocols'+'.'+\
                            d_objs['protocol_id'];
            d_objs['lbo'] = dst_lbo;
            d_objs['pro'] = None;

        # import labbooks
        for lmp in objs['lmp'].unique():
            s.importModPath(lmp);

        # import protocols
        for pmp in objs['pmp'].unique():
            s.importModPath(pmp);

        # initialize labbooks
        for lid in objs['labbook_id'].unique():
            ss = objs[objs['labbook_id']==lid];
            lobj = sys.modules[ ss['lmp'].iloc[0] ].initialize( plbRoot );
            objs.loc[ss.index,'lbo'] = lobj; # store

        # initialize protocols
        for i,r in objs.iterrows():
            pobj = sys.modules[ r['pmp'] ].initialize(r['lbo']);
            objs.loc[i,'pro'] = pobj; # store

        # initialize protocols with destination if specified
        for i,r in d_objs.iterrows():
            pobj = sys.modules[ r['pmp'] ].initialize(r['lbo']);
            d_objs.loc[i,'pro'] = pobj;

        # merge if needed
        if len(d_objs)>0: return pd.concat([ objs, d_objs ]);
        else: return objs;
    ############################################################################
    def queueImportDB(s):
        """import queued data to targeted labbook database."""
        if s.q_labbook==None:
            messagebox.showerror("Error","Select a destination labbook first.");
            return;
        progress = nw.progressWindow(s);
        #----------------------------------------------------------------------#
        def importdb():
            # get queue and simplify
            progress.obj['value']=0;
            progress.var.set("Processing queue...");
            qdf = s.wgrid.widget('q_pane').getVar().copy();
            cols = list(qdf.columns); # dereference
            try: qdf = s._q_simplify_qdf(qdf, skiptargeted=False);
            except Exception as e:
                messagebox.showerror("Error","Error processing queue: "+str(e));
                progress.release();
                return False;

            # import and instantiate labbook/protocol combos
            progress.var.set("Initializing labbooks and protocols...");
            lp_objects = s.massImport(qdf, dst_lbo=s.q_labbook);

            # get destination and source subsets for objects
            dst_objects = lp_objects[lp_objects['labbook_id']==s.q_labbook.id];
            src_objects = lp_objects[lp_objects['labbook_id']!=s.q_labbook.id];
            # go through all queue transfers, try, and indicate status
            # now go
            status = qdf[[
                'labbook_id',
                'protocol_id',
                'experiment_id',
                'set_id',
                'status'
            ]].copy();
            total = len(qdf);
            complete = 0;
            # ref to queue treebox list
            q_tbox = s.wgrid.widget('q_pane').wgrid.widget('treebox');
            q_tbox_cols = [sp.name for sp in q_tbox.columnSpecs];
            progress.var.set("Transferring...");
            for lid in status['labbook_id'].unique():
                l_ss = status[status['labbook_id']==lid];
                for pid in l_ss['protocol_id'].unique():
                    # get protocol references for simplicity (s src, d dest)
                    d_pobj = dst_objects['pro'][
                        (dst_objects['labbook_id']==s.q_labbook.id)&
                        (dst_objects['protocol_id']==pid)
                    ].iloc[0];
                    s_pobj = src_objects['pro'][
                        (src_objects['labbook_id']==lid)&
                        (src_objects['protocol_id']==pid)
                    ].iloc[0];
                    # subset qdf experiments/sets
                    ss = status[
                        (status['labbook_id']==lid)&
                        (status['protocol_id']==pid)
                    ];
                    # connect src and dst protocols
                    d_pobj.connect();
                    s_pobj.connect();
                    # make tables at destination if needed
                    d_pobj.createTables();
                    # list of experiment/set count at destination
                    d_exp_count = \
                        d_pobj.countExperimentsSets(ss['experiment_id']);
                    # transfer list excludes those at destination
                    # DO NOT AUTOMATICALLY OVERWRITE
                    # makes it easy for user to mix altered records
                    # user should delete first
                    transfer_rows = status[~status['experiment_id'].isin(
                        d_exp_count['experiment_id'])];
                    # mark and store notransfer row records
                    notransfer_rows = status[status['experiment_id'].isin(
                        d_exp_count['experiment_id'])];

                    # adjust progress bar counter and status
                    status.loc[notransfer_rows.index, 'status']="Exists";
                    complete += len(notransfer_rows);
                    for i,r in notransfer_rows.iterrows():
                        q_tbox.obj.item(i,
                            values=status.loc[i,q_tbox_cols].tolist());

                    # now go through transfer rows
                    for eid in transfer_rows['experiment_id'].unique():
                        lbp = '.'.join([lid,pid,eid]);
                        progress.obj['value'] = int( (complete/total)*100 );
                        progress.var.set(lbp);
                        complete += 1;
                        # subset
                        ess = ss[ss['experiment_id']==eid];
                        # build where conditions for selects
                        if len(ess)==0: continue;
                        if len(ess)==1: # either all sets or one set ('*')
                            sid = ess['set_id'].iloc[0];
                            if sid=='*': # all sets
                                wheres = pd.DataFrame(
                                    [[eid]],
                                    columns=['experiment_id']
                                );
                            else: # specific set
                                wheres = pd.DataFrame(
                                    [[eid, sid]],
                                    columns=['experiment_id','set_id']
                                );
                        else: # multiple sets
                            wheres = ess[['experiment_id','set_id']].copy();
                        # select
                        sets = s_pobj.selectSetsWhere(wheres);
                        sams = s_pobj.selectSamsWhere(wheres);

                        # store
                        # NOTE: method killreplace raise unique constraint error
                        # NOTE: use ignore to enforce delete before alter
                        if len(sets)>0:
                            try:
                                d_pobj.storeSets(sets, method='ignore');
                            except Exception as e:
                                status.loc[ess.index,'status'] = "SET ERR";
                                s.logger.error("Error storing sets for "+lbp+
                                    ": "+str(e));
                                continue;
                                # raise;
                        if len(sams)>0:
                            try:
                                d_pobj.storeSams(sams, method='ignore');
                            except Exception as e:
                                status.loc[ess.index,'status'] = "SAM ERR";
                                s.logger.error("Error storing sams for "+lbp+
                                    ": "+str(e));
                                continue;
                                # raise;
                        status.loc[ess.index,'status'] = 'OK';
                        # update status in queue panel
                        for i,r in ess[q_tbox_cols].iterrows():
                            q_tbox.obj.item(i,
                                values=status.loc[i,q_tbox_cols].tolist());
                        dlbp = '.'.join([s.q_labbook.id,pid,eid]);
                        s.logger.info("Transferred records "+lbp+
                            " --> "+dlbp+".");
                    # disconnect before we move to next labbook/pid
                    d_pobj.disconnect();
                    s_pobj.disconnect();
                # what to do before we go to next labbook
            # done iterating --------------------------------------------------#
            progress.obj['value']=100;
            progress.var.set("Updating list...");
            # update queue status
            # not needed anymore, queue is updated on the fly
            # s.wgrid.widget('q_pane').obj.loadDataFrame(status);
            # update experiment list if queue labbook is targeted in exps
            if s.c_labbook.id==s.q_labbook.id:
                if s.c_protocol.PROTOCOLID in qdf['protocol_id'].tolist():
                    s.updateExperimentList();
            progress.release();
        #----------------------------------------------------------------------#
        threading.Thread(target=importdb).start();
        return;
############################################################################
    def queueExportSpreadSheets(s):
        """Export queued data to spreadsheet file(s)."""
        values = {};
        nw.exportQueueSpreadSheetWindow(s,values).grab();
        if  not 'format' in values.keys() or \
            not 'destination' in values.keys() or \
            not 'separate' in values.keys() or \
            not 'ignoredups' in values.keys() or \
            not 'reclimit' in values.keys():
            return;
        # setup progress bar
        progress = nw.progressWindow(s);
        progress.obj['value']=0;
        progress.var.set("Starting...");
        ########################################################################
        def _doexport():
        ########################################################################
            progress.var.set("Processing queue...");
            # get queue
            qdf = s.wgrid.widget('q_pane').getVar().copy();
            # simplify qdf
            try: qdf = s._q_simplify_qdf(qdf, skiptargeted=False);
            except Exception as e:
                messagebox.showerror("Error","Error processing queue: "+str(e));
                progress.release();
                return False;

            # try importing everything first
            lbobjs = {};
            probjs = {};
            qdf['lbo']=None;    # column of labbook objects
            qdf['pro']=None;    # column of protocol objects initialized to source
            qdf['prd']=None;    # column of protocol objects initialized to dest
            # populate qdf columns with references to properly initialized labbook and protocol objects
            # initialize protocols with source first
            lp_objects = pd.DataFrame(
                columns=[
                    'ix',           # labbook_id.protocol_id
                    'labbook_id',   # labbook_id
                    'protocol_id',  # protocol_id
                    'lbmp',         # import namespace path for labbook module
                    'prmp',         # import namespace path for protocol module
                    'lbo',          # labbook object
                    'pro'           # protocol object initialized to labbook
            ]);
            # gather unique labbook/protocol combos
            lp_objects['labbook_id'] = qdf['labbook_id'];
            lp_objects['protocol_id'] = qdf['protocol_id'];
            lp_objects = lp_objects.drop_duplicates();
            # drop dups again just in case
            lp_objects = lp_objects.drop_duplicates();
            # build l.p index
            lp_objects['ix'] = \
                lp_objects['labbook_id']+'.'+lp_objects['protocol_id'];
            # build import namespaces
            lp_objects['lbmp'] = \
                'pyLabbook'+'.'+'labbooks'+'.'+lp_objects['labbook_id'];
            lp_objects['prmp'] = \
                'pyLabbook'+'.'+'protocols'+'.'+lp_objects['protocol_id'];

            # check/import
            progress.var.set("Checking labbooks and protocols...");
            importpaths = lp_objects['lbmp'].unique().tolist();
            importpaths += lp_objects['prmp'].unique().tolist();

            # import
            progress.var.set("Importing...");
            for mp in importpaths:
                try: s.importModPath(mp);
                except Exception as e:
                    progress.release();
                    messagebox.showerror("Error","Can't import "+mp+": "+str(e));
                    return;

            # initialize labbooks
            progress.var.set("Initializing...");
            for lbid in lp_objects['labbook_id'].unique():
                ss = lp_objects[lp_objects['labbook_id']==lbid];
                try: lbo = sys.modules[ ss['lbmp'].iloc[0] ].initialize(plbRoot);
                except Exception as e:
                    progress.release();
                    messagebox.showmessage("Error","Can't initialize"+lbid+": "+
                        str(e));
                    return;
                lp_objects.loc[ss.index,'lbo'] = lbo;
            # initialize protocols using l.p index
            for ix in lp_objects['ix'].unique():
                ss = lp_objects[lp_objects['ix']==ix];
                try:
                    # don't forget need to give labbook object to initialize
                    pro = sys.modules[ ss['prmp'].iloc[0] ].initialize(
                        ss['lbo'].iloc[0]
                    );
                except Exception as e:
                    progress.release();
                    messagebox.showmessage("Error","Can't initailize"+ix+
                        ": "+str(e));
                    return;
                lp_objects.loc[ss.index,'pro'] = pro;

            # go through all queue transfers, try, and indicate status
            # now go
            status = qdf[[
                'labbook_id',
                'protocol_id',
                'experiment_id',
                'set_id',
                'status'
            ]].copy();

            # specify file extension from format
            if values['format']=='csv': file_ext='.csv';
            elif values['format']=='xlsx': file_ext='.xlsx';
            else:
                progress.release();
                messagebox.showerror("Error","Unrecognized format: "+
                    str(values['format']));
                return False;

            # write function
            def writeto(ffn, df, fmt):
                # if file exists then append, otherwise write
                # write mode
                mode = 'w';
                if os.path.isfile(ffn): mode='a'; # append if exists
                # write/format
                if fmt=='xlsx':
                    sheet = 'Sheet1';
                    xw = pd.ExcelWriter(ffn, mode=mode);
                    df.to_excel(xw, sheet_name=sheet, index=False, header=True);
                    xw.save();
                    xw.close();
                elif fmt=='csv':
                    df.to_csv(ffn, mode=mode, index=False, header=True);
                else:
                    raise Exception("Unrecognized format "+str(fmt));
                return;

            reclimit = values['reclimit']; # write to file once this many records are loaded
            # for progress bar
            lpeids =    qdf['labbook_id']+'.'+\
                        qdf['protocol_id']+'.'+\
                        qdf['experiment_id'];
            total_lpeids = len(lpeids);
            done_lpeids = 0;
            q_tbox = s.wgrid.widget('q_pane').wgrid.widget('treebox');
            q_tbox_cols = [ sp.name for sp in q_tbox.columnSpecs ];
            qdf['status']="";
            for pid in qdf['protocol_id'].unique():

                # build file names
                set_file = os.path.join(
                    values['destination'],
                    str(pid) + "_SETS" + file_ext
                );
                sam_file = os.path.join(
                    values['destination'],
                    str(pid) + "_SAMPLES" + file_ext
                );

                # remove existing file if exists
                if core.isfile(set_file): core.rmfile(set_file);
                if core.isfile(sam_file): core.rmfile(sam_file);

                # initialize data accumulators
                setacc = [];    # set dataframe accumulator
                samacc = [];    # sample dataframe accumulator

                # subset protocol
                ss_pid = qdf[qdf['protocol_id']==pid];
                setlen = 0; # records accumulated so far for reclimit writes
                samlen = 0; # records accumulated so far for reclimit writes
                for lid in ss_pid['labbook_id'].unique():
                    # subset
                    ss_lid = ss_pid[ss_pid['labbook_id']==lid];
                    # get ref to protocol object
                    protocol = lp_objects['pro'][
                        (lp_objects['labbook_id']==lid)&
                        (lp_objects['protocol_id']==pid)
                    ].iloc[0];
                    # connect to database
                    protocol.connect();
                    for eid in ss_lid['experiment_id'].unique():
                        lbp = '.'.join([pid,lid,eid]);
                        progress.var.set(lbp);
                        # subset records for this eid
                        ss_eid = ss_lid[ss_lid['experiment_id']==eid];
                        # initialize where structure
                        wheres = pd.DataFrame(columns=[
                            'experiment_id',
                            'set_id'
                        ]);
                        # parse * or individual sets
                        unique_sids = ss_eid['set_id'].unique();
                        if '*' in unique_sids:
                            wheres = pd.DataFrame([[eid]],
                                columns=['experiment_id']);
                        else:
                            wheres = pd.DataFrame(
                                columns=['experiment_id','set_id']);
                            wheres['set_id']=unique_sids;
                            wheres['experiment_id']=eid;
                        # select sets and samples
                        lsets = protocol.selectSetsWhere(wheres);
                        lsams = protocol.selectSamsWhere(wheres);
                        # record for reclimit
                        setlen += len(lsets);
                        samlen += len(lsams);
                        # add to accumulators
                        setacc.append(lsets);
                        samacc.append(lsams);
                        # update progress bar
                        progress.var.set('.'.join([lid, pid, eid]));
                        done_lpeids+=1;
                        progress.obj['value'] = \
                            int((done_lpeids/total_lpeids)*100);
                        # test record limit write reclimit write
                        if setlen>=reclimit:
                            try:
                                progress.var.set("Writing...");
                                writeto(set_file, pd.concat( setacc ), values['format']);
                                setacc = []; # clear
                                setlen=0;
                                s.logger.info("Appending to "+set_file+".");
                            except Exception as e:
                                # drop pbar and update queue status
                                progress.release();
                                qdf.loc[ss_eid.index,'status']='ERR';
                                for i,r in ss_eid[q_tbox_cols].iterrows():
                                    q_tbox.obj.item(i,
                                        values=qdf.loc[i,q_tbox_cols].tolist());
                                # error popup
                                messagebox.showerror("Error",
                                    "Couldn't write to "+
                                    set_file+": "+str(e));
                                return False;
                        if samlen>=reclimit:
                            try:
                                progress.var.set("Writing...");
                                writeto(sam_file, pd.concat( samacc ), values['format']);
                                samacc = []; # clear out
                                samlen=0;
                                s.logger.info("Appending to "+sam_file+".");
                            except Exception as e:
                                # drop pbar and update queue status
                                progress.release();
                                qdf.loc[ss_eid.index,'status']='ERR';
                                for i,r in ss_eid[q_tbox_cols].iterrows():
                                    q_tbox.obj.item(i,
                                        values=qdf.loc[i,q_tbox_cols].tolist());
                                # error popup
                                messagebox.showerror("Error",
                                    "Couldn't write to "+
                                    sam_file+": "+str(e));
                                progress.release();
                                return False;
                        # update status
                        qdf.loc[ss_eid.index,'status'] = 'OK';
                        for i,r in ss_eid[q_tbox_cols].iterrows():
                            q_tbox.obj.item(i,
                                values=qdf.loc[i,q_tbox_cols].tolist());
                    # end of experiment id ------------
                # end of labbook id -------------------
                # before we go to next protocol, save
                if len(setacc)>0:
                    try:
                        progress.var.set("Writing...");
                        writeto(set_file, pd.concat( setacc ), values['format']);
                        setacc = []; # clear out
                        s.logger.info("Appending to "+set_file+".");
                    except Exception as e:
                        progress.release();
                        messagebox.showerror("Error","Couldn't write to "+
                            set_file+": "+str(e));
                        return False;
                if len(samacc)>0:
                    try:
                        progress.var.set("Writing...");
                        writeto(sam_file, pd.concat( samacc ), values['format']);
                        samacc = []; # clear out
                        s.logger.info("Appending to "+sam_file+".");
                    except Exception as e:
                        progress.release();
                        messagebox.showerror("Error","Couldn't write to "+
                            sam_file+": "+str(e));
                        return False;
            # end of protocol id ----------------------
            progress.release();
        ########################################################################
        threading.Thread(target=_doexport).start();
        return;

################################################################################
################################################################################
################################################################################
################################################################################
#sys.exit();

# import pyLabbook.labbooks.AldrovandiLab;
# import pyLabbook.protocols.TOAD96W;
# lb = pyLabbook.labbooks.AldrovandiLab.initialize(plbRoot);
# pr = pyLabbook.protocols.TOAD96W.initialize(lb);
# pr.connect();
# print(
#     pr.countExperimentsSets(pd.Series(['20180611','20180618']))
# );
# pr.disconnect();

# src = pd.DataFrame([['a'],['b'],['c'],['d']], columns=['id']);
# dst = pd.DataFrame([['c'],['d']], columns=['id']);
# xfr = src[~src['id'].isin(dst['id'])];
# print(xfr);
# sys.exit();


# import pyLabbook.labbooks.AldrovandiLab;
# import pyLabbook.labbooks.tDestLabbook;
# src_lb = pyLabbook.labbooks.AldrovandiLab.initialize(plbRoot);
# dst_lb = pyLabbook.labbooks.tDestLabbook.initialize(plbRoot);
# import pyLabbook.protocols.TOAD96W;
# src_pr = pyLabbook.protocols.TOAD96W.initialize(src_lb);
# dst_pr = pyLabbook.protocols.TOAD96W.initialize(dst_lb);
# src_pr.connect();
# dst_pr.connect();
# wheres = pd.DataFrame([['20190506']], columns=['experiment_id']);
# sets = src_pr.selectSetsWhere(wheres);
# sams = src_pr.selectSamsWhere(wheres);
# #dst_pr.storeSets(sets, method='replace');
# #dst_pr.storeSams(sams, method='replace');
# sys.exit();

# import pyLabbook.labbooks.AldrovandiLab;
# lb = pyLabbook.labbooks.AldrovandiLab.initialize(plbRoot);
# import pyLabbook.protocols.TOAD96W;
# pr = pyLabbook.protocols.TOAD96W.initialize(lb);
# pr.connect();
# print(pr.setTableExists());
# sys.exit();


# wheres = pd.DataFrame(columns=['andor','field','op','value']);
# def addwheres(wheres, andor=None, field=None, op=None, value=None, sv=False):
#     r = pd.Series();
#     r['andor'] = andor;
#     if field==None: raise Exception("no field specified");
#     else: r['field']=str(field);
#     if op==None: raise Exception("no operation specified");
#     else: r['op']=str(op);
#     if value==None: raise Exception("no value specified");
#     else: r['value']=value;
#     return wheres.append(r, ignore_index=True).reset_index(drop=True);
# import pyLabbook.labbooks.AldrovandiLab;
# import pyLabbook.protocols.TOAD96W;
# lb = pyLabbook.labbooks.AldrovandiLab.initialize(plbRoot);
# pr = pyLabbook.protocols.TOAD96W.initialize(lb);
# pr.connect();
# wheres = addwheres(wheres, andor=None, field='experiment_id', op='=', value='20190506');
# wheres = addwheres(wheres, andor='and', field='sample_id', op='=', value='INFTY');
# result = pr.selectSamsFullWhere(wheres);
# print(result);
# pr.disconnect();
# sys.exit();

# z = pd.Series({'a':1,'b':2});
# print(z[['a','b']]);
# sys.exit();

# import pyLabbook.labbooks.AldrovandiLab;
# import pyLabbook.protocols.Reagents2;
# lb = pyLabbook.labbooks.AldrovandiLab.initialize(plbRoot);
# pr = pyLabbook.protocols.Reagents2.initialize(lb);
#
# print(pr._SETDESC);
# pr.connect();
# pr.testme();
# sys.exit();

#
# qdf = pd.DataFrame([
#     ['l1','p1','e1','s1',''],
#     ['l1','p2','e1','s1',''],
#     ['l2','p2','e1','s1',''],
# ], columns=['labbook_id','protocol_id','experiment_id','set_id','status']);
#
# def mpbuilder(qdf):
#     # simplify
#     objs = qdf[['labbook_id','protocol_id']].copy().drop_duplicates();
#     # build/initialize rest of structure
#     # labbook~protocol combo for uniqueness
#     objs['lp'] = objs['labbook_id']+'~'+objs['protocol_id'];
#     # labbook and protocol import namespaces
#     objs['lmp'] = 'pyLabbook'+'.'+'labbooks'+'.'+objs['labbook_id'];
#     objs['pmp'] = 'pyLabbook'+'.'+'protocols'+'.'+objs['protocol_id'];
#     # actual initialized objects
#     objs['lbo'] = None; # labbook objects
#     objs['pro'] = None; # protocol objects initialized with rsp. labbook
#
#     # import labbooks
#     for lmp in objs['lmp'].unique():
#         z = 1;
#     # import protocols
#     for pmpd in objs['pmp'].unique():
#         z = 1;
#     # initialize labbooks
#     for lid in objs['labbook_id'].unique():
#         ss = objs[objs['labbook_id']==lid];
#         lobj = 1; #initialize with plbRoot
#         objs.loc[ss.index,'lbo'] = lobj; # store
#     # initialize protocols
#     for i,r in objs.iterrows():
#         pobj = 1; # initialize protocol using r['lbo']
#         objs.loc[i,'pro'] = pobj;
#
#
#     print(objs);
#
#
#
# mpbuilder(qdf);
#
#
# sys.exit();
app = pyLabbookManagerApp();
