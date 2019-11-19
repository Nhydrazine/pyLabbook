import os, sys, importlib, re;
import numpy as np, pandas as pd;
import threading;
import time;
import tkinter as tk;
from tkinter import messagebox;
from tkinter import filedialog;
from tkinter import scrolledtext;
from tkinter import ttk;
import logging;
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
################################################################################
SQLEngine = engine.SQLEngine();
dummy_labbook = pyLabbook(
    id="dummy",
    root=plbRoot,
    repositoryPath=plbRoot,
    sheetFormat='xlsx',
    databasePath=plbRoot,
    databaseFile="temp.sqlite3",
    databaseFormat='SQLITE3',
);
################################################################################
def wpos(p):
    px = p.winfo_x();
    py = p.winfo_y();

################################################################################
class empty(object):
    def __init__(s): return;
################################################################################
class dhandle(object):
    def __init__(s): return;
################################################################################
class spec(object):
    def __init__(s,
        name                = None,     # name of object
        label               = None,     # label where applicable
        type                = str,      # data type if applicable
        default             = None,     # default value if applicable
        style               = { },      # style
        size                = 10,       # item size where applicable
        width               = None,     # pixel width where applicable
        height              = None,     # pixel height if applicable
        anchor              = None,# anchor option if applicable
        options             = [ ],      # value options if applicable
        widgetClass         = None,     # widget class type
        createKWA           = { },      # keyword args for creating object
        packKWA             = { },      # keyword args for packing object
        packOp              = 'pack',   # pack type 'grid' or 'pack'
        displayFormatter    = lambda x: x,# for display
        validator           = lambda x: True,   #
        variable            = None,
        frameStyle          = None,
    ):
        s.name              = name;         # name of object
        s.label             = label;        # label where applicable
        s.type              = type;         # data type if applicable
        s.default           = default;      # default value if applicable
        s.style             = style;        # style
        s.size              = size;
        s.width             = width;
        s.anchor            = anchor;       # anchor if applicable
        s.options           = options;      # value options if applicable
        s.widgetClass       = widgetClass;  # widget class type
        s.createKWA         = createKWA;    # keyword args for creating object
        s.packKWA           = packKWA;      # keyword args for packing object
        s.packOp            = packOp;       # pack type 'grid' or 'pack'
        s.displayFormatter  = displayFormatter;
        s.validator         = validator;
        s.variable          = variable;
        s.frameStyle        = frameStyle;
    def re(s, **kwargs):
        for k in kwargs.keys(): setattr(s,k,kwargs[k]);
        return s;
    def copy(s):
        return spec(
        name            = s.name,
        label           = s.label,
        type            = s.type,
        default         = s.default,
        style           = dict(s.style),
        size            = s.size,
        width           = s.width,
        anchor          = s.anchor,
        options         = list(s.options),
        widgetClass     = s.widgetClass,
        createKWA       = dict(s.createKWA),
        packKWA         = dict(s.packKWA),
        packOp          = s.packOp,
        displayFormatter= s.displayFormatter,
        validator       = s.validator,
        variable        = s.variable,
        frameStyle      = s.frameStyle,
        );
    def series(s):
        r = pd.Series({
            'label'             : s.label,
            'type'              : s.type,
            'default'           : s.default,
            'style'             : s.style,
            'size'              : s.size,
            'width'             : s.width,
            'anchor'            : s.anchor,
            'options'           : s.options,
            'widgetClass'       : s.widgetClass,
            'createKWA'         : s.createKWA,
            'packKWA'           : s.packKWA,
            'packOp'            : s.packOp,
            'displatyFormatter' : s.displayFormatter,
            'validator'         : s.validator,
            'variable'          : s.variable,
            'frameStyle'        : s.frameStyle,
        });
        r.name = s.name;
        return r;
################################################################################
class widget(ttk.Frame):
    def __init__(s, parent, spec, build=True):
        ttk.Frame.__init__(s, parent);
        s.parent = parent;
        s.var = tk.StringVar();
        s.spec = spec;          # specification
        s.obj = None;           # object
        if build:
            s.build();
            s.opack();
    def build(s):
        if s.spec.widgetClass==tk.Label:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = tk.Label(
                s,
                textvariable=s.var,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==ttk.Label:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = ttk.Label(
                s,
                textvariable=s.var,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==tk.Entry:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = tk.Entry(
                s,
                textvariable=s.var,
                **s.spec.createKWA
            );
        elif s.spec.widgetClass==ttk.Entry:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = ttk.Entry(
                s,
                textvariable=s.var,
                **s.spec.createKWA
            );
        elif s.spec.widgetClass==tk.Button:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.label));
            else: s.var = s.spec.variable;
            s.obj = tk.Button(
                s,
                textvariable=s.var,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==ttk.Button:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.label));
            else: s.var = s.spec.variable;
            s.obj = ttk.Button(
                s,
                textvariable=s.var,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==tk.Checkbutton:
            if s.spec.variable==None:
                s.var = tk.BooleanVar(value=bool(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = tk.Checkbutton(
                s,
                variable=s.var,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==ttk.Checkbutton:
            if s.spec.variable==None:
                s.var = tk.BooleanVar(value=bool(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = ttk.Checkbutton(
                s,
                variable=s.var,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==ttk.Combobox:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = ttk.Combobox(
                s,
                values=s.spec.options,
                textvariable=s.var,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==tk.OptionMenu:
            if s.spec.variable==None:
                s.var = tk.StringVar(value=str(s.spec.default));
            else: s.var = s.spec.variable;
            s.obj = tk.OptionMenu(
                s,
                s.var,
                *s.spec.options,
                **s.spec.createKWA,
            );
        elif s.spec.widgetClass==tk.Frame:
            s.obj = tk.Frame(s, **s.spec.createKWA);
        elif s.spec.widgetClass==ttk.Frame:
            s.obj = ttk.Frame(s, **s.spec.createKWA);
        elif s.spec.widgetClass==ttk.Separator:
            s.obj = ttk.Separator(s, **s.spec.createKWA)
        elif s.spec.widgetClass==scrolledtext.ScrolledText:
            s.obj = scrolledtext.ScrolledText(s, **s.spec.createKWA);
        elif s.spec.widgetClass==ttk.Progressbar:
            s.obj = ttk.Progressbar(s, **s.spec.createKWA);
        else:
            raise Exception(str(s.spec.widgetClass) + " is not supported");
        s.obj.configure( **s.spec.style );
    def opack(s):
        if s.spec.packOp=='grid':
            s.obj.grid(row=0, column=0, **s.spec.packKWA);
        elif s.spec.packOp=='pack':
            s.obj.pack(**s.spec.packKWA);
        else: raise Exception(str(s.spec.packOp) + " is not supported");
################################################################################
class widgetGrid(ttk.Frame):
    def __init__(s, parent, spec):
        ttk.Frame.__init__(s, parent);
        s.spec = spec;
        # indexed by widget.spec.name
        s.widgets = pd.DataFrame(
            columns=['x','y','widget','packKWA']);
        # packKWA is for the grid packing of the widget into this grid
        # includes options like columnspan and rowspan
        # but does NOT include row and column!
    def make(s, x, y, spec, packKWA={}):
        # make a widget from a spec
        if len(s.widgets[(s.widgets['x']==x)&(s.widgets['y']==y)])>0:
            raise Exception("(" + str(x) + "," + str(y) + ") is occupied");
        if spec.name in s.widgets.index:
            raise Exception(str(spec.name) + " already exists");
        s.widgets = s.widgets.append(
            s._widgetrow(x, y, widget(s, spec, build=True), packKWA));

    def add(s, x, y, awidget, packKWA={}):
        s.widgets = s.widgets.append(s._widgetrow(x, y, awidget, packKWA));

    def _widgetrow(s, x, y, awidget, packKWA={}):
        row = pd.Series({
            'x': x,
            'y': y,
            'widget': awidget,
            'packKWA': packKWA,
        });
        row.name = awidget.spec.name;
        return row;

    def packWidgets(s):
        for i,r in s.widgets.iterrows():
            r['widget'].grid(
                row=r['y'],
                column=r['x'],
#                sticky='nesw'
                **r['packKWA'],
            );
        for col in s.widgets['x'].unique():
            s.columnconfigure(int(col), weight=1);
        for row in s.widgets['y'].unique():
            s.rowconfigure(int(row), weight=1);
    def widget(s,name):
        return s.widgets['widget'].loc[name];
################################################################################
class treeBox(ttk.Frame):
    def __init__(s, master, spec, columnspecs=[], xscroll=True, yscroll=True):
        ttk.Frame.__init__(s, master);
        # initialize
        s.iix = 1;      # current incrementing index
        # store arguments
        s.spec = spec;
        s.columnSpecs = \
            pd.Series(columnspecs, index=[c.name for c in columnspecs]);
        s.var = pd.DataFrame(columns=s.columnSpecs.index.tolist());
        # build Treeview

        s.obj = ttk.Treeview(
            s,
            column=s.columnSpecs.index.tolist(),
            show='headings',
            **s.spec.createKWA,
        );
        # scrollbars
        if yscroll:
            s.ybar = ttk.Scrollbar(s, orient='vertical',command=s.obj.yview);
            s.obj.configure(yscrollcommand=s.ybar.set);
        if xscroll:
            s.xbar = ttk.Scrollbar(s, orient='horizontal', command=s.obj.xview);
            s.obj.configure(xscrollcommand=s.xbar.set);

        # build column headings
        for i,r in s.columnSpecs.iteritems():
            cargs = {'stretch': tk.NO};
            if r.width: cargs['width'] = r.width;
            hargs = {'text': r.label};
            if r.anchor: hargs['anchor'] = r.anchor;
            s.obj.column(i, **cargs);
            s.obj.heading(
                i,
                command=lambda _col=i: s.sort_column(_col, False),
                **hargs);
        # configure
        s.obj.configure(spec.style);
        # pack
        if s.spec.packOp=='grid':
            s.obj.grid(row=0, column=0, **s.spec.packKWA);
            if yscroll: s.ybar.grid(row=0, column=1, sticky='ns');
            if xscroll: s.xbar.grid(row=1, column=0, sticky='ew');
        elif s.spec.packOp=='pack':
            if xscroll: s.xbar.pack(side=tk.BOTTOM,fill='x');
            s.obj.pack(side=tk.LEFT,**s.spec.packKWA);
            if yscroll: s.ybar.pack(side=tk.RIGHT,fill='y');

        else: raise Exception(str(s.spec.packOp) + " is not supported");

    def sort_column(s, col, reverse):
        pos = 0;
        for i,r in s.var.sort_values(by=col, ascending=reverse).iterrows():
            s.obj.move(i, '', pos);
            pos+=1;
        if reverse==True:
            s.obj.heading(col, command=lambda _col=col: s.sort_column(_col, False));
        else:
            s.obj.heading(col, command=lambda _col=col: s.sort_column(_col, True));
    def _prepareRowForDisplay(s, r):
        dr = [];
        for i,sp in s.columnSpecs.iteritems():
            dv = sp.displayFormatter(r[i]);
            dr.append(dv);
        return dr;

    def selected(s): return s.obj.focus();

    def row(s,name): return s.var.loc[name,:];

    def rows(s,names): return s.var.loc[names,:];

    def append(s,r):
        # convert r to properly formatted & typed pd.Series
        row = pd.Series();
        for i,sp in s.columnSpecs.iteritems(): row[i] = sp.type( r[i] );
        # name/iid
        row.name = "_" + str(int(s.iix));
        s.iix+=1;
        # add to dataframe
        s.var = s.var.append(row);
        # insert to tree
        s.obj.insert(
            '', 'end', iid=row.name, values=s._prepareRowForDisplay(row));
        s.lastSelected = '';

    def sortby(s,k):
        ix = s.var.sort_values(by=k).index;
        return;

    def loadDataFrame(s,df, overwrite=True):
        df = df.copy();
        ndf = pd.DataFrame(columns=s.columnSpecs.index.tolist());
        if overwrite: s.var = pd.DataFrame(
            columns=s.columnSpecs.index.tolist());
        newrows = [];
        cols = [ c.name for i,c in s.columnSpecs.iteritems() ];
        for ri,r in df.iterrows():
            newvals = [];
            for i,sp in s.columnSpecs.iteritems():
                v = r[i];
                if v==None: newvals.append('');
                else: newvals.append(sp.type(r[i]));

            # for v in r.iteritems:
            #     if v==None: newvals.append('');
            #     else: newvals.append(
            # r = pd.Series(
            #     [ sp.type(r[i]) for i,sp in s.columnSpecs.iteritems() ],
            #     index=cols
            # );
            r = pd.Series( newvals, index=cols );
            r.name = "_" + str(int(s.iix));
            s.iix+=1;
            newrows.append(r);
        s.var = pd.concat( [s.var, pd.DataFrame(newrows)] );
#        s.clearItems();
        s.synch();

    def appendDataFrame(s, df):
        cols = [ c.name for i,c in s.columnSpecs.iteritems() ];
        ndf = [];
        for i,r in df.iterrows():
            nr = r.copy();
            nr.name = "_" + str(int(s.iix));
            s.iix+=1;
            ndf.append(nr);
        s.var = pd.concat(
            [s.var[cols], pd.DataFrame(ndf)],
            sort=False ).drop_duplicates();
        s.clearItems();
        s.synch();

    def moveUp(s,name): s.obj.move(name, '', s.obj.index( s.obj.prev(name) ));

    def moveDown(s,name): s.obj.move(name, '', s.obj.index( s.obj.next(name) ));

    def move(s,loc,name): s.obj.move(name, '', loc);

    def delete(s,name):
        s.obj.delete( name );
        s.var = s.var.drop(labels=name, axis=0);

    def synch(s):
        # remove tree rows that aren't in the data
        dataix = s.var.index.tolist();
        treeix = list(s.obj.get_children());
        all = pd.DataFrame(
            columns=['df','tv'],
            index=pd.Series(dataix + treeix).unique());
        all.loc[dataix,'df'] = 1;
        all.loc[treeix,'tv'] = 1;
        lix = 0; # local index for ordering
        for i,r in all.iterrows():
            # update, don't move it though, visual order is left up to the tree
            # and is not maintained or curated in the dataframe
            if r['df']==1 and r['tv']==1:
#                s.updateItem(i);
                s.obj.item(
                    i,
                    values=s._prepareRowForDisplay( s.var.loc[i,:] )
                );
            # delete if tree only
            elif r['df']!=1 and r['tv']==1:
                s.obj.delete(i);
            # insert at current lix if not in tree
            elif r['df']==1 and r['tv']!=1:
                iid = i;
                s.obj.insert('',lix,iid=iid,
                    values=s._prepareRowForDisplay( s.var.loc[iid,:] ));
            lix+=1;
#        if s.lastSelected!='':
#            s.obj.selection_set(s.lastSelected);
#            s.obj.focus(s.lastSelected);
    def clearItems(s):
#       # this would work if you used a name as the index instead of a number
#        s.lastSelected = s.selected();
        for c in s.obj.get_children():
            s.obj.delete(c);

    def clearAll(s):
        s.loadDataFrame(pd.DataFrame(columns=[c.name for c in s.columnSpecs]));
        s.clearItems();

    def updateItem(s,name):
        s.obj.item(name, values=s._prepareRowForDisplay( s.var.loc[name,:] ) );
################################################################################
class labbookPane(ttk.Frame):

    def __init__(s, master, aspec, columnspecs=[
        spec(name='id', label='ID')
    ], root=None, glob={}):
        ttk.Frame.__init__(s, master);
        s.glob = glob;
        s.root = root;
        s.spec = aspec;
        s.columnspecs = columnspecs;
        s.wgrid = widgetGrid(s, spec(name='wgrid'));
        s.make_specs();
        s.build();
    #--------------------------------------------------------------------------#
    # DEFINE AND BUILD WIDGETS
    #--------------------------------------------------------------------------#
    def make_specs(s):
        s.specs = {};
        bsty = {'width':3};
        s.specs['b.create'] = spec( name='b.create', label='\u271A',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.delete'] = spec( name='b.delete', label='\u2716',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.inspect'] = spec( name='b.inspect', label='\u2609',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.refresh'] = spec( name='b.refresh', label='\u2941',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.exportdb'] = spec( name='b.exportdb', label='\u21F2',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.test'] = spec( name='b.test', label='T',
            style=bsty, widgetClass=ttk.Button);

        s.specs['p.msg.unavailable'] = spec(name='p.msg.unavailable',
            style={'font': 'arial 14 bold'},
            default="Sorry, that functionality isn't avilable yet.",
            widgetClass=ttk.Label);
        s.specs['treebox'] = spec(name='treebox',
            createKWA={'height': 16, 'selectmode': 'browse'});
        s.specs['p.msg.error'] = spec(name='p.msg.error',
            style={'font': 'arial 12 bold', 'fg': '#aa7777'});
    #--------------------------------------------------------------------------#
    def build(s):
        # label
        s.wgrid.make( 0, 0, spec(
            name='header',
            default='Labbooks',
            widgetClass=ttk.Label,
            createKWA={'style':'PaneHeader.TLabel'},
            packKWA={'padx': 5, 'pady': 5}
        ), packKWA={'sticky':'w'});
        # treebox
        s.columnspecs = [
            spec(name='id', label='labbook_id')];
        s.wgrid.add( 0, 1, treeBox(s.wgrid, s.specs['treebox'],
            columnspecs=s.columnspecs, xscroll=False), packKWA={});
        # buttons
        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));  # button grid
        s.wgrid.add( 0, 2, s.bgrid, packKWA={} );   # add button grid to wgrid
        s.bgrid.make(0, 0, s.specs['b.create'], packKWA={} );
        s.bgrid.make(1, 0, s.specs['b.delete'], packKWA={} );
        # s.bgrid.make(2, 0, s.specs['b.inspect'], packKWA={} );
        s.bgrid.make(3, 0, s.specs['b.refresh'], packKWA={} );
        s.bgrid.make(4, 0, s.specs['b.exportdb'], packKWA={} );
        # s.bgrid.make(5, 0, s.specs['b.test'], packKWA={} );
        # pack
        s.bgrid.packWidgets(); # pack widgets inside of bgrid
        s.wgrid.packWidgets(); # pack object in outermost grid, including bgrid
        s.wgrid.pack();
        # bind
        s.bgrid.widget('b.create').obj.bind('<Button-1>',  s._ba_create);
        s.bgrid.widget('b.delete').obj.bind('<Button-1>', s._ba_delete);
        # s.bgrid.widget('b.inspect').obj.bind('<Button-1>', s._ba_inspect);
        s.bgrid.widget('b.refresh').obj.bind('<Button-1>', s._ba_refresh);
        s.wgrid.widget('treebox').obj.bind('<Double-1>', s._ba_inspect);
        s.bgrid.widget('b.exportdb').obj.bind('<Button-1>', s._ba_exportdb);
        # s.bgrid.widget('b.test').obj.bind('<Button-1>', s._ba_test);

    #--------------------------------------------------------------------------#
    def _selectedItemID(s):
        sel = s.wgrid.widget('treebox').selected();
        if sel=='': return None;
        return s.wgrid.widget('treebox').row(sel)['id'];
    #--------------------------------------------------------------------------#
    # BUTTON ACTIONS
    #--------------------------------------------------------------------------#
    #--------------------------------------------------------------------------#
    def _ba_exportdb(s, e):
        s.root.exportDataBase( s._selectedItemID() );
        return;
    #--------------------------------------------------------------------------#
    def _ba_create(s, e):
        lbw = labbookMaker(s.root, spec(name='lbw')).grab();
        s._refreshList();
    #--------------------------------------------------------------------------#
    def _ba_delete(s, e):
        # get
        labbook_id = s._selectedItemID();
        if labbook_id==None or labbook_id=='':
            s._errorWindow("No labbook has been selected");
            return;
        if s.root.deleteLabbook(labbook_id):
            s.root.focus_force();
    #--------------------------------------------------------------------------#
    def _ba_inspect(s, e):
        labbook_id = s._selectedItemID();
        if labbook_id==None:
            s._errorWindow("No labbook is selected");
            return;
        # try to import and activate labbook
        try: labbook_object = s._importLabbook(labbook_id);
        except Exception as e:
            s._errorWindow(str(e));
            return;
        if labbook_object==None: return;
        lbw = labbookInspector(s.root, labbook_object);
    #--------------------------------------------------------------------------#
    def _ba_refresh(s, e):
        s.root.updateLabbookList();
    #--------------------------------------------------------------------------#
    def _ba_export(s, e):
        pw = popup(s.root, mspec=s.specs['p.msg.unavailable']).grab();
    #--------------------------------------------------------------------------#
    def _ba_import(s, e):
        pw = popup(s.root, mspec=s.specs['p.msg.unavailable']).grab();
    #--------------------------------------------------------------------------#
    def _refreshList(s):
        # this is now handled by s.root
        return;
    #--------------------------------------------------------------------------#
    def _importLabbook(s,labbook_id):
        full = '.'.join(['pyLabbook','labbooks', labbook_id]);
        # check modules
        if full not in sys.modules:
            # import
            try: module = importlib.import_module(full);
            except Exception as e:
                raise Exception("Can't import " + full + ": " + str(e));
        # try to load
        try: labbook_object = sys.modules[full].initialize(plbRoot);
        except Exception as e:
            raise Exception("Can't initialize " + full + ": " + str(e));
        return labbook_object;
################################################################################
class labbookInspector(tk.Toplevel):
    def __init__(s, root, labbook_object):
        tk.Toplevel.__init__(s);
        s.resizable(width=False, height=False);
        s.root = root;
        s.labbook = labbook_object;
        s._mastercontainer = ttk.Frame(s);
        s._mastercontainer.pack(fill='both', expand=True);
        s.container = ttk.Frame(s);
        s.container.pack();
        s.specs = { };
        s.styles = { };
        s.wgrid = widgetGrid(s.container, spec(name='widget'));
        s.attkeys = ['id','repositoryPath','sheetFormat','databasePath',
            'databaseFile','databaseFormat'];

        s.make_styles();
        s.make_specs();
        s.build();

    def make_styles(s):
        s.styles['header'] = {
            'font': 'arial 14 bold underline' };
        s.styles['label'] = { 'font': 'arial 14 bold' };
        s.styles['value'] = { 'font': 'arial 14 italic' };

    def make_specs(s):
        s.specs['header'] = spec(name='header', default='Labbook Inspector',
            widgetClass=ttk.Label, style=s.styles['header']);
        s.specs['button'] = spec(name='button', label='OK',
            widgetClass=ttk.Button, style={});

        for k in s.attkeys:
            lkey = 'l.' + str(k);
            vkey = 'v.' + str(k);
            s.specs[lkey] = spec(name=lkey,
                widgetClass=ttk.Label, default=str(k),
                createKWA={'style':'Field.TLabel'},
                packKWA={'anchor':'e'});
            s.specs[vkey] = spec(name=vkey, style=s.styles['value'],
                widgetClass=ttk.Label, default=getattr(s.labbook, k),
                packKWA={'anchor':'w'});

    def build(s):
        s.wgrid.make(0, 0, s.specs['header'], packKWA={});
        s.igrid = widgetGrid(s.wgrid, spec(name='infogrid'));
        for i,k in enumerate(s.attkeys):
            lkey = 'l.' + str(k);
            vkey = 'v.' + str(k);
            s.igrid.make(0, i, s.specs[lkey], packKWA={'sticky': 'nesw'});
            s.igrid.make(1, i, s.specs[vkey], packKWA={'sticky': 'nesw'});

        s.wgrid.add(0, 1, s.igrid, packKWA={});
        s.wgrid.make(0, 2, s.specs['button'], packKWA={});

        s.igrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack(padx=20, pady=20);

        s.wgrid.widget('button').obj.bind('<Button-1>', s.ba_pressed);

    def ba_pressed(s, e):
        s.destroy();
        s.root.focus_force();
        return;
################################################################################
class labbookMaker(tk.Toplevel):
    def __init__(s, root, aspec, importdb=False):
        tk.Toplevel.__init__(s);
        s.resizable(width=False, height=False);
        s.root = root;
        s.importdb = importdb;
        s._mastercontainer = ttk.Frame(s);
        s._mastercontainer.pack(fill='both', expand=True);
        s._container = ttk.Frame(s);
        s._container.pack();
        s.wgrid = widgetGrid(s._container,spec(name='grid'));
        s.spec = aspec;
        s.specs = { };
        s.styles = { };
        s.attkeys = ['id','repositoryPath','sheetFormat','databasePath',
            'databaseFile','databaseFormat'];
        s.make_styles();
        s.make_specs();
        s.build();

    def grab(s):
        s.transient(s.root);
        s.grab_set();
        s.root.wait_window(s);

    def release(s):
        s.root.focus_force();
        s.destroy();
        return;

    def make_styles(s):
        s.styles['header'] = { 'font': 'arial 14 bold underline' };
        s.styles['status'] = { 'font': 'arial 10'};
        s.styles['hspacer'] = {'height': 30};
        s.styles['label'] = { 'font': 'arial 14 bold' };
        s.styles['entry'] = { 'font': 'arial 13' };
        s.styles['option'] = { };

    def make_specs(s):
        s.specs['header'] = spec(name='header', default='New Labbook',
            widgetClass=ttk.Label, style=s.styles['header']);

        s.specs['status'] = spec(name='status', default="",
            widgetClass=ttk.Label, style=s.styles['status'],
            packKWA={'anchor': 'w'}
        );
        s.specs['_'] = spec(name='spacer', widgetClass=ttk.Frame);
        # entry fields
        s.specs['l.id'] = spec(name='l.id', default='id',
            widgetClass=ttk.Label,
            createKWA={'style':'Field.TLabel'},
            packKWA={'anchor': 'e'});
        s.specs['f.id'] = spec(name='f.id', default='NewLabbook',
            widgetClass=ttk.Entry, style=s.styles['entry'],
            packKWA={'anchor': 'nw'});
        s.specs['l.sheetFormat'] = spec(name='l.sheetFormat',
            default='Sheet Format',
            widgetClass=ttk.Label,
            createKWA={'style':'Field.TLabel'},
            packKWA={'anchor': 'e'});
        s.specs['f.sheetFormat'] = spec(name='f.sheetFormat',
            options=['xlsx','csv'],
            default='xlsx',
            widgetClass=ttk.Combobox,
            createKWA={'state': 'readonly'},
            style=s.styles['option'],
            packKWA={'anchor': 'nw'});
        s.specs['l.dbFormat'] = spec(name='l.dbFormat',
            default='Database Format',
            widgetClass=ttk.Label,
            createKWA={'style':'Field.TLabel'},
            packKWA={'anchor': 'e'});
        s.specs['f.dbFormat'] = spec(name='f.dbFormat',
            options=['SQLITE3'],
            default='SQLITE3',
            widgetClass=ttk.Combobox,
            createKWA={'state': 'readonly'},
            style=s.styles['option'],
            packKWA={'anchor': 'nw'});
        s.specs['l.dbFile'] = spec(name='l.dbFile',
            default='Database File',
            widgetClass=ttk.Label,
            createKWA={'style':'Field.TLabel'},
            packKWA={'anchor':'e'});
        s.specs['f.dbFile'] = spec(name='f.dbFile',
            default='',
            widgetClass=ttk.Entry,
            createKWA={},
            packKWA={'anchor':'nw'});
        s.specs['b.dbFile'] = spec(name='b.dbFile',
            label="Choose",
            widgetClass=ttk.Button,
            createKWA={},
            packKWA={});

        s.specs['b.ok'] = spec(name='b.ok', label="OK",
            widgetClass=ttk.Button, packKWA={'padx': 5});
        s.specs['b.cancel'] = spec(name='b.cancel', label="Cancel",
            widgetClass=ttk.Button, packKWA={'padx': 5});

    def build(s):
        # info grid
        s.igrid = widgetGrid(s.wgrid, spec=spec(name='igrid'));
        # button grid to go in container grid
        s.bgrid = widgetGrid(s.wgrid, spec=spec(name='bgrid', packKWA={'sticky': 'nesw'}));
        # make
        s.wgrid.make(0, 0, s.specs['header'], packKWA={'sticky': 'nesw'});
        s.wgrid.make(0, 1, s.specs['_'].copy().re(name='s1',height=80));

        s.wgrid.add(0, 2, s.igrid, packKWA={'sticky': 'nesw'});
        s.wgrid.make(0, 3, s.specs['_'].copy().re(name='s2',height=20));

        s.igrid.make(1, 0, s.specs['status'], packKWA={'sticky': 'nesw'});
        s.igrid.make(0, 1, s.specs['l.id'], packKWA={'sticky': 'nesw'});
        s.igrid.make(1, 1, s.specs['f.id'], packKWA={'sticky': 'nesw'});
        s.igrid.make(0, 2,s.specs['l.sheetFormat'], packKWA={'sticky': 'nesw'});
        s.igrid.make(1, 2,s.specs['f.sheetFormat'], packKWA={'sticky': 'nesw'});

        s.igrid.make(0, 3,
            s.specs['l.dbFormat'], packKWA={'sticky': 'nesw'});
        s.igrid.make(1, 3,
            s.specs['f.dbFormat'], packKWA={'sticky': 'nesw'});

        s.igrid.make(0, 4,
            s.specs['l.dbFile'], packKWA={'sticky':'nesw'});
        s.dbfgrid = widgetGrid(s.igrid, spec=spec(name='dbfgrid'));
        s.dbfgrid.make(0, 0,
            s.specs['f.dbFile'], packKWA={'sticky':'nesw'});
        s.dbfgrid.make(1, 0,
            s.specs['b.dbFile'], packKWA={'sticky':'ne'});
        s.dbfgrid.packWidgets();
        s.igrid.add( 1, 4, s.dbfgrid, packKWA={'sticky':'nesw'});

        s.wgrid.add(0, 4, s.bgrid, packKWA={'sticky': 'e'});
        s.bgrid.make(0, 0, s.specs['b.cancel'], packKWA={});
        s.bgrid.make(1, 0, s.specs['b.ok'], packKWA={});

        s.bgrid.packWidgets();
        s.igrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack(padx=50, pady=20);

        s.bgrid.widget('b.ok').obj.bind('<Button-1>', s._ba_ok);
        s.bgrid.widget('b.cancel').obj.bind('<Button-1>', s._ba_cancel);
        s.dbfgrid.widget('b.dbFile').obj.bind('<Button-1>', s._ba_dbFile);

    def _ba_dbFile(s, e):
        s.dbfgrid.widget('f.dbFile').var.set(
            filedialog.askopenfilename(
                initialdir=os.path.join(plbRoot,'imports'),
                title="Select Database File",
                filetypes=(
                    ("sqlite","*.sqlite"),
                    ("sqlite3","*.sqlite3"),
                    ("all files","*")
                )
            )
        );

    def _ba_cancel(s, e):
        s.destroy();
        return;

    def _ba_ok(s, e):
        s._validateParameters();
        return;

    def _validateParameters(s):
        rx_anumnz = re.compile(r'^[A-Z,a-z,0-9,\-,\_]+$');
        inputs = {
            'id': s.igrid.widget('f.id').var.get(),
            'sheetFormat': s.igrid.widget('f.sheetFormat').var.get(),
            'databaseFormat': s.igrid.widget('f.dbFormat').var.get(),
            'importDatabaseFile': s.dbfgrid.widget('f.dbFile').var.get(),
        };
        if inputs['id'][0] in (['0','_','-',' ']):
            messagebox.showerror("Error",
                "Labbook ID cannot begin with space, 0, _ or -");
            return False;
        if not rx_anumnz.match(inputs['id']):
            messagebox.showerror("Error",
                "Labbook ID can only contain A-Z, a-z, 0-9, _ or -");
            return False;
        if inputs['id'] in ops.listPyFiles(plbLabbookRoot):
            messagebox.showerror("Error",
                "A labbook named '" + str(inputs['id']) +
                "' already exists.");
            return False;
        if inputs['databaseFormat'] not in ['SQLITE3']:
            messagebox.showerror("Error",
                "'" + str(inputs['databaseFormat']) +
                "' is not a supported database format.");
            return False;
        if inputs['sheetFormat'] not in ['csv','xlsx']:
            messagebox.showerror("Error",
                "'" + str(inputs['sheetFormat']) + "' is not a " +
                "supported spreadsheet format.");
            return False;
        # all good
        s._makeNewLabbook(
            inputs['id'],
            inputs['sheetFormat'],
            inputs['databaseFormat'],
            inputs['importDatabaseFile'],
        );

    def _makeNewLabbook(s, labbook_id, sheetFormat, databaseFormat, importDatabaseFile):
        # instantiate a labbook object and fill in parameters
        try:
            lb = pyLabbook(
        		id=labbook_id,
        		root=plbRoot,
        		repositoryPath=os.path.join('repositories', labbook_id),
        		sheetFormat=sheetFormat,
        		databasePath="databases",
        		databaseFile=labbook_id + '.sqlite3',
        		databaseFormat=databaseFormat,
            );
        except Exception as e:
            messagebox.showerror("Error","Can't initialize " + labbook_id +
                ": " + str(e));
            return;
        # then pass the instance to root to handle the file work
        if s.root.createLabbook(lb, importdb=importDatabaseFile): s.release();
        else: return False;
################################################################################
################################################################################
################################################################################
class protocolPane(ttk.Frame):
    #--------------------------------------------------------------------------#
    def __init__(s, master, aspec, columnspecs=[
        spec(name='id', label='ID')
    ], root=None, glob={}):
        ttk.Frame.__init__(s, master);
        s.glob = glob;
        s.root = root;
        s.spec = aspec;
        s.columnspecs = columnspecs;
        s.wgrid = widgetGrid(s, spec(name='wgrid'));
        s.make_specs();
        s.build();
    #--------------------------------------------------------------------------#
    # DEFINE AND BUILD WIDGETS
    #--------------------------------------------------------------------------#
    def make_specs(s):
        s.specs = {};
        bsty = {'width':3};
        s.specs['b.create'] = spec( name='b.create', label='\u271A',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.delete'] = spec( name='b.delete', label='\u2716',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.inspect'] = spec( name='b.inspect', label='\u2609',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.refresh'] = spec( name='b.refresh', label='\u2941',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.import'] = spec( name='b.import', label='\u21F1',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.export'] = spec( name='b.export', label='\u21F2',
            style=bsty, widgetClass=ttk.Button);
        # s.specs['b.queue'] = spec(name='b.queue', label='Q',
        #     style=bsty, widgetClass=ttk.Button);
        s.specs['p.msg.unavailable'] = spec(name='p.msg.unavailable',
            style={'font': 'arial 14 bold'},
            default="Sorry, that functionality isn't avilable yet.",
            widgetClass=ttk.Label);
        s.specs['treebox'] = spec(name='treebox',
            createKWA={'height': 16, 'selectmode':'browse'});
        s.specs['p.msg.error'] = spec(name='p.msg.error',
            style={'font': 'arial 12 bold', 'fg': '#aa7777'});
    #--------------------------------------------------------------------------#
    def build(s):
        # label
        s.wgrid.make( 0, 0, spec(
            name='header',
            default='Protocols',
            widgetClass=ttk.Label,
            createKWA={'style':'PaneHeader.TLabel'},
            packKWA={'padx': 5, 'pady': 5}
        ), packKWA={'sticky':'w'});
        # treebox
        s.columnspecs = [
            spec(name='id', label='protocol_id')];
        s.wgrid.add( 0, 1, treeBox(s.wgrid, s.specs['treebox'],
            columnspecs=s.columnspecs, xscroll=False), packKWA={});
        # buttons
        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));  # button grid
        s.wgrid.add( 0, 2, s.bgrid, packKWA={} );   # add button grid to wgrid
        s.bgrid.make(0, 0, s.specs['b.create'], packKWA={} );
        s.bgrid.make(1, 0, s.specs['b.delete'], packKWA={} );
        # s.bgrid.make(2, 0, s.specs['b.inspect'], packKWA={} );
        s.bgrid.make(3, 0, s.specs['b.refresh'], packKWA={} );
        s.bgrid.make(4, 0, s.specs['b.import'], packKWA={} );
        s.bgrid.make(5, 0, s.specs['b.export'], packKWA={} );
        # s.bgrid.make(4, 0, s.specs['b.queue'], packKWA={} );
        # pack
        s.bgrid.packWidgets(); # pack widgets inside of bgrid
        s.wgrid.packWidgets(); # pack object in outermost grid, including bgrid
        s.wgrid.pack();
        # bind
        s.bgrid.widget('b.create').obj.bind('<Button-1>',  s._ba_create);
        s.bgrid.widget('b.delete').obj.bind('<Button-1>', s._ba_delete);
        # s.bgrid.widget('b.inspect').obj.bind('<Button-1>', s._ba_inspect);
        s.bgrid.widget('b.refresh').obj.bind('<Button-1>', s._ba_refresh);
        s.bgrid.widget('b.import').obj.bind('<Button-1>', s._ba_import);
        s.bgrid.widget('b.export').obj.bind('<Button-1>', s._ba_export);
#        s.bgrid.widget('b.queue').obj.bind('<Button-1>', s._ba_queue);
        s.wgrid.widget('treebox').obj.bind('<Double-1>', s._ba_inspect);
    #--------------------------------------------------------------------------#
    def _selectedItemID(s):
        sel = s.wgrid.widget('treebox').selected();
        if sel=='': return None;
        return s.wgrid.widget('treebox').row(sel)['id'];
    #--------------------------------------------------------------------------#
    # BUTTON ACTIONS
    #--------------------------------------------------------------------------#
    # def _ba_queue(s, e):
    #     s.root.appendQueue();
    #--------------------------------------------------------------------------#
    def _ba_import(s, e):
        s.root.importProtocol();
        return;
    #--------------------------------------------------------------------------#
    def _ba_export(s, e):
        protocol_id = s._selectedItemID();
        s.root.exportProtocol(protocol_id);
        return;
    #--------------------------------------------------------------------------#
    def _ba_create(s, e):
        s.root.defineProtocol();
        # pm = protocolMaker(s.root, spec(name='pm'));
        # s.root.updateProtocolList();
        return;
    #--------------------------------------------------------------------------#
    def _ba_delete(s, e):
        s.root.deleteProtocol();
        s.root.updateProtocolList();
        return;
    #--------------------------------------------------------------------------#
    def _ba_inspect(s, e):
        protocol_id = s._selectedItemID();
        if protocol_id==None:
            s._errorWindow("No protocol is selected");
            return;
        # try to import and activate labbook
        try: protocol_object = s._importProtocol(protocol_id);
        except Exception as e:
            s._errorWindow(str(e));
            return;
        if protocol_object==None: return;
        pi = protocolInspector(s.root, spec(name='pi'), protocol_object);
    #--------------------------------------------------------------------------#
    def _ba_refresh(s, e):
        s.root.updateProtocolList();
    #--------------------------------------------------------------------------#
    # def _ba_export(s, e):
    #     pw = popup(s.root, mspec=s.specs['p.msg.unavailable']).grab();
    #--------------------------------------------------------------------------#
    # def _ba_import(s, e):
    #     pw = popup(s.root, mspec=s.specs['p.msg.unavailable']).grab();
    #--------------------------------------------------------------------------#
    def _refreshList(s):
        return;
    #--------------------------------------------------------------------------#
    def _importProtocol(s,protocol_id):
        full = '.'.join(['pyLabbook','protocols', protocol_id]);
        # check modules
        if full not in sys.modules:
            # import
            try: module = importlib.import_module(full);
            except Exception as e:
                raise Exception("Can't import " + full + ": " + str(e));
        # try to load
        try:
            protocol_object = sys.modules[full].initialize(dummy_labbook);
        except Exception as e:
            raise Exception("Can't initialize " + full + ": " + str(e));
        return protocol_object;
    #--------------------------------------------------------------------------#
    def _errorWindow(s, msg):
        ew = popupError(s.root, msg).grab();
    def _ackWindow(s, msg):
        ew = popupAcknowledgement(s.root, msg).grab();
################################################################################
class protocolInspector(tk.Toplevel):
    def __init__(s, root, aspec, protocol_object):
        tk.Toplevel.__init__(s);
        s.resizable(width=False, height=False);
        s.root = root;
        s.protocol = protocol_object;
        s._mastercontainer = ttk.Frame(s);
        s._mastercontainer.pack(fill='both', expand=True);
        s._container = ttk.Frame(s._mastercontainer);
        s._container.pack();
        s.wgrid = widgetGrid(s._container,spec(name='grid'));
        s.specs = { };
        s.styles = { };
        s.make_styles();
        s.make_specs();
        s.build();

    def make_styles(s):
        return;

    def make_specs(s):
        checkbox_formatter = lambda x: s.root.bTrue if x else s.root.bFalse;
        empty_formatter = lambda x: '' if x==None else x;

        s.columnspecs = [
            spec(name='name', type=str, label='name', widgetClass=ttk.Entry,
                default="", width=250, createKWA={'width': 20},
                displayFormatter=empty_formatter),
            spec(name='type', type=str, label='type', widgetClass=ttk.Combobox,
                options=['TEXT','REAL','INTEGER','NUMERIC','DATE'],
                default='TEXT', createKWA={'state': 'readonly', 'width': 10}, displayFormatter=empty_formatter, width=100),
            spec(name='notnull', type=bool, label='NN',
                widgetClass=ttk.Checkbutton, default=False, width=30,
                displayFormatter=checkbox_formatter,
                ),
            spec(name='unique', type=bool, label='UNQ',
                widgetClass=ttk.Checkbutton, default=False, width=30,
                displayFormatter=checkbox_formatter,
                ),
            spec(name='default', type=str, label='default',
                createKWA={'width': 20},
                default="", widgetClass=ttk.Entry, width=150,
                displayFormatter=empty_formatter),
            spec(name='description', type=str, label='description',
                createKWA={'width': 40}, default="", widgetClass=ttk.Entry, width=400, displayFormatter=empty_formatter),
        ];
        s.specs['treebox'] = spec(name='treebox');
        return;

    def build(s):
        s.hgrid = widgetGrid(s.wgrid, spec(name='hgrid'));
        s.hgrid.make(0, 0, spec(name='pidlabel',
            widgetClass=ttk.Label,
            default="Protocol ID",
            style={'font':'arial 20 bold'}
        ));
        s.hgrid.make(1, 0, spec(name='protocol_id',
            widgetClass=ttk.Label,
            default=str(s.protocol.PROTOCOLID),
            style={'font':'arial 20'}
        ));

        pset = treeBox(s.wgrid, spec(name='setbox'), columnspecs=s.columnspecs);
        pset.loadDataFrame(s.protocol.setDesc());
        psam = treeBox(s.wgrid, spec(name='sambox'), columnspecs=s.columnspecs);
        psam.loadDataFrame(s.protocol.samDesc());

        s.wgrid.add(0, 0, s.hgrid, packKWA={'sticky':'w'});
        s.wgrid.make(0, 1, spec(name='setlabel', default="Set Description",
            widgetClass=ttk.Label, style={'font':'arial 15 bold'}));
        s.wgrid.add(0, 2, pset);
        s.wgrid.make(0, 3, spec(name='samlabel', default="Sample Description",
            widgetClass=ttk.Label, style={'font':'arial 15 bold'}));
        s.wgrid.add(0, 4, psam);
        s.wgrid.make(0, 5, spec(name='okbutton', label="OK",
            widgetClass=ttk.Button), packKWA={'sticky':'e'});

        s.hgrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack();

        s.wgrid.widget('okbutton').obj.bind('<Button-1>', s._ba_ok);
        s.wgrid.widget('setbox').obj.bind('<Double-1>', s._dblclick_set);
        s.wgrid.widget('sambox').obj.bind('<Double-1>', s._dblclick_sam);

        s.bind('<Return>', s._ba_ok);
        s.bind('<Escape>', s._ba_ok);

    def _dblclick_set(s, e):
        tix = s.wgrid.widget('setbox').obj.selection()[0];
        row = s.wgrid.widget('setbox').row( tix );
        popupRowDisplay(s,
            titlespec=spec(name='title', default="Set Field",
                style={'font':'arial 20 bold'},
            ),
            headerspec=spec(name='header',
                style={'font':'arial 14 bold'},
            ),
            infospec=spec(name='info',
                style={'font':'arial 14'},
            ),
            row=row
        ).grab();

    def _dblclick_sam(s, e):
        tix = s.wgrid.widget('sambox').obj.selection()[0];
        row = s.wgrid.widget('sambox').row( tix );
        popupRowDisplay(s,
            titlespec=spec(name='title', default="Sample Field",
                style={'font':'arial 20 bold'},
            ),
            headerspec=spec(name='header',
                style={'font':'arial 14 bold'},
            ),
            infospec=spec(name='info',
                style={'font':'arial 14'},
            ),
            row=row
        ).grab();

    def _ba_ok(s, e):
        s.destroy();
        s.root.focus_force();
        return;
################################################################################
class protocolMaker(tk.Toplevel):
    def __init__(s, root, aspec):
        tk.Toplevel.__init__(s);
        s.resizable(width=False, height=False);
        s.root = root;
        s._mastercontainer = ttk.Frame(s);
        s._mastercontainer.pack(fill='both', expand=True);
        s._container = ttk.Frame(s);
        s._container.pack();
        s.wgrid = widgetGrid(s._container,spec(name='grid'));
        s.spec = aspec;
        s.specs = { };
        s.styles = { };
        s.make_styles();
        s.make_specs();
        s.build();

    def make_styles(s):
        return;

    def make_specs(s):
        s.specs['l.pid'] = spec(name='l.pid', default="Protocol id",
            widgetClass=ttk.Label, width=10,
            packKWA={'anchor': 'w'});
        s.specs['e.pid'] = spec(name='e.pid', default="NewProtocol",
            widgetClass=ttk.Entry,
            packKWA={'anchor': 'e'});
        s.specs['ss.head'] = spec(name='ss.head', default="Definition",
            widgetClass=ttk.Label,
            style={'font':'arial 20 bold'});
        s.specs['b.ok'] = spec(name='b.ok', label="OK",
            widgetClass=ttk.Button);
        s.specs['b.cancel'] = spec(name='b.cancel', label="Cancel",
            widgetClass=ttk.Button);
        s.specs['hsep'] = spec(name='hs', widgetClass=ttk.Separator,
            createKWA={'orient': 'horizontal'}, packKWA={'fill':'both'});

        return;

    def build(s):
        s.hgrid = widgetGrid(s.wgrid, spec(name='hgrid'));
        s.hgrid.make(0, 0, s.specs['l.pid']);
        s.hgrid.make(1, 0, s.specs['e.pid']);

        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));
        s.bgrid.make(0, 0, s.specs['b.cancel']);
        s.bgrid.make(1, 0, s.specs['b.ok']);

        pset = protocolSetSamMaker(s.wgrid, s.specs['ss.head'].copy().re(
            name='setdesc', default="Set Fields"
        ));
        psam = protocolSetSamMaker(s.wgrid, s.specs['ss.head'].copy().re(
            name='samdesc', default="Sample Fields"
        ));

        s.wgrid.add(0, 0, s.hgrid, packKWA={'sticky':'w'});
        s.wgrid.make(0, 1, s.specs['hsep'].copy().re(name='hs1'),
            packKWA={'sticky':'ew'});
        s.wgrid.add(0, 2, pset, packKWA={});
        s.wgrid.make(0, 3, s.specs['hsep'].copy().re(name='hs2'),
            packKWA={'sticky':'ew'});
        s.wgrid.add(0, 4, psam, packKWA={});
        s.wgrid.make(0, 5, s.specs['hsep'].copy().re(name='hs3'),
            packKWA={'sticky':'ew'});
        s.wgrid.add(0, 6, s.bgrid, packKWA={'sticky':'e'});

        s.hgrid.packWidgets();
        s.bgrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack();

        s.bgrid.widget('b.ok').obj.bind('<Button-1>', s._ba_ok);
        s.bgrid.widget('b.cancel').obj.bind('<Button-1>', s._ba_cancel);

    def _ba_ok(s, e):
        pid = s.hgrid.widget('e.pid').var.get();
        if not core.validID(pid):
            message.showerror("Error","'" + str(pid) + "' contains invalid " +
                "characters");
            return;
        # attempt to initialize a new protocol
        np = pyProtocol(dummy_labbook);
        try: np.PROTOCOLID = pid;
        except Exception as e:
            messagebox.showerror("Error", "Can't assign id '" + str(pid) +
                "': " + str(e));
            return;
        u_setdesc=s.wgrid.widget('setdesc').wgrid.widget('treebox').var;
        u_samdesc=s.wgrid.widget('samdesc').wgrid.widget('treebox').var;
        setc = \
        s.wgrid.widget('setdesc').wgrid.widget('treebox').obj.get_children();
        u_setdesc=u_setdesc.loc[setc,:];
        samc = \
        s.wgrid.widget('samdesc').wgrid.widget('treebox').obj.get_children();
        u_samdesc=u_samdesc.loc[samc,:];

        for i,r in u_setdesc.iterrows():
            default = None;
            if r['default']!='':
                try: default = SQLEngine.dmap[r['type']]['py'](r['default']);
                except:
                    messagebox.showerror("Error",
                        "Can't cast default value '" +
                        str(r['default']) + "' into type " + str(r['type']) + ".");
                    return;
            try:
                np.addSetColumn(
                    name = r['name'],
                    type = r['type'],
                    notnull = bool(r['notnull']),
                    unique = bool(r['unique']),
                    description = r['description'],
                    default = default,
                    primary_key = False,
                );
            except Exception as e:
                messagebox.showerror("Error",
                "Error adding '" + str(r['name']) + "': " + str(e));
                return;
        for i,r in u_samdesc.iterrows():
            default = None;
            if r['default']!='':
                try: default = SQLEngine.dmap[r['type']]['py'](r['default']);
                except:
                    messagebox.showerror("Error",
                        "Can't cast default value '" +
                        str(r['default']) + "' into type " + str(r['type']) + ".");
                    return;
            try:
                np.addSamColumn(
                    name = r['name'],
                    type = r['type'],
                    notnull = r['notnull'],
                    unique = r['unique'],
                    description = r['description'],
                    default = default,
                    primary_key = False,
                );
            except Exception as e:
                messagebox.showerror("Error",
                "Error adding '" + str(r['name']) + "': " + str(e));
                return;
        # defined, so call maker with new object
        if s.root.createProtocol(np):
            s.root.focus_force();
            s.destroy();
        else: return;

    def grab(s):
        s.transient(s.root);
        s.grab_set();
        s.root.wait_window(s);


    def _ba_cancel(s, e):
        s.destroy();
        s.root.focus_force();
        return;
################################################################################
class protocolSetSamMaker(ttk.Frame):
    def __init__(s, master, aspec):
        ttk.Frame.__init__(s, master);
        s.master = master;
        s._mastercontainer = ttk.Frame(s);
        s._mastercontainer.pack(fill='both', expand=True);
        s._container = ttk.Frame(s._mastercontainer);
        s._container.pack();
        s.wgrid = widgetGrid(s._container,spec(name='grid'));
        s.spec = aspec;
        s.specs = { };
        s.styles = { };
        s.selectedtid = None;
        s.make_styles();
        s.make_specs();
        s.build();

    def make_styles(s):
        return;

    def make_specs(s):
        s.bTrue='\u25CF';
        s.bFalse='\u25CB';
        checkbox_formatter = lambda x: s.bTrue if x else s.bFalse;
        s.columnspecs = [
            spec(name='name', type=str, label='name', widgetClass=ttk.Entry,
                default="", width=250, createKWA={'width': 20}),
            spec(name='type', type=str, label='type', widgetClass=ttk.Combobox,
                options=['TEXT','REAL','INTEGER','NUMERIC','DATE'],
                default='TEXT', createKWA={'state': 'readonly', 'width': 10}, width=100),
            spec(name='notnull', type=bool, label='NN',
                widgetClass=ttk.Checkbutton, default=False, width=30,
                displayFormatter=checkbox_formatter,
                ),
            spec(name='unique', type=bool, label='UNQ',
                widgetClass=ttk.Checkbutton, default=False, width=30,
                displayFormatter=checkbox_formatter,
                ),
            spec(name='default', type=str, label='default',
                createKWA={'width': 20},
                default="", widgetClass=ttk.Entry, width=200),
            spec(name='description', type=str, label='description',
                createKWA={'width': 40}, default="", widgetClass=ttk.Entry, width=350),
        ];
        bsty={'width':2};
        s.buttonspecs = [
            spec(name='add', label='\u271A', widgetClass=ttk.Button,style=bsty),
            spec(name='delete', label='\u2716', widgetClass=ttk.Button,style=bsty),
            spec(name='moveup', label='\u2191', widgetClass=ttk.Button,style=bsty),
            spec(name='movedn', label='\u2193', widgetClass=ttk.Button,style=bsty),
            spec(name='edit', label='\u21EA', widgetClass=ttk.Button,style=bsty),
        ]
        s.specs['treebox'] = spec(name='treebox');
        return;

    def build(s):
        s.hgrid = widgetGrid(s.wgrid, spec(name='hgrid'));
        # would like separators on either side of title here
        s.hgrid.make(0, 0, s.spec, packKWA={});

        s.egrid = widgetGrid(s.wgrid, spec(name='egrid'));
        for i,sp in enumerate(s.columnspecs):
            s.egrid.make(i, 0, sp.copy().re(
                widgetClass=ttk.Label,
                name='l.' + sp.name,
                default=sp.label,
                createKWA={'style':'Field.TLabel'},
            ));
            s.egrid.make(i, 1, sp, packKWA={});

        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));
        for i,b in enumerate(s.buttonspecs):
            s.bgrid.make(i, 0, b);


        s.wgrid.add(0, 0, s.hgrid);
        s.wgrid.add(0, 2, s.egrid, packKWA={});
        s.wgrid.add(0, 3, treeBox(
            s.wgrid, s.specs['treebox'], columnspecs=s.columnspecs
        ));
        s.wgrid.add(0, 4, s.bgrid, packKWA={'sticky':'e'});

        s.hgrid.packWidgets();
        s.egrid.packWidgets();
        s.bgrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack();

        s.bgrid.widget('add').obj.bind('<Button-1>', s._ba_add);
        s.bgrid.widget('moveup').obj.bind('<Button-1>', s._ba_moveup);
        s.bgrid.widget('movedn').obj.bind('<Button-1>', s._ba_movedn);
        s.bgrid.widget('delete').obj.bind('<Button-1>', s._ba_delete);
        s.bgrid.widget('edit').obj.bind('<Button-1>', s._ba_edit);
        s._setEntryDefaults();

        s.button = empty();
        s.button.add = s.bgrid.widget('add');
        s.button.moveup = s.bgrid.widget('moveup');
        s.button.movedn = s.bgrid.widget('movedn');
        s.button.delete = s.bgrid.widget('delete');
        s.button.edit = s.bgrid.widget('edit');
        return;

    def _ba_edit(s, e):
        # uses "pop-edit" functionality so user can
        # use moveup and movedn during active edit
        if s.wgrid.widget('treebox').selected()=='': return;
        selrow = s.wgrid.widget('treebox').row(
            s.wgrid.widget('treebox').selected());
        # remove from treeview
        s.wgrid.widget('treebox').delete(selrow.name);
        # pop into entry fields
        for c in s.columnspecs:
            s.egrid.widget(c.name).var.set( selrow[c.name] );
        # is that it?

    def _ba_add(s, e):
        # get info
        newrow = pd.Series();
        for c in s.columnspecs:
            newrow[c.name] = s.egrid.widget(c.name).var.get();
        # validate
        if newrow['name']=="": return;
        if newrow['name'] in s.wgrid.widget('treebox').var['name'].tolist():
            messagebox.showerror("Error", "'" + str(newrow['name']) +
                "' already exists.");
            return;
        if not core.validID(newrow['name']):
            messagebox.showerror("Error", "'" + str(newrow['name']) +
                "' contains invalid characters.");
            return;
        if newrow['default']!='':
            try:
                newrow['default'] = SQLEngine.dmap[newrow['type']]['py']( newrow['default'] );
            except:
                messagebox.showerror("Error", "Can't cast default value '" +
                    str(newrow['default']) + "' into type " + str(newrow['type']) + ".");
                return;
        # insert
        try: s.wgrid.widget('treebox').append(newrow);
        except Exception as e:
            messagebox.showerror("Error", "Error inserting row: " + str(e));
            raise;
        # reset entry fields
        s._setEntryDefaults();

    def _ba_delete(s, e):
        if s.wgrid.widget('treebox').selected()=='': return;
        s.wgrid.widget('treebox').delete(
            s.wgrid.widget('treebox').selected()
        );

    def _ba_moveup(s, e):
        # exclusively through treeview, order is obtained at save
        if s.wgrid.widget('treebox').selected()=='': return;
        tit = s.wgrid.widget('treebox').obj.focus();
        s.wgrid.widget('treebox').obj.move(
            tit,
            '',
            s.wgrid.widget('treebox').obj.index(
                s.wgrid.widget('treebox').obj.prev(tit)
            )
        );

    def _ba_movedn(s, e):
        # exclusively through treeview, order is obtained at save
        if s.wgrid.widget('treebox').selected()=='': return;
        tit = s.wgrid.widget('treebox').obj.focus();
        s.wgrid.widget('treebox').obj.move(
            tit,
            '',
            s.wgrid.widget('treebox').obj.index(
                s.wgrid.widget('treebox').obj.next(tit)
            )
        );

    def _setEntryDefaults(s):
        for c in s.columnspecs:
            s.egrid.widget(c.name).var.set( c.default );
################################################################################
class experimentPane(ttk.Frame):
    #--------------------------------------------------------------------------#
    def __init__(s, master, aspec, columnspecs=[
        spec(name='id', label='ID')
    ], root=None, glob={}):
        ttk.Frame.__init__(s, master);
        s.root = root;
        s.glob = glob;
        s.spec = aspec;
        def boolformat(x):
            bTrue = '\u25CF';
            bFalse = '\u25CB';
            # pandas is auto-converting bool's to str
            if type(x)==str:
                if x in ['Y','y','1','True','true']: x=True;
                else: x=False;
            if x==True: return bTrue;
            elif x==False: return bFalse;
            else: raise Exception("unrecognized bool value");
        s.columnspecs = [
            spec(name='experiment_id', label='experiment_id',
            width=220,
            ),
            spec(name='sets', label='Sets',
            width=70,
            ),
            spec(name='sams', label='Sams',
            width=70,
            ),
            spec(name='repository', label='Repo.',
            width=50,
            displayFormatter=boolformat,
            ),
            spec(name='setfile', label='Set',
            width=50,
            displayFormatter=boolformat,
            ),
            spec(name='samfile', label='Sam',
            width=50,
            displayFormatter=boolformat,
            ),
        ];
        s.wgrid = widgetGrid(s, spec(name='wgrid'));
        s.make_specs();
        s.build();
    #--------------------------------------------------------------------------#
    # DEFINE AND BUILD WIDGETS
    #--------------------------------------------------------------------------#
    def make_specs(s):
        s.specs = {};
        bsty = {'width':3};
        s.specs['b.create'] = spec( name='b.create', label='\u271A',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.delete'] = spec( name='b.delete', label='\u2716R',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.drop'] = spec( name='b.drop', label='\u2716D',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.refresh'] = spec( name='b.refresh', label='\u25C9',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.store'] = spec( name='b.store', label='\u21A9',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.restore'] = spec( name='b.restore', label='\u21AA',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.queue_all'] = spec(name='b.queue_all', label='\u21F6',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.queue_sel'] = spec(name='b.queue_sel', label='\u21FE',
            style=bsty, widgetClass=ttk.Button);

        s.specs['p.msg.unavailable'] = spec(name='p.msg.unavailable',
            style={'font': 'arial 14 bold'},
            default="Sorry, that functionality isn't avilable yet.",
            widgetClass=ttk.Label);
        s.specs['treebox'] = spec(name='treebox',
            createKWA={'height': 16,'selectmode':'extended'});
        s.specs['p.msg.error'] = spec(name='p.msg.error',
            style={'font': 'arial 12 bold', 'fg': '#aa7777'});
    #--------------------------------------------------------------------------#
    def build(s):
        # label
        s.hgrid = widgetGrid(s.wgrid, spec(name='hgrid'));

        s.hgrid.make( 0, 0, spec(
            name='header',
            default='Experiments',
            widgetClass=ttk.Label,
            createKWA={'style':'PaneHeader.TLabel'},
            packKWA={'padx': 5, 'pady': 5}
        ), packKWA={'sticky':'w'});

        s.hgrid.make(1, 0, spec(
            name='plb',
            default=" ",
            widgetClass=ttk.Label,
            createKWA={'style':'Selected.TLabel'},
        ), packKWA={'sticky':'e','padx':1});

        s.wgrid.add(0, 0, s.hgrid, packKWA={'sticky':'nesw'});

        s.wgrid.add( 0, 1, treeBox(s.wgrid, s.specs['treebox'],
            columnspecs=s.columnspecs, xscroll=False), packKWA={});
        # buttons
        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));  # button grid
        s.wgrid.add( 0, 2, s.bgrid, packKWA={} );   # add button grid to wgrid
        s.bgrid.make(0, 0, s.specs['b.create'], packKWA={} );
        s.bgrid.make(1, 0, s.specs['b.delete'], packKWA={} );
        s.bgrid.make(2, 0, s.specs['b.drop'], packKWA={} );
        s.bgrid.make(3, 0, s.specs['b.refresh'], packKWA={} );
        s.bgrid.make(4, 0, s.specs['b.store'], packKWA={} );
        s.bgrid.make(5, 0, s.specs['b.restore'], packKWA={} );
        s.bgrid.make(6, 0, s.specs['b.queue_all'], packKWA={} );
        s.bgrid.make(7, 0, s.specs['b.queue_sel'], packKWA={} );
        # pack
        s.hgrid.packWidgets();
        s.bgrid.packWidgets(); # pack widgets inside of bgrid
        s.wgrid.packWidgets(); # pack object in outermost grid, including bgrid
        s.wgrid.pack();
        # bind
        s.bgrid.widget('b.create').obj.bind('<Button-1>',  s._ba_create);
        s.bgrid.widget('b.delete').obj.bind('<Button-1>', s._ba_delete);
        s.bgrid.widget('b.drop').obj.bind('<Button-1>', s._ba_drop);
        s.bgrid.widget('b.refresh').obj.bind('<Button-1>', s._ba_refresh);
        s.bgrid.widget('b.store').obj.bind('<Button-1>', s._ba_store);
        s.bgrid.widget('b.restore').obj.bind('<Button-1>', s._ba_restore);
        s.bgrid.widget('b.queue_all').obj.bind('<Button-1>', s._ba_queue_all);
        s.bgrid.widget('b.queue_sel').obj.bind('<Button-1>', s._ba_queue_sel);
        s.wgrid.widget('treebox').obj.bind('<Double-1>', s._ba_inspect);
        # initialize widgets where needed

    #--------------------------------------------------------------------------#
    def _selectedItemID(s):
        sel = s.wgrid.widget('treebox').obj.focus();
        if sel=='': return None;
        return s.wgrid.widget('treebox').row(sel)['experiment_id'];
    #--------------------------------------------------------------------------#
    def _selectedItemRow(s):
        sel = s.wgrid.widget('treebox').selected();
        if sel=='': return None;
        return s.wgrid.widget('treebox').row(sel);
    #--------------------------------------------------------------------------#
    # BUTTON ACTIONS
    #--------------------------------------------------------------------------#
    def _ba_drop(s, e):
        sel = s.wgrid.widget('treebox').obj.selection();
        if len(sel)==0: return;
        eids = s.wgrid.widget('treebox').var.loc[sel,'experiment_id'];
        s.root.dropExperimentIDS(eids);
        return;
    #--------------------------------------------------------------------------#
    def _ba_queue_all(s, e):
        if s.root.c_labbook==None or s.root.c_protocol==None: return;
        esids = pd.DataFrame();
        esids['experiment_id'] = \
            s.wgrid.widget('treebox').var.loc[:,'experiment_id'];
        esids['set_id']='*';
        esids['labbook_id'] = s.root.c_labbook.id;
        esids['protocol_id'] = s.root.c_protocol.PROTOCOLID;
        s.root.appendsQueue(esids);
    #--------------------------------------------------------------------------#
    def _ba_queue_sel(s, e):
        if s.root.c_labbook==None or s.root.c_protocol==None: return;
        sel = s.wgrid.widget('treebox').obj.selection();
        esids = pd.DataFrame();
        esids['experiment_id'] = s.wgrid.widget('treebox').var.loc[
            sel,'experiment_id'];
        esids['set_id']='*';
        esids['labbook_id'] = s.root.c_labbook.id;
        esids['protocol_id'] = s.root.c_protocol.PROTOCOLID;
        s.root.appendsQueue(esids);
#        s.root.appendQueue(s._selectedItemID());
    #--------------------------------------------------------------------------#
    def _ba_create(s, e):
        s.root.defineExperiment();
        return;
    #--------------------------------------------------------------------------#
    def _ba_delete(s, e):
        sel = s.wgrid.widget('treebox').obj.selection();
        if len(sel)==0:
            return;
        eids = s.wgrid.widget('treebox').var.loc[sel,'experiment_id'];

        if not messagebox.askyesno("warning","WARNING: this will delete all "+
            "of the files in each experiment repository folder.  Are you "+
            "sure about this?", default='no'
        ):
            return;
        s.root.deleteExperimentIDS(eids);
        return;
    #--------------------------------------------------------------------------#
    def _ba_refresh(s, e):
        s.root.setExperimentLabbookProtocol();
    #--------------------------------------------------------------------------#
    def _ba_export(s, e):
        pw = popup(s.root, mspec=s.specs['p.msg.unavailable']).grab();
    #--------------------------------------------------------------------------#
    def _ba_import(s, e):
        pw = popup(s.root, mspec=s.specs['p.msg.unavailable']).grab();
    #--------------------------------------------------------------------------#
    def _ba_store(s, e):
        sel = s.wgrid.widget('treebox').obj.selection();
        if len(sel)==0:
            return;
        eids = s.wgrid.widget('treebox').var.loc[sel,'experiment_id'];
        s.root.storeExperimentIDS(eids);
        return;
    #--------------------------------------------------------------------------#
    def _ba_restore(s, e):
        sel = s.wgrid.widget('treebox').obj.selection();
        if len(sel)==0:
            return;
        eids = s.wgrid.widget('treebox').var.loc[sel,'experiment_id'];
        s.root.restoreExperimentIDS(eids);
        return;
    #--------------------------------------------------------------------------#
    def _ba_inspect(s, e):
        eid = s._selectedItemID();
        s.root.inspectExperimentID(eid);
        return;
    #--------------------------------------------------------------------------#
    def _refreshList(s,protocol_object):
        return;
################################################################################
################################################################################
################################################################################
# class setViewer(tk.Toplevel):
#     def __init__(s,root,lbpath,setdata,columnspecs=[]):
#         tk.Toplevel.__init__(s);
#         s.root = root;
#         s.root.logger.debug("setViewer("+lbpath+").");
#         s.setdata = setdata;
#         s.filler = ttk.Frame(s);
#         s.filler.pack(fill='both', expand=True);
#         s.container = ttk.Frame(s.filler);
#         s.container.pack(fill='both', expand=True);
#         s.maxsize(1000,800);
#         s.specs = {};
#         s.specs['tb'] = spec(name='treebox',
#             packKWA={'fill':'both', 'expand':True});
#         s.specs['tbc'] = [];
#         if len(columnspecs)==0:
#             for c in s.setdata.columns:
#                 s.specs['tbc'].append(spec(name=c, label=c, default=c));
#         else: s.specs['tbc'] = columnspecs;
#
#         s.wgrid = widgetGrid(s.container, spec(name='wgrid'));
#         s.hgrid = widgetGrid(s.wgrid, spec(name='hgrid'));
#         s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));
#
#         s.hgrid.make(0, 0, spec(name='sets', default='Sets',
#             widgetClass=ttk.Label), packKWA={'sticky': 'w'});
#         s.hgrid.make(1, 0, spec(name='lbpath', default=lbpath,
#             widgetClass=ttk.Label), packKWA={'sticky': 'e'});
#
#         s.hgrid.packWidgets();
#
#         s.bgrid.make(0, 0, spec(name='b.ok', label="OK",
#             widgetClass=ttk.Button), packKWA={'sticky': 'e'});
#         s.bgrid.packWidgets();
#
#         s.wgrid.add(0, 0, s.hgrid, packKWA={'sticky':'nesw'});
#         s.wgrid.add(0, 1, treeBox(s.wgrid,
#             s.specs['tb'], columnspecs=s.specs['tbc'],
#             xscroll=True, yscroll=False),
#             packKWA={'sticky':'nesw'}
#         );
#
#         s.wgrid.add(0, 2, s.bgrid);
#
#         s.wgrid.packWidgets();
#         s.wgrid.pack(fill='both',expand=True);
#         s.wgrid.rowconfigure(0, weight=0);
#         s.wgrid.rowconfigure(2, weight=0);
#
#         s.wgrid.widget('treebox').loadDataFrame(s.setdata);
#
#         s.bgrid.widget('b.ok').obj.bind('<Button-1>', s._ba_ok);
#         s.bind('<Return>', s._ba_ok);
#         s.bind('<Escape>', s._ba_ok);
#         s.wgrid.widget('treebox').obj.bind('<Double-1>', s._ba_doubleclick);
#
#     def grab(s):
#         s.transient(s.root);
#         s.grab_set();
#         s.root.wait_window(s);
#
#     def _ba_ok(s, e):
#         s.close();
#
#     def _ba_doubleclick(s, e):
#         selix = s.wgrid.widget('treebox').selected();
#         row = s.wgrid.widget('treebox').row(selix);
#         print(row);
#         s.root.appendsQueue(row[['experiment_id','set_id']]);
#
#     def close(s):
#         s.destroy();
#         s.root.focus_force();
################################################################################
class setViewer(tk.Toplevel):
    def __init__(s,root,lbpath,wheres,labbook,protocol,columnspecs=[]):
        tk.Toplevel.__init__(s);
        s.root = root;
        s.labbook = labbook;
        s.protocol = protocol;
        s.lbp = '.'.join([s.labbook.id,s.protocol.PROTOCOLID]);
        s.title("pyLabbook: "+s.lbp+" sets");
        s.filler = ttk.Frame(s);
        s.filler.pack(fill='both', expand=True);
        s.container = ttk.Frame(s.filler);
        s.container.pack(fill='both', expand=True);
        s.maxsize(1000,800);
        s.specs = {};
        s.specs['tb'] = spec(name='treebox',
            packKWA={'fill':'both', 'expand':True});
        s.specs['tbc'] = [];
        if len(columnspecs)==0:
            for c in s.setdata.columns:
                type = s.desc['type'][s.desc['name']==c].iloc[0];
                s.specs['tbc'].append(
                    spec(
                        name=c,
                        label=c,
                        default=c,
                    )
                );
        else: s.specs['tbc'] = columnspecs;
        s.columnspecs=s.specs['tbc']; # FIX: just one copy of this please
        s.wheres = pd.DataFrame(columns=['andor','field','op','value']);
        s.wheres = pd.concat([s.wheres,wheres],ignore_index=True).reset_index();
        bsty = {'width':3};
        s.specs['b.queueall'] = spec(
            name='b.queueall',
            widgetClass=ttk.Button,
            label='\u21F6',
            createKWA=bsty,
        );
        s.specs['b.queueselected'] = spec(
            name='b.queueselected',
            widgetClass=ttk.Button,
            label='\u21FE',
            createKWA=bsty,
        );

        s.specs['e.active'] = spec(
            name='e.active',
            widgetClass=ttk.Checkbutton,
            default=False,
            width=2,
        );
        s.specs['e.andor'] = spec(
            name='e.andor',
            widgetClass=ttk.Combobox,
            options=['and','or'],
            default='and',
            createKWA={'width': 5, 'state':'readonly'},
        );
        s.specs['e.field'] = spec(
            name='e.field',
            widgetClass=ttk.Combobox,
            options=[sp.name for sp in s.columnspecs],
            default=s.columnspecs[0].name,
            createKWA={'width': 20, 'state':'readonly'},
        );
        s.specs['e.op'] = spec(
            name='e.op',
            widgetClass=ttk.Combobox,
            # options=s.root.c_protocol.sql.ops,
            # default=s.root.c_protocol.sql.ops[0],
            options=s.protocol.sql.ops,
            default=s.protocol.sql.ops[0],
            createKWA={'width':5, 'state':'readonly'},
        );
        s.specs['e.value'] = spec(
            name='e.value',
            default="",
            widgetClass=ttk.Entry,
            createKWA={'width':25},
        );
        s.specs['e.b.filter'] = spec(
            name='e.b.filter',
            widgetClass=ttk.Button,
            label='select'
        );

        s.wgrid = widgetGrid(s.container, spec(name='wgrid'));
        s.hgrid = widgetGrid(s.wgrid, spec(name='hgrid'));
        s.bcgrid = widgetGrid(s.wgrid, spec(name='bcgrid'));
        s.bbbgrid = widgetGrid(s.bcgrid, spec(name='bccgrid'));
        s.bgrid = widgetGrid(s.bcgrid, spec(name='bgrid'));
        s.egrid = widgetGrid(s.wgrid, spec(name='egrid'));
        s.wbgrids = {};

        s.whereblocks = [1,2,3];
        # build where entry widgets using passed where values
        for i,n in enumerate(s.whereblocks):
            s.wbgrids[i] = widgetGrid(s.egrid, spec(name=str(i)));
            if i<len(s.wheres): # have values to set
                s.wbgrids[i].make(0, 0, s.specs['e.active'].copy().re(
                default=True));
                if i>0:
                    s.wbgrids[i].make(1, 0, s.specs['e.andor'].copy().re(
                        default=s.wheres['andor'].iloc[i],
                    ));
                s.wbgrids[i].make(2, 0, s.specs['e.field'].copy().re(
                    default=s.wheres['field'].iloc[i],
                ));
                s.wbgrids[i].make(3, 0, s.specs['e.op'].copy().re(
                    default=s.wheres['op'].iloc[i],
                ));
                s.wbgrids[i].make(4, 0, s.specs['e.value'].copy().re(
                    default=s.wheres['value'].iloc[i],
                ));
            else: # no values to set, use spec defaults
                s.wbgrids[i].make(0, 0, s.specs['e.active'].copy().re(
                default=False));
                if i>0:
                    s.wbgrids[i].make(1, 0, s.specs['e.andor']);
                s.wbgrids[i].make(2, 0, s.specs['e.field']);
                s.wbgrids[i].make(3, 0, s.specs['e.op']);
                s.wbgrids[i].make(4, 0, s.specs['e.value']);
            s.wbgrids[i].packWidgets();
            s.egrid.add(0, i, s.wbgrids[i],packKWA={'sticky':'e'});
        # set first checkbox in where blocks to permanent on
        s.wbgrids[0].widget('e.active').var.set(True);
        s.wbgrids[0].widget('e.active').obj.config(state=tk.DISABLED);
        s.egrid.make(len(s.whereblocks)+1, 0, s.specs['e.b.filter']);
        s.egrid.widget('e.b.filter').obj.bind('<Button-1>', s._ba_filter);
        s.egrid.packWidgets();
        s.wgrid.add(0, 0, s.egrid);

        s.hgrid.make(0, 1, spec(name='sets', default='Sets',
            widgetClass=ttk.Label), packKWA={'sticky': 'w'});
        s.hgrid.make(1, 1, spec(name='lbpath', default=lbpath,
            widgetClass=ttk.Label), packKWA={'sticky': 'e'});

        s.hgrid.packWidgets();

        s.bbbgrid.make(0, 0, s.specs['b.queueall']);
        s.bbbgrid.make(1, 0, s.specs['b.queueselected']);
        s.bbbgrid.packWidgets();
        s.bgrid.make(0, 1, spec(name='b.ok', label="OK",
            widgetClass=ttk.Button), packKWA={'sticky':'e','columnspan':2});
        s.bgrid.packWidgets();

        s.bcgrid.add(0, 0, s.bbbgrid);
        s.bcgrid.add(0, 1, s.bgrid, packKWA={'sticky':'nesw'});
        s.bcgrid.packWidgets();

        s.wgrid.add(0, 1, s.hgrid, packKWA={'sticky':'nesw'});
        s.wgrid.add(0, 2, treeBox(s.wgrid,
            s.specs['tb'], columnspecs=s.specs['tbc'],
            xscroll=True, yscroll=False),
            packKWA={'sticky':'nesw'}
        );

        s.wgrid.add(0, 3, s.bcgrid, packKWA={'sticky':'nesw'});

        s.wgrid.packWidgets();
        s.wgrid.pack(fill='both',expand=True);
        s.wgrid.rowconfigure(0, weight=0);
        s.wgrid.rowconfigure(1, weight=0);
        s.wgrid.rowconfigure(2, weight=1);
        s.wgrid.rowconfigure(3, weight=0);

        s.select();

        s.bgrid.widget('b.ok').obj.bind('<Button-1>', s._ba_ok);
        s.bind('<Return>', s._ba_filter);
        s.bind('<Escape>', s._ba_ok);
        s.wgrid.widget('treebox').obj.bind('<Double-1>', s._ba_doubleclick);
        s.bbbgrid.widget('b.queueall').obj.bind('<Button-1>', s._ba_queueall);
        s.bbbgrid.widget('b.queueselected').obj.bind('<Button-1>', s._ba_queueselected);

    def _ba_filter(s, e):
        #process wheres
        l_wheres = [];
        for i,n in enumerate(s.whereblocks):
            if s.wbgrids[i].widget('e.active').var.get()==True:
                if i>0: andor = s.wbgrids[i].widget('e.andor').var.get();
                else: andor=None;
                field = s.wbgrids[i].widget('e.field').var.get();
                op = s.wbgrids[i].widget('e.op').var.get();
                value = s.wbgrids[i].widget('e.value').var.get();
                # split comma sep if op=in, this should be done
                # somewhere else...  like SQLEngine?
                if op=='in':
                    value = ','.split(value);
                wrow = pd.Series(
                    [andor, field, op, value],
                    index=['andor','field','op','value']
                );
                l_wheres.append(wrow);
        l_wheres = pd.DataFrame(l_wheres);
        s.wheres = l_wheres;
        s.select();

    # TODO: put this into manager.py and have a progress bar
    def select(s):
        # try: s.root.c_protocol.connect();
        try: s.protocol.connect();
        except Exception as e:
            messagebox.showerror("Error","Can't connect to database: "+str(e));
            raise;
        # try: result = s.root.c_protocol.selectSetsFullWhere(s.wheres);
        try: result = s.protocol.selectSetsFullWhere(s.wheres);
        except Exception as e:
            messagebox.showerror("Error","Error selecting: "+str(e));
            # s.root.c_protocol.disconnect();
            return;
        # s.root.c_protocol.disconnect();
        s.protocol.disconnect();
        s.wgrid.widget('treebox').loadDataFrame(result);
        return;

    def grab(s):
        s.transient(s.root);
        s.grab_set();
        s.root.wait_window(s);

    def _ba_ok(s, e):
        s.close();

    def _ba_doubleclick(s, e):
        selix = s.wgrid.widget('treebox').selected();
        row = s.wgrid.widget('treebox').row(selix);
        lpesids = pd.DataFrame(row).T[['experiment_id','set_id']];
        lpesids['labbook_id']=s.labbook.id;
        lpesids['protocol_id']=s.protocol.PROTOCOLID;
        s.root.appendsQueue(lpesids);
#        s.root.appendsQueue(pd.DataFrame(row).T[['experiment_id','set_id']]);
#        s.root.appendQueue(eid=row['experiment_id'], sid=row['set_id']);

    def _ba_queueselected(s, e):
        selix = s.wgrid.widget('treebox').obj.selection();
        rows = s.wgrid.widget('treebox').rows(selix);
        lpesids = rows[['experiment_id','set_id']];
        lpesids['labbook_id']=s.labbook.id;
        lpesids['protocol_id']=s.protocol.PROTOCOLID;
        s.root.appendsQueue(lpesids);
#        s.root.appendsQueue(rows[['experiment_id','set_id']]);

    def _ba_queueall(s, e):
        lpesids = \
            s.wgrid.widget('treebox').var[['experiment_id','set_id']].copy();
        lpesids.loc[:,'labbook_id']=s.labbook.id;
        lpesids.loc[:,'protocol_id']=s.protocol.PROTOCOLID;
        s.root.appendsQueue(lpesids);
#        s.root.appendsQueue(seids);


    def close(s):
        s.destroy();
        s.root.focus_force();
################################################################################
class exportQueueSpreadSheetWindow(tk.Toplevel):
    def __init__(s, root, handle={}):
        tk.Toplevel.__init__(s);
        s.root = root;
        s.handle = handle;
        s.padder = ttk.Frame(s);
        s.padder.pack(fill='both', expand=True);
        s.container = ttk.Frame(s.padder);
        s.container.pack(fill='both', expand=True, padx=20, pady=20);
        s.wgrid = widgetGrid(s.container, spec(name='grid'));
        s.egrid = widgetGrid(s.wgrid, spec(name='egrid'));
        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));
        s.specs = {};

        default_destination = os.path.join(plbRoot,'exports');
        if not core.ispath(default_destination):
            default_destination="";

        s.specs['l.format'] = spec(name='l.format',
            widgetClass=ttk.Label, default='Format',
            packKWA={});
        s.specs['l.destination'] = spec(name='l.destination',
            widgetClass=ttk.Label, default='Destination',
            packKWA={});
        s.specs['l.reclimit'] = spec(name='l.reclimit',
            widgetClass=ttk.Label, default='Record limit',
            packKWA={});
        s.specs['l.separate'] = spec(name='l.separate',
            widgetClass=ttk.Label, default='Separate experiments',
            packKWA={});
        s.specs['l.ignoredups'] = spec(name='l.ignoredups',
            widgetClass=ttk.Label, default='Ignore duplicate experiment ids',
            packKWA={});
        s.specs['e.format'] = spec(name='e.format',
            widgetClass=ttk.Combobox, default='xlsx',
            options=['xlsx','csv'],
            createKWA={'state':'readonly'},
            packKWA={});
        s.specs['e.destination'] = spec(name='e.destination',
            widgetClass=ttk.Entry, default=default_destination,
            packKWA={});
        s.specs['e.reclimit'] = spec(name='e.reclimit',
            widgetClass=ttk.Entry, default='100000',
            packKWA={});
        s.specs['b.destination'] = spec(name='b.destination',
            widgetClass=ttk.Button, label='Choose',
            packKWA={});
        s.specs['e.separate'] = spec(name='e.separate',
            widgetClass=ttk.Checkbutton, default=False,
            packKWA={'anchor':'w'});
        s.specs['e.ignoredups'] = spec(name='e.ignoredups',
            widgetClass=ttk.Checkbutton, default=False,
            packKWA={'anchor':'w'});
        s.specs['b.cancel'] = spec(name='b.cancel',
            widgetClass=ttk.Button, label="Cancel",
            packKWA={});
        s.specs['b.ok'] = spec(name='b.ok',
            widgetClass=ttk.Button, label="OK",
            packKWA={});


        s.egrid.make(0, 0, s.specs['l.format'], packKWA={'sticky':'e'});
        s.egrid.make(1, 0, s.specs['e.format'], packKWA={'sticky':'w'});
        s.egrid.make(0, 1, s.specs['l.destination'], packKWA={'sticky':'e'});
        s.egrid.make(1, 1, s.specs['e.destination'], packKWA={'sticky':'w'});
        s.egrid.make(2, 1, s.specs['b.destination'], packKWA={'sticky':'e'});
        s.egrid.make(0, 2, s.specs['l.reclimit'], packKWA={'sticky':'e'});
        s.egrid.make(1, 2, s.specs['e.reclimit'], packKWA={'sticky':'w'});
        # s.egrid.make(0, 3, s.specs['l.separate'], packKWA={'sticky':'e'});
        # s.egrid.make(1, 3, s.specs['e.separate'], packKWA={'sticky':'w'});
        # s.egrid.make(0, 3, s.specs['l.ignoredups'], packKWA={'sticky':'e'});
        # s.egrid.make(1, 3, s.specs['e.ignoredups'], packKWA={'sticky':'w'});

        s.egrid.packWidgets();

        s.bgrid.make(0, 0, s.specs['b.cancel']);
        s.bgrid.make(1, 0, s.specs['b.ok']);
        s.bgrid.packWidgets();

        s.wgrid.add(0, 0, s.egrid, packKWA={'sticky':'nesw'});
        s.wgrid.add(0, 1, s.bgrid, packKWA={'sticky':'e'});
        s.wgrid.packWidgets();
        s.wgrid.pack();

        s.bgrid.widget('b.cancel').obj.bind('<Button-1>', s._ba_cancel);
        s.bgrid.widget('b.ok').obj.bind('<Button-1>', s._ba_ok);
        s.egrid.widget('b.destination').obj.bind('<Button-1>', s._ba_destination);

    def _ba_destination(s, e):
        s.egrid.widget('e.destination').var.set(
            filedialog.askdirectory(
                title="Folder to export to",
                initialdir=os.path.join(plbRoot,'exports'),
            )
        );

    def _ba_ok(s, e):
        # load into handle
        s.handle['format'] = s.egrid.widget('e.format').var.get();
        s.handle['destination'] = s.egrid.widget('e.destination').var.get();
        # s.handle['separate'] = s.egrid.widget('e.separate').var.get();
        s.handle['separate'] = False; # option removed
        s.handle['ignoredups'] = False; # option removed
        s.handle['reclimit'] = s.egrid.widget('e.reclimit').var.get();
        try: s.handle['reclimit']=int(s.handle['reclimit']);
        except:
            messagebox.showerror("Error","Record limit must be an integer value");
            return False;
        if s.handle['reclimit']<10:
            messagebox.showerror("Error","The minimum record limit is 10");
            return False;
        if not core.ispath( s.handle['destination'] ):
            messagebox.showerror("Error","Can't find "+s.handle['destination']);
            return False;
        s.release();

    def _ba_cancel(s, e):
        s.release();
        return;

    def release(s):
        s.destroy();
        return;

    def grab(s):
        s.transient(s.root);
        s.grab_set();
        s.root.wait_window(s);


################################################################################
class popup(tk.Toplevel):
    def __init__(s, root,
        handle=dhandle(),
        mspec=spec(name='message', default="Boo!", widgetClass=ttk.Label)
    ):
        tk.Toplevel.__init__(s);
        s.resizable(width=False, height=False);
        s.handle = handle;
        s.root = root;
        s.container = ttk.Frame(s);
        s.container.pack(fill='both', expand=True);
        s.wgrid = widgetGrid(s.container, spec(name='grid'));
        s.wgrid.make(0, 0, mspec, packKWA={});
        s.wgrid.make(0, 1, spec( name='button',
            label="OK", default=True, widgetClass=ttk.Button
        ), packKWA={'padx': 15, 'pady': 15});
        s.wgrid.widget('button').obj.bind('<Button-1>', s.release);
        s.wgrid.packWidgets();
        s.wgrid.pack(padx=30, pady=30);
        s.wgrid.widget('button').focus_force();
        s.bind('<Return>', s.release);

    def grab(s):
        s.transient(s.root);
        s.grab_set();
        s.root.wait_window(s);

    def release(s, e):
        s.handle.value = True;
        s.destroy();
        return;
################################################################################
class popupError(popup):
    def __init__(s, root, message):
        mspec = spec(name='emsg', default=message, widgetClass=ttk.Label,
            style={'style': 'Error.TLabel'},
            packKWA={});
        popup.__init__(s, root, mspec=mspec);
################################################################################
class popupAcknowledgement(popup):
    def __init__(s, root, message):
        mspec = spec(name='emsg', default=message, widgetClass=ttk.Label,
            style={'style': 'Ackno.TLabel'},
            packKWA={});
        popup.__init__(s, root, mspec=mspec);
################################################################################
class popupRowDisplay(tk.Toplevel):
    def __init__(s, root,
        row=pd.Series(),
        titlespec=spec(name='title', default="Title"),
        headerspec=spec(name='header'),
        infospec=spec(name='info')
    ):
        tk.Toplevel.__init__(s, root);
        s.root = root;
        s.resizable(width=False, height=False);
        s.protocol("WM_DELETE_WINDOW", s.close);
        s.filler = ttk.Frame(s);
        s.filler.pack(fill='both', expand=True);
        s.container = ttk.Frame(s.filler);
        s.container.pack(padx=20, pady=20);
        s.wgrid = widgetGrid(s.container, spec(name='wgrid'));


        s.igrid = widgetGrid(s.wgrid, spec(name='igrid'));
        inc = 0;
        for i,v in row.iteritems():
            s.igrid.make(0, inc, headerspec.copy().re(
                name='l.' + str(i),
                createKWA={'style':'Field.TLabel'},
                default=str(i), widgetClass=ttk.Label
            ), packKWA={'sticky':'ne'});
            s.igrid.make(1, inc, infospec.copy().re(
                name='v.' + str(i),
                default=str(v), widgetClass=ttk.Label,
                createKWA={'wraplength': 300},
            ), packKWA={'sticky':'nw'});
            inc += 1;

        s.wgrid.make(0, 0, titlespec.copy().re(widgetClass=ttk.Label));
        s.wgrid.add(0, 1, s.igrid);
        s.wgrid.make(0, 2, spec(name='bok', label="OK",
            widgetClass=ttk.Button));

        s.igrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack();

        s.wgrid.widget('bok').obj.bind('<Button-1>', s._ba_ok);
        s.bind('<Return>', s.close);

    def grab(s):
        s.bind('<Return>', s._ba_ok);
        s.bind('<Escape>', s._ba_ok);
        s.transient(s.root);
        s.grab_set();
        s.root.wait_window(s);

    def show(s):
        return;

    def _ba_ok(s, e):
        s.close();

    def close(s):
        s.destroy();
        s.root.focus_force();
        return;
################################################################################
class popupEntry(tk.Toplevel):
    def __init__(s,root,mspec,espec,validator=lambda x: True):
        tk.Toplevel.__init__(s, root);
        s.root = root;
        s.validator = validator;
        s.fillframe = ttk.Frame(s);
        s.fillframe.pack(fill='both', expand=True);
        s.container = ttk.Frame(s.fillframe);
        s.container.pack(padx=20, pady=20);
        s.wgrid = widgetGrid(s.container,spec(name='wgrid'));
        s.specs = {
            'message': mspec.copy().re(widgetClass=ttk.Label),
            'entry': espec.copy().re(widgetClass=ttk.Entry),
        };

        s.make_specs();
        s.build();

    def make_specs(s):
        s.specs['label'] = spec(name='label', widgetClass=ttk.Label);
        s.specs['response'] = spec(name='response', widgetClass=ttk.Label,
            style={'font':'arial 11'}, default='');
        s.specs['okbutton'] = spec(name='okbutton', widgetClass=ttk.Button,
            label="OK");
        s.specs['cancelbutton'] = spec(name='cancelbutton',
            widgetClass=ttk.Button, label="Cancel");
        return;

    def build(s):
        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));
        s.bgrid.make(0, 0, s.specs['okbutton']);
        s.bgrid.make(1, 0, s.specs['cancelbutton']);

        s.wgrid.make(0, 0, s.specs['message']);
        s.wgrid.make(0, 1, s.specs['entry']);
        s.wgrid.make(0, 2, s.specs['response']);

        s.wgrid.add(0, 3, s.bgrid, packKWA={'sticky':'e'});

        s.bgrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack();

        s.bgrid.widget('okbutton').obj.bind('<Button-1>', s._ba_ok);
        s.bgrid.widget('cancelbutton').obj.bind('<Button-1>', s._ba_cancel);

        s.bind('<Return>', s._ba_ok);
        s.bind('<Escape>', s._ba_cancel);

    def grab(s):
        s.transient(s.root);
        s.grab_set();
        s.wgrid.widget('entry').obj.focus_set();
        s.root.wait_window(s);

    def _ba_cancel(s, e):
        s.destroy();
        s.root.focus_force();
        return False;

    def _ba_ok(s, e):
        if s.validator( s.wgrid.widget('entry').var.get() ):
            s.destroy();
            s.root.focus_force();
            if s.root.initializeExperiment(
                s.wgrid.widget('entry').var.get()
            ):
                s.destroy();
                s.root.focus_force();
                return True;
            else:
                return;
        else:
            messagebox.showerror("Error","Invalid id.  Only A-Z, a-z, 0-9, "+
                "_, and - characters are allowed.");
        return;
################################################################################
################################################################################
################################################################################
class queuePane(ttk.Frame):
    def __init__(s, master, aspec, root=None):
        ttk.Frame.__init__(s, master);
        s.spec = aspec;
        s.root = root;
        s.selectedbook = tk.StringVar(value="");

        s.wgrid = widgetGrid(s, spec(name='wgrid'));    # master
        s.bgrid = widgetGrid(s.wgrid, spec(name='bgrid'));  # buttons
        s.hgrid = widgetGrid(s.wgrid, spec(name='hgrid'));  # headers

        # columns
        s.columnspecs = [
            spec(name='labbook_id', label='labbook_id', width=100),
            spec(name='protocol_id', label='protocol_id', width=100),
            spec(name='experiment_id', label='experiment_id', width=100),
            spec(name='set_id', label='set_id', width=100),
            spec(name='status', label='status', width=70),
        ];

        # make treebox
        s.obj = treeBox(s.wgrid, spec(name='treebox', createKWA={'height':16}),
            columnspecs=s.columnspecs, xscroll=False, yscroll=True);
        # basic specs
        s.specs = {};
        # header
        s.specs['header'] = spec(name='header', default='Queue',
            widgetClass=ttk.Label, createKWA={'style':'PaneHeader.TLabel'},
            packKWA={'padx': 5, 'pady': 5});
        s.specs['selectedbook'] = spec(name='selectedbook', default='',
            widgetClass=ttk.Label,
            variable=s.selectedbook,
            createKWA={'style':'Selected.TLabel'});
        # buttons
        bsty={'width':3};
        s.specs['b.selectlb'] = spec(name='b.selectlb', label='\u25C9',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.clear'] = spec(name='b.clear', label='\u2715',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.importdb'] = spec(name='b.importdb', label='\u2219\u21E6',
            style=bsty, widgetClass=ttk.Button);
        # s.specs['b.importre'] = spec(name='b.importre', label='\u21E9R',
        #     style=bsty, widgetClass=ttk.Button);
        s.specs['b.exportsheets'] = spec(name='b.exportsheets', label='\u21F2',
            style=bsty, widgetClass=ttk.Button);
        s.specs['b.remove'] = spec(name='b.remove', label='\u2716',
            style=bsty, widgetClass=ttk.Button);

        # make headers
        s.hgrid.make(0, 0, s.specs['header'], packKWA={'sticky':'w'});
        s.hgrid.make(1, 0, s.specs['selectedbook'],
            packKWA={'sticky':'e','padx':1});

        # make buttons in bgrid
        s.bgrid.make(0, 0, s.specs['b.selectlb']);
        s.bgrid.make(1, 0, s.specs['b.clear']);
        s.bgrid.make(2, 0, s.specs['b.importdb']);
        # s.bgrid.make(3, 0, s.specs['b.importre']);
        s.bgrid.make(3, 0, s.specs['b.exportsheets']);
        s.bgrid.make(4, 0, s.specs['b.remove']);
        # header
        s.wgrid.add(0, 0, s.hgrid, packKWA={'sticky':'ew'});
        # treebox
        s.wgrid.add(0, 1, s.obj);
        # buttons
        s.wgrid.add(0, 2, s.bgrid);

        s.hgrid.packWidgets();
        s.bgrid.packWidgets();
        s.wgrid.packWidgets();
        s.wgrid.pack();

#        s.obj = s.wgrid.widget('treebox');
#        s.var = s.wgrid.widget('treebox').var;

        s.bgrid.widget('b.selectlb').obj.bind('<Button-1>',
            s._ba_selectLabbook);
        s.bgrid.widget('b.clear').obj.bind('<Button-1>', s._ba_clear);
        s.bgrid.widget('b.importdb').obj.bind('<Button-1>', s._ba_importdb);
        # s.bgrid.widget('b.importre').obj.bind('<Button-1>', s._ba_importre);
        s.bgrid.widget('b.exportsheets').obj.bind('<Button-1>', s._ba_exportsheets);
        s.bgrid.widget('b.remove').obj.bind('<Button-1>', s._ba_remove);

    def _ba_selectLabbook(s, e):
        s.root.selectQueueLabbook();

    def _ba_exportsheets(s, e):
        s.root.queueExportSpreadSheets();
        return;

    def _ba_remove(s, e):
        items = s.obj.obj.selection();
        for item in items: s.obj.delete(item);
        return;

    def _ba_clear(s, e):
        s.wgrid.widget('treebox').clearAll();

    def _ba_importdb(s, e):
        s.root.queueImportDB();
        return;

    def _ba_importre(s, e):
        return;

    def _selectedItemID(s):
        sel = s.wgrid.widget('treebox').selected();
        if sel=='': return None;
        return s.wgrid.widget('treebox').row(sel)['id'];

    def getVar(s):
        return s.wgrid.widget('treebox').var;

    def append(s, lbid, pid, eid, sid):
        s.wgrid.widget('treebox').append([lbid, pid, eid, sid]);
################################################################################
################################################################################
################################################################################
class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    # from ttps://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self);
        # Store a reference to the Text it will log to
        self.text = text;

    def emit(self, record):
        msg = self.format(record);
        def append():
            self.text.configure(state='normal');
            self.text.insert(tk.END, msg + '\n');
            self.text.configure(state='disabled');
            # Autoscroll to the bottom
            self.text.yview(tk.END);
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append);
################################################################################
################################################################################
class progressWindow(tk.Toplevel):
    def __init__(s, root):
        tk.Toplevel.__init__(s);
        s.root = root;
        s.padder = ttk.Frame(s);
        s.padder.pack(fill='both', expand=True);
        s.container = ttk.Frame(s.padder);
        s.container.pack(fill='both', expand=True, padx=20, pady=20);
        s.wgrid = widgetGrid(s.container, spec(name='wgrid'));
        s.specs = {};
        s.specs['l.info'] = spec(name='l.info', default='test',
            widgetClass=ttk.Label, packKWA={},
            createKWA={'wraplength':250},
            style={'font':'arial 11'});
        s.specs['p.bar'] = spec(name='p.bar',
            widgetClass=ttk.Progressbar,
            createKWA={'length': 250},
            packKWA={});


        s.wgrid.make(0, 0, s.specs['p.bar'], packKWA={});
        s.wgrid.make(0, 1, s.specs['l.info'], packKWA={});
        s.wgrid.packWidgets();
        s.wgrid.pack();

        s.obj = s.wgrid.widget('p.bar').obj;
        s.var = s.wgrid.widget('l.info').var;

    def grab(s):
        s.transient(s.root);
        s.grab_set();
        s.root.wait_window(s);
        return s;

    def release(s):
        s.destroy();
        return;
################################################################################
