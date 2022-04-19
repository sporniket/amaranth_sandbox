# Binary tree cache of tagged value

## About this tutorial

This project demonstrates :

* A makefile to streamline the workflow : `make all`
* Recursive instanciation of modules

### How to generate and view simulation data

* `make simulations`
* Invoke `gtkwave` with the 'vcd' or the 'gtkw' file of interest

### How to perform the formal verification

* `make verifications`
* When any verification fails, invoke `gtkwave` with the trace of interest.

## About the module

### Functional principles

* The module recognizes (matches) up to 2^n values and output a tag between _0_ and _2^n - 1_.
* A new value may be binded to a free or _recently unused_ tag. The search will be limited to the half tree that did not triggered the last match.
* There is no duplicate.

_(writeEnabled, dataIn) &rarr; { oldest } &rarr; (hasFreeTag, isMatching, dataOut)_
