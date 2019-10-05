# pyProtocol specification generated by pyProtocol.py
from pyLabbook import pyProtocol;
class initialize(pyProtocol):
	def setup(s):
		s.PROTOCOLID = "PLAPREP";
		s.addSetColumn(
			name			= "panel",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "plasmid panel where applicable",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "ZEBS_legacy",
			type			= "INTEGER",
			notnull			= False,
			unique			= False,
			description		= "1 if source is an old ZEBS plasmid",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "ZEBS_legacy_id",
			type			= "INTEGER",
			notnull			= False,
			unique			= False,
			description		= "ZEBS database record id for old ZEBS plasmid",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "ZEBS_legacy_DLBI",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "prep notes in old ZEBS plasmid database",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "name",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "name of plasmid",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "source_tubeid",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "source tube id where applicable",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "source_note",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "note about source tube",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "transform_date",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "transformation date YYYYMMDD",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "transform_cells",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "cell type used for transformation",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "transform_method",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "protocol/method used for transformation",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "resistance",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "plasmid resistance",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "colonies",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "description of transformant colonies if applicable (Y for colonies, N for none)",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "cultured",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "description of culture where applicable (Y for cultured, N for not cultured)",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "prep_date",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "DNA prep date YYYYMMDD",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "prep_kit",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "kit used for DNA prep",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "tubeid",
			type			= "TEXT",
			notnull			= True,
			unique			= False,
			description		= "product tube id",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "concentration",
			type			= "REAL",
			notnull			= False,
			unique			= False,
			description		= "product plasmid concentration",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "concentration_units",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "product plasmid concentration units",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "absorbance_260_280",
			type			= "REAL",
			notnull			= False,
			unique			= False,
			description		= "absorbance ratio (260/280)",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "absorbance_260_230",
			type			= "REAL",
			notnull			= False,
			unique			= False,
			description		= "absorbance ratio (260/230)",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "extra1",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "meta 1",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "extra2",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "meta 2",
			default			= None,
			primary_key		= False,
		);
		s.addSetColumn(
			name			= "extra3",
			type			= "TEXT",
			notnull			= False,
			unique			= False,
			description		= "meta 3",
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