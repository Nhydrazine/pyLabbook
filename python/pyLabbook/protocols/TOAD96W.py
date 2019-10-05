# pyProtocol specification generated by pyProtocol.py
from pyLabbook import pyProtocol;
import numpy as np, pandas as pd;
class initialize(pyProtocol):
	def setup(s):
		s.PROTOCOLID = "TOAD96W";
		s.addSetColumn(
			name			= "source_file",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "name of raw data file",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "source_sheet",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "name of raw data sheet",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "platemap",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "platemap used for data extraction if applicable",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "env",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "name of virus",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "pseudo_id",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "id of virus batch",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "pseudo_x",
			type			= "REAL",
			notnull			= True,
			unique			= False,
			description		= "final concentration of virus stock (X)",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "inhibitor_name",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "name of inhibitor used",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "inhibitor_id",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "id of inhibitor where applicable",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "inhibitor_conc",
			type			= "REAL",
			notnull			= True,
			unique			= False,
			description		= "final concentration of inhibitor",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "inhibitor_conc_units",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "units of inhibitor concentration",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "timepoints",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "semicolon separated list of differential time points starting with 0",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "cell_type",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "cell type used",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "temperature",
			type			= "REAL",
			notnull			= True,
			unique			= False,
			description		= "temperature in celsius during time course",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "reporter",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "name of infectivity reporter",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "read_type",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "infectivity reporter read type",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "notes",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "notes",
			default			= None,
			primary_key		= False,
		);
		s.addSamColumn(
			name			= "time_id",
			type			= "INTEGER",
			notnull			= True,
			unique			= False,
			description		= "time position number",
			default			= None,
			primary_key		= False,
		);
		s.addSamColumn(
			name			= "type",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "sample type (INFTY, ZERO, T1...Tn)",
			default			= None,
			primary_key		= False,
		);
		s.addSamColumn(
			name			= "value",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "measured infectivity value",
			default			= None,
			primary_key		= False,
		);

	def workup(s, sets, sams, varianceFormula=False):
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
			additional set columns:
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

		"""
		if varianceFormula:
			return s.workup_varianceFormula(sets, sams);
		else:
			return s.workup_noVarianceFormula(sets, sams);

	def workup_noVarianceFormula(s, sets, sams):
		"""Works up data points to subtracted, normalized and baseline'd values.
		Calculates average/stdev of data after working up instead of using
		variance formula.  This tends to give smaller error estimates.
		Conforms to specifications of s.workup().

		"""
		sets = sets.copy();
		sams = sams.copy();
		# cast as float for calculations
		sams['value'] = sams['value'].astype(float);
		# generate compound keys
		sets['_esid'] = sets['experiment_id']+'.'+sets['set_id'];
		sams['_esid'] = sams['experiment_id']+'.'+sams['set_id'];
		sams['_esrid'] = sams['_esid']+'.'+sams['replicate']; # for replicates
		# initialize calculated columns
		set_cols = [
			'_baseline_avg','_baseline_std', # % infection at time zero
			'_rebase' # baseline conversion factor
		];
		sam_cols = [
				'_time',					# time point
				'_raw_avg', '_raw_std',		# raw signal value (infectivity)
				'_sub_avg', '_sub_std',		# subtracted
				'_norm_avg', '_norm_std',	# normalized
				'_bnorm_avg', '_bnorm_std'	# baselined (t0 = 0% infection)
		];
		# initialize columns with np.nan
		for c in set_cols: sets[c] = np.nan;
		for c in sam_cols: sams[c] = np.nan;
		sams['_raw_avg'] = sams['value'];

		# calculate individual replicates
		for esid in sets['_esid']:
			r = sets[sets['_esid']==esid].iloc[0].copy(); # set row subset
			# split time points
			tpoints = pd.Series(str(r['timepoints']).split(';')).astype(float);
			# store in samples by aligning time_id with tpoints index
			samss = sams[sams['_esid']==esid];
			sams.loc[ samss.index,'_time' ] = \
				list(tpoints[ list(samss['time_id']) ] );
			# process individual replicate sample curves for this set
			for esrid in samss['_esrid'].unique():
				ss = sams[sams['_esrid']==esrid].copy(); # subset
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

		# process avg/std of worked up curve replicates
		reduced_sams = []; # samples with replicates reduced
		for esid in sets['_esid']:
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
		# replace
		sams = pd.DataFrame(reduced_sams);

		# one emore loop for additional set data
		for esid in sets['_esid']:
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
		# format as pandas.DataFrame
		reduced_sams = pd.DataFrame(reduced_sams);
		# return copies to be safe
		return (sets.copy(), sams.copy());

	def workup_varianceFormula(s, sets, sams):
		"""Works up data points to subtracted, normalized and baseline'd values.
		Calculates average/stdev of data using variance formula to propagate
		error.  This tends to give larger error estimates.  Conforms to
		specifications of s.workup().

		"""
		# confirm matching data sets
		sets = sets.copy();
		sams = sams.copy();
		# confirm set/sample matches
		sets['_esid'] = sets['experiment_id']+'.'+sets['set_id'];
		sams['_esid'] = sams['experiment_id']+'.'+sams['set_id'];
		se_esid = pd.Series(sets['_esid'].unique()).sort_values();
		sa_esid = pd.Series(sams['_esid'].unique()).sort_values();
		if not (se_esid==sa_esid).all():
			raise Exception("set and sample dataframes don't match");
		# force measurement data type, string is often used to preserve
		# error instrument reads
		sams['value'] = sams['value'].astype(float);
		# reduce replicates using combined key
		sams['_essid'] = sams['_esid']+'.'+sams['sample_id'];
		sams_reduced = [];
		for essid in sams['_essid'].unique():
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
		sams = pd.DataFrame(sams_reduced);
		sams_reduced = [];
		# calculated set columns
		set_cols = ['_baseline_avg','_baseline_std','_rebase'];
		# calculated sample columns
		sam_cols = [
				'_time',					# time point
				'_sub_avg', '_sub_std',		# subtracted
				'_norm_avg', '_norm_std',	# normalized
				'_bnorm_avg', '_bnorm_std'	# baselined (t0 = 0% infection)
		];
		# initialize calculated cols
		for c in sam_cols: sams[c] = np.nan;
		for c in set_cols: sets[c] = np.nan;
		# calculate for every distinct experiment_id.set_id
		for esid in sets['_esid'].unique():
			ss = sams[sams['_esid']==esid]; # sample subset
			r = sets[sets['_esid']==esid].iloc[0]; # set row
			# process time points
			tpoints = pd.Series(str(r['timepoints']).split(';')).astype(float);
			# use time_id as index of time point value in tpoints
			sams.loc[ss.index, '_time'] = list(tpoints[ list(ss['time_id']) ]);
			# subtract background
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
			# normalize
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
			# baseline
			# this is used for fitting.  Baseline'd values are adjusted so that
			# infection at time ZERO is true 0%, which is expected by some
			# fitting methods like lognormal.  This gives a baseline and a
			# rebase factor for adjusting back, when plotting.
			# first calculate percent infection baseline (at time ZERO)
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
			# so that Fac = Fab * rebase + baseline
			# where Fac is % infection with cell control at zero
			# and Fab is % infection with t0 at zero
		return (
			sets[['experiment_id','set_id']+set_cols],
			sams[['experiment_id','set_id','sample_id','replicate']+sam_cols]
		);
