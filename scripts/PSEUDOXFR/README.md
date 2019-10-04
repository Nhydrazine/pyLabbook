# Scripts associated with PSEUDOXFR protocol

This folder contains scripts associated with the PSEUDOXFR protocol (python/pyLabbook/protocols/PSEUDOXFR.py).

## Transfection recipe calculator
**transfection_recipe.py** is a command-line use script that calculates two-plasmid transfection recipes from set information of the PSEUDOXFR protocol.  Specify the labbook and experiment ids to calculate recipes for using the command line.  Outputs a spreadsheet (xlsx or csv format) that can be printed and used as a reference during the transfection protocol.  Relies on the extended PSEUDOXFR methods: `formatBioT_TransfectionRecipes()` and `calculateBioT_TransfectionRecipes()`.  These calculations are specific to BioT transfection protocol but may be modified for others - this is just an example.
