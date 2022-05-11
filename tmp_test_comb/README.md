# The famous blink module

This project demonstrates :

* How to get simulation trace with expected signal names.

## How to get and view simulation data

* Generate the simulation data using : `python3 EightInputsOr.py` ; that will generate `test.vcd` and `test.gtkw`.
* View simulation data using : `gtkwave test.gtkw` or `gtkwave test.vcd` ; select the signals of interest, and zoom out to fit the size of the visualization panel.


### How to perform formal verification and view generated simulation data

* Generate the formal verification source `EightInputsOr.il` : `python3 EightInputsOr.py generate -t il EightInputsOr__test.il`
* Perform the formal verification : `sby -f test.sby`

_One may chains the two commands into one :_ `python3 EightInputsOr.py generate -t il EightInputsOr.il && sby -f test.sby`

## About the module

### Functional principles

* The module implements an eight inputs OR gate using a tree of two inputs OR gates.
* The simulation use an encapsulation module to get the expected name for output signals.

_(d0,d1,d2,d3,d4,d5,d6,d7) &rarr; (out)_
