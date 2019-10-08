# pyProtocol specification generated by pyProtocol.py
from pyLabbook import pyProtocol;
class initialize(pyProtocol):
	def setup(s):
		s.PROTOCOLID = "inhibitorProtocol";
		s.addSetColumn(
			name			= "subject",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "id or name of the subject being tested",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "subject_concentration",
			type			= "REAL",
			notnull			= True,
			unique			= False,
			description		= "final concentration of subject",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "subject_concentraiton_units",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "units for subject concentration",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "inhibitor",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "name of inhibitor",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "inhibitor_max_concentration",
			type			= "REAL",
			notnull			= True,
			unique			= False,
			description		= "maximum concentration of inhibitor in titration",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "inhibitor_concentration_units",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "units for inhibitor concentration",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "fold_dilution",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "fold dilution across inhibitor titration series",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "operator",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "initials of operator",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "date",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "date of experiment (YYYYMMDD)",
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
			name			= "type",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "D for dose, N for normal control, B for background control",
			default			= None,
			primary_key		= False,
		);
		s.addSamColumn(
			name			= "dilution_id",
			type			= "INTEGER",
			notnull			= True,
			unique			= False,
			description		= "position of sample in inhibitor titration series (0 for N and B control types)",
			default			= None,
			primary_key		= False,
		);
		s.addSamColumn(
			name			= "value",
			type			= "REAL",
			notnull			= True,
			unique			= False,
			description		= "measured signal value",
			default			= None,
			primary_key		= False,
		);