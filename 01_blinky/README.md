# The famous blink module

This project demonstrates :

* The basics of hardware design with amaranth
* How to obtain simulation data to be viewed using GTKWave.

## How to get and view simulation data

* Generate the simulation data using : `python3 bleep.py` ; that will generate `test.vcd` and `test.gtkw`.
* View simulation data using : `gtkwave test.gtkw` or `gtkwave test.vcd` ; select the signals of interest, and zoom out to fit the size of the visualization panel.
