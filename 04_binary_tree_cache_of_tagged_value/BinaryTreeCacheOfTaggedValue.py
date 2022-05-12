### local deps
from CellOfTaggedValue import CellOfTaggedValue
### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional
### test deps ###
from amaranth.sim import Simulator, Delay, Settle
from amaranth.cli import main_parser # READ amaranth/cli.py to find out parameters and what it does.
from amaranth.asserts import * # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial
#
from cli_sporny import main_runner_by_sporniket

class BinaryTreeCacheOfTaggedValue(Elaboratable):
    """
    A component that matches a set of values and output a tag.

    A new value can be added to the set. When the set is full, a value that has not been recently in use is replaced.
    """

    def __init__(self, level: int, tagSeed:int, tagWidth:int, valueShape:Shape, isRoot:bool = True):
        if isRoot and tagWidth <= level:
            raise ValueError('tagWidth should be strictly superior to root level value')
        # Store parameters to instanciate submodules inside elaborate
        self.level = level
        self.tagSeed = tagSeed
        self.tagWidth = tagWidth
        self.valueShape = valueShape
        self.isRoot = isRoot

        # Registers
        # -- book-keeping of the oldest side
        self.previousOldest = Signal() # 0 -> left branch/leaf ; 1 -> right branch/leaf ; latch of currentOldest
        self.currentOldest = Signal() # 0 -> left branch/leaf ; 1 -> right branch/leaf
        self.needChangeOldest = Signal()
        # -- gating writeEnabled
        self.effectiveWriteEnabled = Signal()

        # inputs
        self.writeEnabled = Signal() # should be asserted to bind value in dataIn to the tag.
        self.dataIn = Signal(shape=valueShape, reset_less=True) # the value to compare to internal value, or the value to bind to the tag.

        #outputs
        self.isMatching = Signal() # asserted when one of the leaf is binded to dataIn.
        self.isBound = Signal() # asserted when one of the leaf has just been bound to a value.
        self.hasFreeTag = Signal(reset_less=True) # asserted when no value has been bound to the tag
        self.dataOut = Signal(shape=unsigned(tagWidth),reset_less=True) # the tag.

    def ports(self) -> List[Signal]:
        return [
            # inputs
            self.writeEnabled, self.dataIn,

            #outputs
            self.isMatching, self.isBound, self.dataOut, self.hasFreeTag
        ]

    def elaborate(self, platform: Platform) -> Module:
        if 0 == self.level:
            return self.elaborate_leaf(platform)
        else:
            return self.elaborate_tree(platform)

    def elaborate_leaf(self, platform: Platform) -> Module:
        m = Module()

        # instanciate submodules
        subTagSeed = 2 * self.tagSeed
        m.submodules.left = left = CellOfTaggedValue(subTagSeed, unsigned(self.tagWidth), self.valueShape)
        m.submodules.right = right = CellOfTaggedValue(subTagSeed + 1, unsigned(self.tagWidth), self.valueShape)

        self.wireEverything(m, True)
        return m

    def elaborate_tree(self, platform: Platform) -> Module:
        m = Module()

        # instanciate submodules
        subLevel = self.level - 1
        subTagSeed = 2 * self.tagSeed
        m.submodules.left = left = BinaryTreeCacheOfTaggedValue(subLevel, subTagSeed, self.tagWidth, self.valueShape, isRoot=False)
        m.submodules.right = right = BinaryTreeCacheOfTaggedValue(subLevel, subTagSeed + 1, self.tagWidth, self.valueShape, isRoot=False)

        self.wireEverything(m)
        return m

    def wireEverything(self, m:Module, isLeaf:bool=False):
        left = m.submodules.left
        right = m.submodules.right

        # the root protect the whole tree against duplicate binding of a value
        exprEffectiveWriteEnabled = (~self.isMatching & self.writeEnabled) if self.isRoot else (self.writeEnabled)
        exprHasFreeTag = (left.isFree | right.isFree) if isLeaf else (left.hasFreeTag | right.hasFreeTag)

        m.d.comb += [
            # effective Write Enabled for this module
            self.effectiveWriteEnabled.eq(exprEffectiveWriteEnabled),
            # book-keeping of the oldest side
            self.needChangeOldest.eq(#
                (~self.previousOldest & (left.isMatching | left.isBound)) # either the oldest was on the left and it is now matching or have just been bound
                | (self.previousOldest & (right.isMatching | left.isBound)) # or the oldest was on the right and it is now matching or have just been bound
                ),
            self.currentOldest.eq(Mux(self.needChangeOldest, ~(self.previousOldest), self.previousOldest)),
            # wire effectiveEnabled to the oldest side
            left.writeEnabled.eq(~self.currentOldest & self.effectiveWriteEnabled),
            right.writeEnabled.eq(self.currentOldest & self.effectiveWriteEnabled),
            # fanout inputs
            left.dataIn.eq(self.dataIn),
            right.dataIn.eq(self.dataIn),
            # combine outputs
            self.isMatching.eq(left.isMatching | right.isMatching),
            self.isBound.eq(left.isBound | right.isBound),
            self.hasFreeTag.eq(exprHasFreeTag),
            self.dataOut.eq(Mux(left.isMatching,left.dataOut, right.dataOut))
        ]

        m.d.sync += [
            # latches the current oldest
            self.previousOldest.eq(self.currentOldest)
        ]

class TestBench(Elaboratable):
    def __init__(self, level: int, tagSeed:int, tagWidth:int, valueShape:Shape):
        self.dut = BinaryTreeCacheOfTaggedValue(1, 0, 2, dataInShape)
        self.sync = ClockDomain()
        # inputs
        self.writeEnabled = Signal() # should be asserted to bind value in dataIn to the tag.
        self.dataIn = Signal(shape=valueShape, reset_less=True) # the value to compare to internal value, or the value to bind to the tag.
        #outputs
        self.isMatching = Signal() # asserted when one of the leaf is binded to dataIn.
        self.isBound = Signal() # asserted when one of the leaf has just been bound to a value.
        self.hasFreeTag = Signal(reset_less=True) # asserted when no value has been bound to the tag
        self.dataOut = Signal(shape=unsigned(tagWidth),reset_less=True) # the tag.

        pass

    def ports(self) -> List[Signal]:
        return [
            self.sync.clk, self.sync.rst,
            # inputs
            self.dut.writeEnabled, self.dut.dataIn,
            # outputs
            self.isMatching, self.isBound, self.hasFreeTag, self.dataOut
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        m.submodules.dut = self.dut
        m.domains.sync = self.sync
        # wire everything
        m.d.comb += [
            # outputs
            self.isMatching.eq(self.dut.isMatching),
            self.isBound.eq(self.dut.isBound),
            self.hasFreeTag.eq(self.dut.hasFreeTag),
            self.dataOut.eq(self.dut.dataOut),

            #inputs
            self.dut.writeEnabled.eq(self.writeEnabled),
            self.dut.dataIn.eq(self.dataIn)
        ]

        return m
def ononGenerateForCoverage(parser, args, m:Module, dut: Elaboratable):
    print('--> onGenerateForCoverage')

    # prepare some other signals
    rst = m.submodules.bench.sync.rst
    # Execute
    main_runner(parser, args, m, ports=dut.ports())

def onSimulate(m: Module, dut: Elaboratable):
    print('--> onSimulate')

    # prepare simulator
    sim = Simulator(m)
    sim.add_clock(1e-6)

    def simulation():
        # fill 3 slots
        yield dut.dataIn.eq(1)
        yield dut.writeEnabled.eq(1)
        yield
        yield dut.dataIn.eq(2)
        yield
        yield dut.dataIn.eq(4)
        yield
        # match the oldest should be the right hand side, make a match to swap to the left
        yield dut.writeEnabled.eq(0)
        yield dut.dataIn.eq(2)
        yield
        # fill a slot will do that in the left hand side
        yield dut.dataIn.eq(3)
        yield dut.writeEnabled.eq(1)
        yield
        yield dut.writeEnabled.eq(0)
        yield
        # check all the slots
        yield dut.dataIn.eq(1)
        yield
        yield dut.dataIn.eq(2)
        yield
        yield dut.dataIn.eq(3)
        yield
        yield dut.dataIn.eq(4)
        yield
        # no match
        yield dut.dataIn.eq(5)
        yield
        yield dut.dataIn.eq(6)
        yield
        yield dut.dataIn.eq(7)
        yield
        yield dut.dataIn.eq(8)
        yield
        yield dut.dataIn.eq(9)
        yield
        yield dut.dataIn.eq(10)
        yield
        yield dut.dataIn.eq(11)
        yield
        yield dut.dataIn.eq(12)
        yield
        yield dut.dataIn.eq(13)
        yield
        yield dut.dataIn.eq(14)
        yield
        yield dut.dataIn.eq(15)
        yield
        yield dut.dataIn.eq(0)
        yield
        # replace the value of a 'not recently used slot'
        yield dut.dataIn.eq(10)
        yield dut.writeEnabled.eq(1)
        yield
        yield dut.writeEnabled.eq(0)
        yield # should see '0'
        # replace the value of a 'not recently used slot'
        yield dut.dataIn.eq(11)
        yield dut.writeEnabled.eq(1)
        yield
        yield dut.writeEnabled.eq(0)
        yield # should see '1'
        print("All done !")

    sim.add_sync_process(simulation)
    with sim.write_vcd("test.vcd", "test.gtkw", traces=dut.ports()):
        sim.run()
    print('<-- onSimulate')

if __name__ == "__main__":
    # Prepare
    # Prepare : retrieve cli args
    parser = main_parser()
    args = parser.parse_args()

    # Prepare : prepare the test bench
    dataInShape = unsigned(4)
    tagWidth = 2
    m = Module()
    m.submodules.bench = bench = TestBench(1, 0, tagWidth, dataInShape)

    if args.action == "generate":
        onGenerateForCoverage(parser, args, m, bench.dut)
    else:
        onSimulate(m, bench)
