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

    def __init__(self, level: int, tagSeed:int, tagWidth:int, valueShape:Shape, isRoot:bool = False):
        if isRoot and tagWidth <= level:
            raise ValueError('tagWidth should be strictly superior to root level value')
        # Store parameters to instanciate submodules inside elaborate
        self.level = level
        self.tagSeed = tagSeed
        self.tagWidth = tagWidth
        self.valueShape = valueShape
        self.isRoot = isRoot

        # Registers
        self.oldest = Signal() # 0 -> left branch/leaf ; 1 -> right branch/leaf

        # inputs
        self.writeEnabled = Signal() # should be asserted to bind value in dataIn to the tag.
        self.dataIn = Signal(shape=valueShape, reset_less=True) # the value to compare to internal value, or the value to bind to the tag.

        #outputs
        self.isMatching = Signal(reset_less=True) # asserted when one of the leaf is binded to dataIn.
        self.hasFreeTag = Signal(reset_less=True) # asserted when no value has been bound to the tag
        self.dataOut = Signal(shape=tagShape,reset_less=True) # the tag.

    def ports(self) -> List[Signal]:
        return [
            # inputs
            self.writeEnabled, self.dataIn,

            #outputs
            self.isMatching, self.dataOut, self.hasFreeTag
        ]

    def elaborate(self, platform: Platform) -> Module:
        if 0 < self.level:
            return elaborate_tree(self, platform)
        else
            return elaborate_tree(self, platform)

    def elaborate_leaf(self, platform: Platform) -> Module:
        m = Module()

        # instanciate submodules
        subTagSeed = 2 * self.tagSeed
        m.submodules.left = left = CellOfTaggedValue(subTagSeed, unsigned(self.tagWidth), self.valueShape)
        m.submodules.right = right = CellOfTaggedValue(subTagSeed, unsigned(self.tagWidth), self.valueShape)

        # wire everything
        # -- asynchronous logic
        m.d.comb += [
            # inputs
            left.dataIn.eq(self.dataIn),
            right.dataIn.eq(self.dataIn),
            # outputs
            self.isMatching.eq(left.isMatching | right.isMatching),
            self.hasFreeTag.eq(left.isFree | right.isFree),
            self.dataOut.eq(Mux(left.isMatching,left.dataOut, right.dataOut))
        ]
        if self.isRoot:
            # the root protect the whole tree against duplicate binding of a value
            effectiveWriteEnabled = Signal()
            m.d.comb += [
                effectiveWriteEnabled.eq(self.writeEnabled & ~self.isMatching),
                left.writeEnabled.eq(effectiveWriteEnabled),
                right.writeEnabled.eq(effectiveWriteEnabled)
            ]
        else:
            m.d.comb += [
                left.writeEnabled.eq(self.writeEnabled),
                right.writeEnabled.eq(self.writeEnabled)
            ]

        # -- synchronous logic
        m.d.sync += [
            # TODO
        ]
        return m

    def elaborate_tree(self, platform: Platform) -> Module:
        m = Module()

        # instanciate submodules
        subLevel = self.level - 1
        subTagSeed = 2 * self.tagSeed
        m.submodules.left = left = BinaryTreeCacheOfTaggedValue(subLevel, subTagSeed, self.tagWidth, self.valueShape)
        m.submodules.right = right = BinaryTreeCacheOfTaggedValue(subLevel, subTagSeed + 1, self.tagWidth, self.valueShape)

        # wire everything
        return m

if __name__ == "__main__":
    # Prepare
    # Prepare : retrieve cli args
    parser = main_parser()
    args = parser.parse_args()

    # Prepare : prepare the test bench
    m = Module()
    m.submodules.dut = dut = BinaryTreeCacheOfTaggedValue()

    # Prepare : prepare the test bench : workaround sim bug , override clk and rst
    nameOfClockDomain = "sync"
    m.domains.sync = sync = ClockDomain(nameOfClockDomain)
    syncClk = ClockSignal(nameOfClockDomain)
    rst = Signal()
    sync.rst = rst

    # To verify
    def myVerification(m:Module):
        pass

    def mySimulation(sim:Simulator, m:Module):

        def process():
            pass

        sim.add_sync_process(process)


    # Execute
    main_runner_by_sporniket(parser, args, m, ports=[rst, sync.clk] + dut.ports(), prepareVerification=myVerification, prepareSimulation=mySimulation)
