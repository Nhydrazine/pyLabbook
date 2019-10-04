# pyLabbook Core Classes

## pyLabbook.py
Contains the `pyLabbook.pyLabbook` class.  A container class that holds information about the files and paths associated with a labbook.  A **labbook** is an instance of this base class that is populated the the corresponding path and file information.

## pyProtocol.py
Contains the `pyLabbook.pyProtocol` class.  A class that holds information about the structure of protocol-associated data and contains methods used to store and retrieve this information from a labbook's database and repository.  The `pyLabbook.pyProtocol` class itself specifies the **minimal data structure** that is inherited by all protocols.  A **protocol** is an extended `pyLabbook.pyProtocol` object that has its own, modified `setup()` method.  See python/pyLabbook/protocols documentation for more information on how protocols extend this base class.
