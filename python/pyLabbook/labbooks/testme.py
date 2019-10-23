# pyLabbook specification generated by pyLabbook.py
from pyLabbook import pyLabbook;
def initialize(root):
	plb = pyLabbook(
		id="testme",
		root=root,
		repositoryPath="repositories/testme",
		sheetFormat="csv",
		databasePath="databases",
		databaseFile="testme.SQLITE3",
		databaseFormat="SQLITE3",
	);
	return plb;