# Binary tree cache of tagged value

## About this tutorial

This project demonstrates :

* A makefile to streamline the workflow : `make all`

### How to generate and view simulation data

* `make simulations`
* Invoke `gtkwave` with the 'vcd' or the 'gtkw' file of interest

### How to perform the formal verification

* `make verifications`
* When any verification fails, invoke `gtkwave` with the trace of interest.

## About the module

### Functional principles

* The module recognizes (matches) up to 2^n values and output a tag between _0_ and _2^n - 1_.
* A new value may be binded to a free or _recently unused_ tag.
* There is no duplicate.

_(writeEnabled, dataIn) &rarr; { ? } &rarr; (hasFreeTag, isMatching, dataOut)_
