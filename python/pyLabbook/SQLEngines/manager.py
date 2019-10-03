import importlib;
def loadSQLEngine(format):
    # switch this to loading module using string
    try:
        # import the module containing the engine class
        m = importlib.import_module('pyLabbook.SQLEngines.' + str(format));
        # return an instance of the engine class for that module
        return m.engine();
    except Exception as e:
        raise Exception("Can't find SQLEngine for " + str(format) + ": " + str(e));
