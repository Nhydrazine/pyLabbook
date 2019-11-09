"""
pyLabbook protocol module for time of addition kinetics assay
Author: Nicholas E. Webb

This module is intended to be run from the pyLabbook data management system.

PROTOCOL DEFINITIONS
--------------------
    EXPERIMENT
        A single run of the protocol consisting of any number of 96-well
        plates with 5 kinetic curves (SETS) per plate.  Experiments are coded
        by date in YYYYMMDD format with suffixes to distinguish multiple
        experiments run on the same day.
    SET
        A single kinetic curve consisting of independent duplicates of 8 time
        points (ZERO, T1, T2, T3, T4, T5, T6, INFTY) and a cell background
        (C).  Sets are coded by P[PLATE NO]V[VIRUS NO].
    SAMPLE
        A single measurement of infectivity via. 'reporter' for a SET.

"""
from pyLabbook import pyProtocol;
import sys, math;
import numpy as np, pandas as pd;
from scipy.optimize import curve_fit;
from scipy.stats import lognorm, norm;
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
class initialize(pyProtocol): ##################################################
    def setup(s):
        s.PROTOCOLID = "TOAD96W";
        s.addSetColumn(
            name        = "source_file",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "name of raw data file",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "source_sheet",
            type        = "TEXT",
            notnull     = False,
            unique      = False,
            description = "name of raw data sheet",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "platemap",
            type        = "TEXT",
            notnull     = False,
            unique      = False,
            description = "platemap used for data extraction if applicable",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "env",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "name of virus",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "pseudo_id",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "id of virus batch",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "pseudo_x",
            type        = "REAL",
            notnull     = True,
            unique      = False,
            description = "final concentration of virus stock (X)",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "inhibitor_name",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "name of inhibitor used",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "inhibitor_id",
            type        = "TEXT",
            notnull     = False,
            unique      = False,
            description = "id of inhibitor where applicable",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "inhibitor_conc",
            type        = "REAL",
            notnull     = True,
            unique      = False,
            description = "final concentration of inhibitor",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "inhibitor_conc_units",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "units of inhibitor concentration",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "timepoints",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "semicolon separated list of differential time points starting with 0",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "cell_type",
            type        = "TEXT",
            notnull     = False,
            unique      = False,
            description = "cell type used",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "temperature",
            type        = "REAL",
            notnull     = True,
            unique      = False,
            description = "temperature in celsius during time course",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "reporter",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "name of infectivity reporter",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "read_type",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "infectivity reporter read type",
            default     = None,
            primary_key = False,
        );
        s.addSetColumn(
            name        = "notes",
            type        = "TEXT",
            notnull     = False,
            unique      = False,
            description = "notes",
            default     = None,
            primary_key = False,
        );
        s.addSamColumn(
            name        = "time_id",
            type        = "INTEGER",
            notnull     = True,
            unique      = False,
            description = "time position number",
            default     = None,
            primary_key = False,
        );
        s.addSamColumn(
            name        = "type",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "sample type (INFTY, ZERO, T1...Tn)",
            default     = None,
            primary_key = False,
        );
        s.addSamColumn(
            name        = "value",
            type        = "TEXT",
            notnull     = True,
            unique      = False,
            description = "measured infectivity value",
            default     = None,
            primary_key = False,
        );
        #----------------------------------------------------------------------#
        # ansi color definitions for verbose outputs
        class ansi:
            red         = "\033[0;31m";
            green       = "\033[0;32m";
            clear       = "\033[0m";
        s.ansi = ansi();
    ############################################################################
    # SAMPLE DATA PROCESSING AND WORKUP ########################################
    ############################################################################
    def workup(s, sets, sams, varianceFormula=False, verbose=False):
        """Interface for data workup and associated options.

        Parameters
        ----------
        sets : pandas.DataFrame
            Set data to workup.
        sams : pandas.DataFrame
            Associated sample data to workup.
        varianceFormula : bool
            Use variance formula to propagate error (True) or use avg/stdev of
            individually worked-up replicates (False).  Uses
            s.workup_varianceFormula() or s.workup_noVarianceFormula()
            accordingly.

        Returns
        -------
        (pandas.DataFrame, pandas.DataFrame)
            Tuple of (sets, sams) pandas.DataFrames that include the following
            additional set columns with calculated values:
                _baseline_avg
                    average baseline (% infection at time ZERO).

                _baseline_std
                    stdev baseline (% infection at time ZERO).

                _rebase
                    rebase factor to convert from ZERO baselined to CELL
                    basedlined.

            and the following additional sample columns:
                _time
                    time point, in minutes, from initiation.

                _raw_avg, _raw_std
                    average and stdev of raw infectivity signal level.

                _sub_avg, _sub_std
                    average and stdev of background subtracted infectivity
                    signal.

                _norm_avg, _norm_std
                    average and stdev of normalized (to INFTY) infectivity.

                _bnorm_avg, _bnorm_std
                    average and stdev of baselined infectivity, bound by ZERO
                    and INFTY (so C background is no longer 0).

        Notes
        -----
            rebasing
                Rebasing is the conversion of % infection from a range that goes
                from sample C to sample INFTY, to a range that goes from sample
                ZERO to INFTY.  C to INFTY is 'background normalized' while
                ZERO to INFTY is baselined, so that the time zero point is
                0% infection.  This is needed for processes like lognormal CDF
                fitting, which expects the time zero first data point to have
                0% infection.

                Conversion between these ranges is given by the rebase formula:

                    Fac = Fab * rebase + baseline

                where

                    > Fac is % infection for the C -> INFTY range (subtracted)
                    > Fab is % infection for the ZERO -> INFTY range (baselined)
                    > basline is the subtracted % infection of ZERO sample
                    (also called the baseline infectivity)

                    > rebase is a conversion factor calculated from raw signal
                    levels of the INFTY, ZERO and C samples:

                        rebase = (INFTY - ZERO)/(INFTY - C)

                Most often, rebase ~ 1 meaning that the subtracted range and the
                baselined range are nearly the same.  This also coincides with
                the normalized % infection of sample ZERO being very close to
                0%, indicating a nearly perfect baseline infectivity.

            standard deviation
                Please note that there are differences in the default behavior
                of numpy and pandas in terms of whether degrees of freedom is N
                (population) or N-1 (sample of population), when calculating
                standard deviation.  This module always explicitly uses the N-1
                setting.

        """
        if varianceFormula:
            return s.workup_varianceFormula(sets, sams, verbose);
        else:
            return s.workup_noVarianceFormula(sets, sams, verbose);
    #--------------------------------------------------------------------------#
    def workup_noVarianceFormula(s, sets, sams, verbose=False):
        """Works up data points to subtracted, normalized and baselined values.
        Calculates average/stdev of data after working up instead of using
        variance formula.  This tends to give smaller error estimates.
        Conforms to argument/return specifications of s.workup().

        """
        sets = sets.copy();
        sams = sams.copy();
        # cast as float for calculations
        sams['value'] = sams['value'].astype(float);
        # generate compound keys for processing loops
        # experiment.set
        sets['_esid'] = \
            sets['experiment_id'].astype(str)+'.'+\
            sets['set_id'].astype(str);
        sams['_esid'] = \
            sams['experiment_id'].astype(str)+'.'+\
            sams['set_id'].astype(str);
        # experiment.set.sample
        sams['_essid'] = sams['_esid'].astype(str)+'.'+\
            sams['sample_id'].astype(str);
        # experiment.set.sample.replicate
        sams['_esrid'] = \
            sams['_esid'].astype(str)+'.'+\
            sams['replicate'].astype(str); # for replicates
        # initialize columns that will contain calculated values
        set_cols = [
            '_baseline_avg','_baseline_std', # % infection at time zero
            '_rebase' # baseline conversion factor
        ];
        sam_cols = [
                # set derived data
                '_time',    # time point
                # calculated values
                '_raw_avg', '_raw_std', # raw signal value (infectivity)
                '_sub_avg', '_sub_std', # subtracted
                '_norm_avg', '_norm_std', # normalized
                '_bnorm_avg', '_bnorm_std' # baselined (t0 = 0% infection)
        ];
        # initialize columns with np.nan so NULL is clearly defined
        for c in set_cols: sets[c] = np.nan;
        for c in sam_cols: sams[c] = np.nan;
        sams['_raw_avg'] = sams['value'];
        # calculate individual replicates
        for esid in sets['_esid']: # for every experiment set (e.g. curve)
            if verbose: print("working "+str(esid)+": ", end='', flush=True);
            # get set information for this experiment set
            r = sets[sets['_esid']==esid].iloc[0].copy();
            # get samples for this experiment set
            samss = sams[sams['_esid']==esid];
            # split time points from semicolon delimted to array-like Series
            tpoints = pd.Series(str(r['timepoints']).split(';')).astype(float);
            # add appropriate time point values to samples by aligning time_id
            # with tpoints index
            sams.loc[ samss.index,'_time' ] = \
                list(tpoints[ list(samss['time_id']) ] );
            # process individual replicate sample curves for this set
            for esrid in samss['_esrid'].unique(): #for each replicate
                # subset samples
                ss = sams[sams['_esrid']==esrid].copy();
                # subtract background
                bg = ss[ss['sample_id']=='C'].iloc[0];
                sams.loc[ ss.index,'_sub_avg' ] = ss['value'] - bg['value'];
                # normalize
                ss = sams[sams['_esrid']==esrid].copy();
                norm = ss[ss['sample_id']=='INFTY'].iloc[0];
                sams.loc[ ss.index,'_norm_avg' ] = \
                    ss['_sub_avg'] / norm['_sub_avg'];
                # baseline
                ss = sams[sams['_esrid']==esrid].copy();
                base = ss[ss['sample_id']=='ZERO'].iloc[0];
                norm = ss[ss['sample_id']=='INFTY'].iloc[0];
                sams.loc[ ss.index,'_bnorm_avg' ] = (
                    (sams['_raw_avg'] - base['_raw_avg']) /
                    (norm['_raw_avg'] - base['_raw_avg'])
                );
            if verbose: print(s.ansi.green+"OK"+s.ansi.clear);

        # process avg/std of worked up curve replicates
        reduced_sams = []; # samples with replicates reduced
        for esid in sets['_esid']:
            if verbose: print("averaging "+str(esid)+": ", end='', flush=True);
            samss = sams[sams['_esid']==esid]; # subset
            setss = sets[sets['_esid']==esid].iloc[0]; # subset set row
            # for each sample id
            for sid in samss['sample_id'].unique():
                sidss = samss[samss['sample_id']==sid]; # subset replicates
                srow = sidss.iloc[0].copy(); # copy to new row
                # set avg and std values in new row
                for c in ['_raw','_sub','_norm','_bnorm']:
                    srow[c+'_avg'] = sidss[c+'_avg'].mean();
                    srow[c+'_std'] = sidss[c+'_avg'].std(ddof=1);
                reduced_sams.append(srow); # append
            if verbose: print(s.ansi.green+"OK"+s.ansi.clear);
        # replace
        sams = pd.DataFrame(reduced_sams);

        # one more loop for calculating rebase conversion factors
        for esid in sets['_esid']:
            if verbose:
                print("rebase conversion "+str(esid)+": ", end='', flush=True);
            samss = sams[sams['_esid']==esid]; # subset
            setss = sets[sets['_esid']==esid].iloc[0]; # subset set row
            sets.loc[ setss.name, '_baseline_avg' ] = \
                samss['_norm_avg'][samss['sample_id']=='ZERO'].iloc[0];
            sets.loc[ setss.name, '_baseline_std' ] = \
                samss['_norm_std'][samss['sample_id']=='ZERO'].iloc[0];
            norm = samss[samss['sample_id']=='INFTY'].iloc[0];
            base = samss[samss['sample_id']=='ZERO'].iloc[0];
            cell = samss[samss['sample_id']=='C'].iloc[0];
            sets.loc[ setss.name, '_rebase' ] = (
                (norm['_raw_avg'] - base['_raw_avg']) /
                (norm['_raw_avg'] - cell['_raw_avg'])
            );
            if verbose: print(s.ansi.green+"OK"+s.ansi.clear);
        # format as pandas.DataFrame
        if verbose: print("concatenating: ", end='', flush=True);
        reduced_sams = pd.DataFrame(reduced_sams);
        if verbose: print(s.ansi.green+"OK"+s.ansi.clear);
        # return copies to be safe
        return (sets.copy(), sams.copy());
    #--------------------------------------------------------------------------#
    def workup_varianceFormula(s, sets, sams, verbose):
        """Works up data points to subtracted, normalized and baseline values.
        Calculates average/stdev of data using variance formula to propagate
        error.  This tends to give larger error estimates.  Conforms to
        specifications of s.workup().

        """
        sets = sets.copy();
        sams = sams.copy();
        # generate compound keys for sorting, looping and reducing replicates
        # experiment.set
        sets['_esid'] = \
            sets['experiment_id'].astype(str)+'.'+\
            sets['set_id'].astype(str);
        sams['_esid'] = \
            sams['experiment_id'].astype(str)+'.'+\
            sams['set_id'].astype(str);
        # experiment.set.sample
        sams['_essid'] = sams['_esid'].astype(str)+'.'+\
            sams['sample_id'].astype(str);
        # experiment.set.sample.replicate
        sams['_esrid'] = \
            sams['_esid'].astype(str)+'.'+\
            sams['replicate'].astype(str); # for replicates
        # preserve original column names for clean return
        original_setcols = sets.columns;
        original_samcols = sams.columns;

        # confirm set and samples contain the same data sets
        se_esid = pd.Series(
            sets['_esid'].unique()
        ).sort_values().reset_index(drop=True);
        sa_esid = pd.Series(
            sams['_esid'].unique()
        ).sort_values().reset_index(drop=True);
        if len(sa_esid)!=len(se_esid):
            raise Exception("set and sample dataframes don't have the same "+
                "number of sets");
        if not (se_esid==sa_esid).all():
            raise Exception("set and sample dataframes don't match");
        # cast as float for calculations
        sams['value'] = sams['value'].astype(float);
        # reduce sample replicates using compound key -------------------------#
        sams_reduced = [];
        all_essids = sams['_essid'].unique();
        ten_percent = int(len(all_essids)/100);
        if verbose:
            print("reducing replicates: ", end='', flush=True);
            if len(all_essids)>150:
                print("    ", end='', flush=True);
        for i,essid in enumerate(all_essids):
            if verbose:
                if len(all_essids)>150:
                    if (i%ten_percent)==0:
                        dpercent = int((i/len(all_essids))*100)
                        print("\b\b\b\b", end='', flush=True);
                        print(
                                s.ansi.green+
                                str(str(dpercent)).rjust(3)+
                                s.ansi.clear+
                                "%",
                            end='', flush=True
                        );
            # subset replicates
            rss = sams[sams['_essid']==essid];
            # copy first row
            row = rss.iloc[0].copy();
            # average and stdev the replicates
            try: row['_raw_avg'] = rss['value'].mean();
            except:
                row['_raw_avg'] = np.nan;
                row['_raw_std'] = np.nan;
                continue; # skip
            try: row['_raw_std'] = rss['value'].std(ddof=1);
            except:
                row['_raw_std'] = np.nan;
            sams_reduced.append(row);
        if verbose:
            if len(all_essids)>150:
                print("\b\b\b\b", end='', flush=True);
            print(s.ansi.green+"OK     "+s.ansi.clear);
        sams = pd.DataFrame(sams_reduced); #-----------------------------------#
        sams_reduced = []; # free
        # calculated set columns
        set_cols = ['_baseline_avg','_baseline_std','_rebase'];
        # calculated sample columns
        sam_cols = [
                # set derived data
                '_time',    # time point
                # calculated values
                '_sub_avg', '_sub_std', '_sub_cv',   # subtracted
                '_norm_avg', '_norm_std',            # normalized
                '_bsub_avg', '_bsub_std', '_bsub_cv',# zero subtracted
                '_bnorm_avg', '_bnorm_std'           # zero normalized
        ];
        # initialize calculated cols with NaN so NULL is clearly defined
        for c in sam_cols: sams[c] = np.nan;
        for c in set_cols: sets[c] = np.nan;
        # calculate for every distinct experiment_id.set_id
        for esid in sets['_esid'].unique():
            if verbose: print("working "+str(esid)+": ", end='', flush=True);
            ss = sams[sams['_esid']==esid]; # sample subset
            r = sets[sets['_esid']==esid].iloc[0]; # set row
            # process time points
            tpoints = pd.Series(str(r['timepoints']).split(';')).astype(float);
            # use time_id as index of time point value in tpoints
            sams.loc[ss.index, '_time'] = list(tpoints[ list(ss['time_id']) ]);
            # subtract background ---------------------------------------------#
            bg = ss[ss['sample_id']=='C'].iloc[0]; # background row
            sams.loc[ss.index,'_sub_avg'] = \
                ss['_raw_avg'] - bg['_raw_avg'];
            sams.loc[ss.index,'_sub_std'] = \
                np.sqrt(
                    (ss['_raw_std']**2) +
                    (bg['_raw_std']**2)
                );
            sams.loc[ss.index,'_sub_cv'] = \
                sams.loc[ss.index,'_sub_std'] / sams.loc[ss.index,'_sub_avg'];
            # normalize -------------------------------------------------------#
            ss = sams[sams['_esid']==esid]; # updated sample subset
            norm = ss[ss['sample_id']=='INFTY'].iloc[0]; # INFTY row
            # using numpy explicitly here to avoid math typos
            sams.loc[ss.index,'_norm_avg'] = \
                np.divide(ss['_sub_avg'], norm['_sub_avg']);
            sams.loc[ss.index,'_norm_std'] = \
                np.multiply(
                    np.sqrt(
                        (ss['_sub_cv']**2) +
                        (norm['_sub_cv']**2)
                    ),
                    np.divide(ss['_sub_avg'], norm['_sub_avg'])
                );
            # baseline ---------------------------------------------------------
            ss = sams[sams['_esid']==esid]; # updated sample subset
            base = ss[ss['sample_id']=='ZERO'].iloc[0];
            sets.loc[r.name, ['_baseline_avg','_baseline_std']] = \
                list(base[['_norm_avg','_norm_std']]);
            # calculate rebase bfactor (T-B)/(T-C) where:
            # T is max raw signal, B is baseline raw signal (at t0)
            # and C is cell control raw signal.
            sets.loc[r.name,'_rebase'] = \
                np.divide(
                    np.subtract(
                        ss['_raw_avg'][ss['sample_id']=='INFTY'].iloc[0],
                        ss['_raw_avg'][ss['sample_id']=='ZERO'].iloc[0]
                    ),
                    np.subtract(
                        ss['_raw_avg'][ss['sample_id']=='INFTY'].iloc[0],
                        ss['_raw_avg'][ss['sample_id']=='C'].iloc[0]
                    ),
                );
            # baseline subtracted ---------------------------------------------#
            ss = sams[sams['_esid']==esid]; # updated sample subset
            zero = ss[ss['sample_id']=='ZERO'].iloc[0];
            sams.loc[ss.index, '_bsub_avg'] = \
                ss['_raw_avg'] - zero['_raw_avg'];
            ss = sams[sams['_esid']==esid]; # updated sample subset
            sams.loc[ss.index, '_bsub_std'] = \
                np.sqrt(
                    (ss['_raw_std']**2) +
                    (zero['_raw_std']**2)
                );
            sams.loc[ss.index, '_bsub_cv'] = \
                sams.loc[ss.index,'_bsub_std'] / sams.loc[ss.index,'_bsub_avg'];
            # baseline normalized ---------------------------------------------#
            ss = sams[sams['_esid']==esid]; # updated sample subset
            bnorm = ss[ss['sample_id']=='INFTY'].iloc[0]; # INFTY row
            # using numpy explicitly here to avoid math typos
            sams.loc[ss.index,'_bnorm_avg'] = \
                np.divide(ss['_bsub_avg'], bnorm['_bsub_avg']);
            sams.loc[ss.index,'_bnorm_std'] = \
                np.multiply(
                    np.sqrt(
                        (ss['_bsub_cv']**2) +
                        (bnorm['_bsub_cv']**2)
                    ),
                    np.divide(ss['_bsub_avg'], bnorm['_bsub_avg'])
                );
            if verbose: print(s.ansi.green+"OK"+s.ansi.clear);
            # -----------------------------------------------------------------#
        return (
            sets[list(original_setcols)+set_cols],
            sams[list(original_samcols)+sam_cols]
        );
    #--------------------------------------------------------------------------#
    def workup_delta(s, sams, verbose=False):
        """Processes change in infection over change in time for sample data
        that has been processed by workup() function.  Differential is
        calculated as change in infection over change in time between two
        sample data points.  The result is a median time (between the points)
        and a differential of infection.

        Parameters
        ----------
        sams : pandas.DataFrame
            Samples pandas.DataFrame that has been processed by workup() and has
            _esid, _time, _norm_avg and _norm_std columns populated.

        Returns
        -------
        pandas.DataFrame
            Pandas DataFrame of sample differentials.

        Columns
        -------
            experiment_id   : experiment
            set_id          : set
            _esid           : experiment.set
            med_t           : median _time between two time points
            dydt_avg        : change in _norm_avg over change in _time
            dyst_std        : standard deviation for dydt_avg

        """
        deltas = [];
        # for every set
        for esid in sams['_esid'].unique():
            if verbose: print("delta "+str(esid)+": ", end='', flush=True);
            ss = sams[
                (sams['_esid']==esid) &
                (~sams['sample_id'].isin(['C','INFTY']))
            ];
            # for every time point
            for tid in ss['time_id'].sort_values():
                if tid==0: continue; # skip time ZERO, delta from right side
                p = ss[ ss['time_id']==(tid-1) ].iloc[0]; # previous time
                n = ss[ ss['time_id']==(tid) ].iloc[0];   # current time
                # change in time
                dt = n['_time'] - p['_time'];
                # average change in % infection
                dy = n['_norm_avg'] - p['_norm_avg'];
                # stdev
                err = (1/dt) * np.sqrt( np.add(
                    (n['_norm_std']**2),(p['_norm_std']**2)
                ) );
                # in order of delta.columns listed above
                row = pd.Series({
                    # experiment
                    'experiment_id' : ss['experiment_id'].values[0],
                    # set
                    'set_id'        : ss['set_id'].values[0],
                    # experiment.set
                    '_esid'         : esid,
                    # median time
                    'med_t'         : np.average( [p['_time'], n['_time']] ),
                    # change in infection average
                    'dydt_avg'      : dy / dt,
                    # change in infection stdev
                    'dydt_std'      : err,
                });
                deltas.append(row);
            if verbose: print(s.ansi.green+"OK"+s.ansi.clear);
        return pd.DataFrame(deltas);
    ############################################################################
    # LOGNORMAL FITTING ########################################################
    ############################################################################
    # NOTE: for lognormal fitting functions convention of "s" for "self" is
    # changed to "self" to avoid conflict with "sigma" as "s".

    # lognormal functions parameterized with u as a non-exponential
    # this is done to avoid precision rounding errors during fitting iterations
    def ln_cdf_ne(self,x,u,s): return lognorm.cdf( x,s,scale=u );
    def ln_pdf_ne(self,x,u,s): return lognorm.pdf( x,s,scale=u );
    def ln_ppf_ne(self,x,u,s): return lognorm.ppf( x,s,scale=u );

    # exponential-parameterized lognormal functions used for plotting, which
    # does not involve precision rounding errors.
    def ln_cdf(self,x,u,s): return lognorm.cdf( x,s,scale=np.expm1(u) );
    def ln_pdf(self,x,u,s): return lognorm.pdf( x,s,scale=np.expm1(u) );
    def ln_ppf(self,x,u,s): return lognorm.ppf( x,s,scale=np.expm1(u) );
    #--------------------------------------------------------------------------#
    def ln_fit(s, sets, sams, verbose=False):
        """Runs lognormal CDF fitting on set and sample data that has been
        processed to have calculated _bnorm_avg and _time columns.  Also
        requires _esid compound key in both set and sample DataFrames.  Fitting
        is run using scipy.optimize.curve_fit() with whatever function is
        referenced in fit_func definition below.

        Parameters
        ----------
        sets : pandas.DataFrame
            Set data pandas.DataFrame with _esid key
        sams : pandas.DataFrame
            Corresponding samples pandas.DataFrame with _esid, _bnorm_avg and
            _time column properly populated.
        verbose : bool
            Print progress to screen if True, otherwise silent.

        Returns
        -------
        pandas.DataFrame
            Fitted results DataFrame with experiment_id, set_id and _esid keys.

        """
        sets = sets.copy();
        sams = sams.copy();
        # ref to function to be used for fitting (non-expnential lognormal CDF)
        # insert your own model here, that takes x values as first arg
        fit_func = s.ln_cdf_ne;
        #----------------------------------------------------------------------#
        # fit each set, expect compound keys to already be generated
        fit_results = []; # list of pd.Series of fit results
        for esid in sets['_esid'].unique():
            if verbose: print("fitting "+str(esid)+": ", end='', flush=True);
            # index for this set in sets DataFrame
            s_ix = sets[sets['_esid']==esid].index[0];
            # get subset of sample data for fitting
            fs = sams[
                (sams['_esid']==esid) &
                (~sams['sample_id'].isin(['C','INFTY','ZERO']))
            ].sort_values(by='_time',axis=0); # sort by time
            # Fit -------------------------------------------------------------#
            fiterr = False;
            try:
                popt, pcov = curve_fit(
                    fit_func,                   # ref to function to fit
                    fs['_time'].astype(float),  # times (min)
                    fs['_bnorm_avg'],           # infection (baseline %)
                );
            except Exception as e:
                print(str(e));
                fiterr = True;
            except OptimizeWarning as e:
                print(str(e));
                fiterr = True;
            except ValueError as e:
                print(str(e));
                fiterr = True;
            except RuntimeError as e:
                print(str(e));
                fiterr = True;
            if fiterr:
                fit_results.append(
                    pd.Series({
                        # experiment
                        'experiment_id' : sets.loc[ s_ix, 'experiment_id' ],
                        # set
                        'set_id'        : sets.loc[ s_ix, 'set_id' ],
                        # experiment.set
                        '_esid'         : esid,
                        # lognormal fitted mu
                        'ln_u'          : np.nan,
                        # stdev of lognormal fitted mu
                        'ln_u_std'      : np.nan,
                        # lognormal fitted sigma
                        'ln_s'          : np.nan,
                        # stdev of lognormal fitted sigma
                        'ln_s_std'      : np.nan,
                        # lognormal fit R2
                        'ln_r2'         : np.nan,
                    })
                );
                continue;
            # Post-processing error and R2 ------------------------------------#
            perr = np.sqrt(np.diag(pcov));  # stdev of fitted params
            # calculate R2
            _residuals = fs['_bnorm_avg'].astype(float) - \
                fit_func( fs['_time'].astype(float), *popt );
            _ssres = np.sum( _residuals**2 );
            _sstot = np.sum( (fs['_bnorm_avg'].astype(float) - \
                fs['_bnorm_avg'].astype(float).mean())**2 );
            r2 = 1 - (_ssres/_sstot);
            # Store fitted metrics --------------------------------------------#
            fit_results.append(
                pd.Series({
                    # experiment
                    'experiment_id' : sets.loc[ s_ix, 'experiment_id' ],
                    # set
                    'set_id'        : sets.loc[ s_ix, 'set_id' ],
                    # experiment.set
                    '_esid'         : esid,
                    # lognormal fitted mu
                    'ln_u'          : np.log1p( popt[0] ),
                    # stdev of lognormal fitted mu
                    'ln_u_std'      : perr[0] / popt[0],
                    # lognormal fitted sigma
                    'ln_s'          : popt[1],
                    # stdev of lognormal fitted sigma
                    'ln_s_std'      : perr[1],
                    # lognormal fit R2
                    'ln_r2'         : r2
                })
            );
            if verbose: print(s.ansi.green+"OK"+s.ansi.clear);
        return pd.DataFrame(fit_results);
    #--------------------------------------------------------------------------#
    def ln_metrics(self, fits):
        """Calculates extended lognormal fit metrics from mu and s.

        Parameters
        ----------
        fits : pandas.DataFrame
            DataFrame of results from ln_fit() function.

        Returns
        -------
        pandas.DataFrame
            Copy of the original fits DataFrame with extra columns populated
            with additional metrics from fitted parameters.

        Added Metrics
        -------------
            ln_tdmax    DELAY: time point of PDF peak (mode)
            ln_l        left side of delta_hi (~60% max delta, in min)
            ln_r        right side of delta_hi (~60% max delta, in min)
            ln_d        DURATION: time spent at delta_hi (>60% max delta, min)
            ln_dmax     Max rate of change in infection (y value of PDF peak)
            ln_t20      Time point of 20% infection (**)
            ln_t50      Time point of 50% infection (**)
            ln_t75      Time point of 75% infection (**)

            (**) These are basline normalized values, so if the baseline is
            20% infection then 50% of the remaining 80% infection would put us
            at 60% non-baselined infection.  So these are percentages of the
            REMAINING range available after basline is accounted for.  So
            ln_t50 can still be calculated if the basline starts at 60%
            infection.

        """
        fits = fits.copy();
        for esid in fits['_esid'].unique():
            # get fundamental parameters for set
            s_ix = fits[fits['_esid']==esid].index[0];
            set = fits.loc[ s_ix,: ];
            u = float(set['ln_u']); # force type
            s = float(set['ln_s']); # force type
            # a little pre-calculation
            dhi_base = (u-(s**2));
            dhi_pm = np.sqrt( 2*(s**2) * np.log1p(1/0.75) );
            # calculate extended metrics
            fits.loc[ s_ix,'ln_dmax' ]  = self.ln_pdf( np.exp(u-(s**2)),u,s );
            fits.loc[ s_ix,'ln_tdmax' ] = np.exp( u - (s**2) );
            fits.loc[ s_ix,'ln_t20' ]   = self.ln_ppf( 0.2,u,s );
            fits.loc[ s_ix,'ln_t50' ]   = self.ln_ppf( 0.5,u,s );
            fits.loc[ s_ix,'ln_t75' ]   = self.ln_ppf( 0.75,u,s );
            fits.loc[ s_ix,'ln_l' ]     = np.exp( dhi_base - dhi_pm );
            fits.loc[ s_ix,'ln_r' ]     = np.exp( dhi_base + dhi_pm );
            fits.loc[ s_ix,'ln_d' ]     = np.exp( dhi_base + dhi_pm ) - \
                                          np.exp( dhi_base - dhi_pm );
        return fits;
################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
