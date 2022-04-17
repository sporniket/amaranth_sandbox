# Cell of tagged value

## About this tutorial

This project demonstrates :

* Formal verification by assertions

### How to get and view simulation data

* Generate the simulation data using : `python3 CellOfTaggedValue.py simulate -v test.vcd -w test.gtkw -c 20` ; that will generate `test.vcd` and `test.gtkw`.
* View simulation data using : `gtkwave test.gtkw` or `gtkwave test.vcd` ; select the signals of interest, and zoom out to fit the size of the visualization panel.

_One may chains the two commands into one :_ `python3 CellOfTaggedValue.py simulate -v test.vcd -w test.gtkw -c 20 && gtkwave test.gtkw`

### How to perform formal verification and view generated simulation data

* Generate the formal verification source `test.il` : `python3 CellOfTaggedValue.py generate -t il CellOfTaggedValue__test.il`
* Perform the formal verification : `sby -f test.sby`

_One may chains the two commands into one :_ `python3 CellOfTaggedValue.py generate -t il CellOfTaggedValue__test.il && sby -f test.sby`

## About the module

### Functional principles

* The module recognizes (matches) a specific value and output a fixed tag.
* The module can tell that no value is bounded, yet. A free cell never match.
* The module can be bound to a given value.

_(writeEnabled, dataIn) &rarr; {tag, value} &rarr; (isFree, isMatching, dataOut)_
