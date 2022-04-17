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
        self.dataOut = Signal(shape=tagShape,reset=tagValue) # the tag.

    def ports(self) -> List[Signal]:
        return [
            # inputs
            self.writeEnabled, self.dataIn,

            #outputs
            self.isFree, self.isMatching, self.dataOut
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

        return m


### Test suite ###
if __name__ == "__main__":
    # Prepare
    # Prepare : retrieve cli args
    parser = main_parser()
    args = parser.parse_args()
    isSimulation = ("simulate" == args.action)

    # Prepare : prepare the test bench
    m = Module()
    tagValue = 3
    m.submodules.taggedValue = taggedValue = CellOfTaggedValue(tagValue, unsigned(3), unsigned(7))

    # Prepare : prepare the test bench : workaround sim bug , override clk and rst
    nameOfClockDomain = "sync"
    m.domains.sync = sync = ClockDomain(nameOfClockDomain)
    syncClk = ClockSignal(nameOfClockDomain)
    rst = Signal()
    sync.rst = rst
    # Prepare : prepare the test bench : workaround sim bug , input signals of interest
    dataIn = Signal(unsigned(16), reset=0)
    m.d.comb += taggedValue.dataIn.eq(dataIn)
    writeEnabled = Signal()
    m.d.comb += taggedValue.writeEnabled.eq(writeEnabled)

    # To verify
    def myVerification(m:Module):
        # -- the tag value is always out.
        m.d.sync += Assert(taggedValue.dataOut == tagValue)
        with m.If(Past(rst)):
            # -- Reset renders the cell free again
            m.d.sync += [
                Assert(taggedValue.isFree),
                Assert(~taggedValue.isMatching)
            ]
        with m.If(~Past(rst) & Past(taggedValue.writeEnabled)):
            # -- Write enabled bind the cell to a value, and the cell immediately matches the binded value.
            m.d.sync += [
                Assert(~taggedValue.isFree),
                Assert(taggedValue.isMatching)
            ]
        with m.If(# 2 clock cycles ago, Bind Cell to 15
                (Past(dataIn,2) == 15) & Past(writeEnabled,2)
                # 1 clock ago onward, commit the binding and keep it
                & ~Past(writeEnabled,1) & ~Past(writeEnabled)
                # when datain is not the same
                & (Past(dataIn) != 15)
            ):
            # -- Only the binded value at dataIn triggers a match
            m.d.sync += [
                Assert(~(taggedValue.isMatching))
            ]

    def mySimulation(sim:Simulator, m:Module):

        def process():
            yield dataIn.eq(512)
            yield
            yield writeEnabled.eq(1)
            yield
            yield writeEnabled.eq(0)
            yield
            yield dataIn.eq(254)
            yield
            yield dataIn.eq(512)
            yield
            yield dataIn.eq(1024)
            yield

        sim.add_sync_process(process)


    # Execute
    main_runner_by_sporniket(parser, args, m, ports=[rst, sync.clk] + taggedValue.ports(), prepareVerification=myVerification, prepareSimulation=mySimulation)
