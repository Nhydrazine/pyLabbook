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
output_folder = os.path.join(myroot,"model_k1all");
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
# EQN 5 MVC ------------------------------------------------------------------ #
model_mvc_eq5 = fitModels.model();
def cor_k(t, k0, k1):
	# Eqn. 5
	return (
		1 - (
			( (k1*np.exp(-k0*t)) - (k0*np.exp(-k1*t)) ) /
			(k1 - k0)
		)
	);
def cor_r(t, k0, a):
	# allows k1, k0 relation constraints by expressing as ratio:
	# k1 = a*k0
	# F = 1-( (a*exp(-k0*t) - exp(-a*k0*t)) / (a-1) )
	return (
		1 - (
			( (a*np.exp(-k0*t)) - np.exp(-a*k0*t)) /
			(a-1)
		)
	);
model_mvc_eq5.equation = cor_r;
model_mvc_eq5.params = pd.Series({'k0': np.nan, 'a': np.nan});
# EQN 5 T20 ------------------------------------------------------------------ #
model_t20_eq5 = fitModels.model();
model_t20_eq5.equation = cor_r;
model_t20_eq5.params = pd.Series({'k0': np.nan, 'a': np.nan});
# EQN 8 T20 ------------------------------------------------------------------ #
model_t20_eq8 = fitModels.model();
def tfit_eqn8(t,k2,k0,k1):
	return (
		1 - (
			( k0*k2*np.exp(-k1*t) )/( (k1-k0)*(k1-k2) ) -
			( k1*k2*np.exp(-k0*t) )/( (k0-k1)*(k0-k2) ) -
			( k0*k1*np.exp(-k2*t) )/( (k2-k0)*(k2-k1) )
		)
	);
model_t20_eq8.equation = tfit_eqn8;
model_t20_eq8.params = pd.Series({'k2':np.nan,'k0':np.nan,'k1':np.nan});
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
    try:
        mvc_results, mvc_r2 = model_mvc_eq5.fit(
            mvc_fit_sams['_time'],
            mvc_fit_sams['_bnorm_avg'],
            model_mvc_eq5.params.copy(),
            curve_fit_kwargs = {
                'p0': [1,0.99],
                'bounds': ((0,0),(np.inf,np.inf)),
            }
        );
    except Exception as e:
        print(pairid + ": " + str(e));
        summary.append(result_set);
        continue;
    # mvc_delay = np.exp(np.subtract(
    #     np.log(mvc_results['u']),
    #     (mvc_results['s']**2)
    # ));
    result_set['mvc_k0'] = mvc_results['k0'];
    result_set['mvc_a'] = mvc_results['a'];
    result_set['mvc_k1'] = result_set['mvc_k0']*result_set['mvc_a'];
    result_set['mvc_r2'] = mvc_r2;
    mvc_predict = model_mvc_eq5.predict(
        xpoints,
        *mvc_results
    );
    # fit t20
    t20_fit_sams = t20_sams[~t20_sams['sample_id'].isin(['INFTY'])];
    t20_fitparams = model_t20_eq5.params.copy();
    try:
        t20_results, t20_r2 = model_t20_eq5.fit(
            t20_fit_sams['_time'],
            t20_fit_sams['_bnorm_avg'],
            t20_fitparams,
            curve_fit_kwargs = {
                'p0': [1,0.99],
                'bounds': ((0,0),(np.inf,np.inf)),
            }
        );
    except Exception as e:
        print(pairid + ": " + str(e));
        summary.append(result_set);
        continue;

    result_set['t20_k0'] = t20_results['k0'];
    result_set['t20_a'] = t20_results['a'];
    result_set['t20_k1'] = result_set['t20_k0']*result_set['t20_a'];
    result_set['t20_r2'] = t20_r2;
    t20_predict = model_mvc_eq5.predict(
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
                "mvc_k0: "+str(np.round(result_set['mvc_k0'],4)),
                "mvc_k1: "+str(np.round(result_set['mvc_k1'],4)),
                "mvc_r2: "+str(np.round(result_set['mvc_r2'],4)),
                "t20_k0: "+str(np.round(result_set['t20_k0'],4)),
                "t20_k1: "+str(np.round(result_set['t20_k1'],4)),
                "t20_r2: "+str(np.round(result_set['t20_r2'],4)),
                # "mvc delay: "+str(np.round(mvc_delay,2))+" ("+str(np.round(mvc_r2,4))+")",
                # "t20 delay: "+str(np.round(t20_delay,2))+" ("+str(np.round(t20_r2,4))+")",
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
