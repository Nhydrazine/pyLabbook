################################################################################
import sys, os, re;
import numpy as np, pandas as pd;
import matplotlib.pyplot as plt;
import matplotlib as mpl;
from nicMods.graphing import plotPage;
from scipy.stats import lognorm;
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
output_folder = os.path.join(myroot,"model_lognormal");
if not os.path.isdir(output_folder):
    os.mkdir(output_folder);
################################################################################
# instantiate labbook and protocol
lb = plbCore.import_initialize_labbook('AldrovandiLab', plbRoot);
pr = plbCore.import_initialize_protocol('TOAD96W', lb);
################################################################################
# load data
datafile = os.path.join(myroot,"simuldata_workup.xlsx");
xl = pd.ExcelFile(datafile);
paired = xl.parse('paired', index=None);
sets = xl.parse('sets', index=None);
sams = xl.parse('sams', index=None);
xl.close();
################################################################################
# subset for plotting/fitting
# paired = paired[paired['env']=='B24731_XPD_704'];
# use_esids = [];
# for elist in paired['esid_list']: use_esids += elist.split(',');
# sets = sets[sets['_esid'].isin(use_esids)];
# sams = sams[sams['_esid'].isin(use_esids)];
################################################################################
styles = {
    't20_scatter': {
        'color'     : 'blue',
        'alpha'     : 0.6,
        's'         : 25,
        'marker'    : 'o',
    },
    'mvc_scatter': {
        'color'     : 'red',
        'alpha'     : 0.6,
        's'         : 25,
        'marker'    : 'o',
    },
    'mvc_predict': {
        'color'     : 'red',
    },
    't20_predict': {
        'color'     : 'blue',
    },
    'erb': {
        'capsize'   : 3,
        'color'     : '#000000',
        'fmt'       : '|',
        'alpha'     : 0.3,
    },
};
################################################################################
# setup model(s)
xpoints = np.linspace(0,130,200);
# LOGNORMAL CDF -------------------------------------------------------------- #
model_lognorm = fitModels.model();
def ln_cdf_ne(x,u,s): return lognorm.cdf(x, s, scale=u);
model_lognorm.equation = ln_cdf_ne;
model_lognorm.params = pd.Series({'u':np.nan, 's':np.nan});

################################################################################
# plot
summary = [];
for pairid in paired['pairid'].unique():
    # sets
    ss_sets = sets[sets['pairid']==pairid];
    if len(ss_sets)!=2:
        raise Exception(pairid + " doesn't have exactly 2 sets");
    mvc_set = ss_sets[ss_sets['inhibitor_id']=='MVC'].iloc[0];
    t20_set = ss_sets[ss_sets['inhibitor_id']=='T20'].iloc[0];
    result_set = mvc_set[['experiment_id','pairid','env','pseudo_id']].copy();
    # samples
    mvc_sams = sams[sams['esid']==mvc_set['esid']];
    t20_sams = sams[sams['esid']==t20_set['esid']];
    # fit MVC
    mvc_fit_sams = mvc_sams[~mvc_sams['sample_id'].isin(['INFTY'])];
    mvc_results, mvc_r2 = model_lognorm.fit(
        mvc_fit_sams['_time'],
        mvc_fit_sams['_bnorm_avg'],
        model_lognorm.params.copy()
    );
    mvc_delay = np.exp(np.subtract(
        np.log(mvc_results['u']),
        (mvc_results['s']**2)
    ));
    result_set['mvc_u'] = mvc_results['u'];
    result_set['mvc_s'] = mvc_results['s'];
    result_set['mvc_delay'] = mvc_delay;
    result_set['mvc_r2'] = mvc_r2;
    mvc_predict = model_lognorm.predict(
        xpoints,
        *mvc_results
    );
    # fit t20
    t20_fit_sams = t20_sams[~t20_sams['sample_id'].isin(['INFTY'])];
    t20_results, t20_r2 = model_lognorm.fit(
        t20_fit_sams['_time'],
        t20_fit_sams['_bnorm_avg'],
        model_lognorm.params.copy()
    );
    t20_delay = np.exp(np.subtract(
        np.log(t20_results['u']),
        (t20_results['s']**2)
    ));
    result_set['t20_u'] = t20_results['u'];
    result_set['t20_s'] = t20_results['s'];
    result_set['t20_delay'] = t20_delay;
    result_set['t20_r2'] = t20_r2;
    t20_predict = model_lognorm.predict(
        xpoints,
        *t20_results
    );
    # plot
    fig, ax = plt.subplots(ncols=1, nrows=1);
    ax.set_ylim(-0.1,1.1);
    ax.set_xlim(0,130);
    ax.set_xlabel("time (min)");
    ax.set_ylabel("infection (%, baseline)");
    mvc_plot = mvc_sams[
        ~mvc_sams['sample_id'].isin(['INFTY'])
    ].sort_values(by='_time');
    t20_plot = t20_sams[
        ~t20_sams['sample_id'].isin(['INFTY'])
    ].sort_values(by='_time');
    ax.scatter(
        mvc_plot['_time'],
        mvc_plot['_bnorm_avg'],
        **styles['mvc_scatter'],
    );
    ax.plot(
        xpoints,
        mvc_predict,
        **styles['mvc_predict'],
    );
    ax.plot(
        xpoints,
        t20_predict,
        **styles['t20_predict'],
    );

    ax.scatter(
        t20_plot['_time'],
        t20_plot['_bnorm_avg'],
        **styles['t20_scatter'],
    );
    ax.errorbar(
        mvc_plot['_time'],
        mvc_plot['_bnorm_avg'],
        mvc_plot['_bnorm_std'],
        **styles['erb'],
    );
    ax.errorbar(
        t20_plot['_time'],
        t20_plot['_bnorm_avg'],
        t20_plot['_bnorm_std'],
        **styles['erb'],
    );
    ax.text(1,1.08,
        str(
            "\n".join([
                pairid,
                t20_set['env']+"("+t20_set['pseudo_id']+")",
                "mvc delay: "+str(np.round(mvc_delay,2))+" ("+str(np.round(mvc_r2,4))+")",
                "t20 delay: "+str(np.round(t20_delay,2))+" ("+str(np.round(t20_r2,4))+")",
            ])
        ),
        verticalalignment="top",
        horizontalalignment="left",
    );
    summary.append(result_set);
    plotfile = pairid + ".pdf";
    plot_outputfile = os.path.join(output_folder, plotfile);
    print("writing to "+plot_outputfile);
    plt.savefig(plot_outputfile);
    plt.close();
summary = pd.DataFrame(summary);
outfile = os.path.join(output_folder, "summary.xlsx");
print("writing to "+outfile);
xw = pd.ExcelWriter(outfile);
summary.to_excel(xw,'summary',index=False);
paired.to_excel(xw,'paired',index=False);
sets.to_excel(xw,'sets',index=False);
sams.to_excel(xw,'sams',index=False);
xw.save();
xw.close();
print("done");












#
