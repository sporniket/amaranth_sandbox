### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional

__all__ = [
    "CellOfTaggedValue"
]

class CellOfTaggedValue(Elaboratable):
    """
    A component that matches a value and output a tag.
    """

    def __init__(self, tagValue: int, tagShape:Shape, valueShape:Shape):
        # internal Registers
        self.value = Signal(shape=valueShape)
        self.tag = Const(tagValue, shape=tagShape)

        # inputs
        self.writeEnabled = Signal() # should be asserted to bind value in dataIn to the tag.
        self.dataIn = Signal(shape=valueShape, reset_less=True) # the value to compare to internal value, or the value to bind to the tag.

        #outputs
        self.isMatching = Signal() # asserted when the cell is not free, and dataIn is matching the value.
        self.isFree = Signal(reset=1) # asserted when no value has been bound to the tag
        self.isBound = Signal() # asserted when a value has just been bound
        self.dataOut = Signal(shape=tagShape,reset=tagValue) # the tag.

    def ports(self) -> List[Signal]:
        return [
            # inputs
            self.writeEnabled, self.dataIn,

            #outputs
            self.isFree, self.isMatching, self.isBound, self.dataOut
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.comb += [
            self.dataOut.eq(self.tag),
            self.isMatching.eq((self.isFree == 0) & ((self.dataIn ^ self.value) == 0))
        ]

        with m.If(self.writeEnabled):
            m.d.sync += [
                self.value.eq(self.dataIn),
                self.isFree.eq(Const(0))
            ]

        # in effect, isBound latches writeEnabled
        m.d.sync += self.isBound.eq(self.writeEnabled)

        return m

class DataChangeWatcher(Elaboratable):
    """
    Components that signals when an input data changes.
    """

    def __init__(self, valueShape:Shape):
        # internal registers
        self.previousData = Signal(shape=dataShape)

        # inputs
        self.data = Signal(shape=dataShape)

        # outputs
        self.isDifferentImmediate = Signal()
        self.isDifferent = Signal() #synchronized latch of isDifferentImmediate

    def ports(self) -> List[Signal]:
        return [
            # inputs
            self.data,

            # outputs
            self.isDifferent
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.sync += [
            self.previousData.eq(self.data),
            self.isDifferent.eq(self.isDifferentImmediate)
        ]

        m.d.comp += self.isDifferentImmediate.eq(self.data == self.previousData)

        return m


class Comparator(Elaboratable):
    """
    Components that codifies a comparison between 2 inputs.
    """

    def __init__(self, valueShape:Shape, comparisonImpl):
        """
        comparisonImpl is a function : comparisonImpl(m:Module, left:Signal, right:Signal) -> Signal.
        The returned signal has the default shape (unsigned(1))
        """
        # inputs
        self.left = Signal(shape=valueShape)
        self.right = Signal(shape=valueShape)

        # outputs
        self.resultImmediate = Signal() # result of comparing a with b
        self.result = Signal() # synchronous latch of resultImmediate
        self.resultSymetricImmediate = Signal() # result of comparing b with a
        self.resultSymetric = Signal() # synchronous latch of resultSymetricImmediate

        # store the implementation function
        self.comparisonImpl = comparisonImpl

    def ports(self) -> List[Signal]:
        return [
            #inputs
            self.left, self.right,
            #outputs
            self.resultImmediate,self.result,
            self.resultSymetricImmediate, self.resultSymetric
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.comb += [
            self.resultImmediate.eq(self.comparisonImpl(m, self.left, self.right)),
            self.resultSymetricImmediate.eq(self.comparisonImpl(m, self.right, self.left)),
        ]

        m.d.sync += [
            self.result.eq(self.resultImmediate),
            self.resultSymetric.eq(self.resultSymetricImmediate)
        ]

        return m
