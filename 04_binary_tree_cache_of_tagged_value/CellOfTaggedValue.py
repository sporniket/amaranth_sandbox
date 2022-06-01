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
### local deps ###
from components import *

### Test suite ###
if __name__ == "__main__":
    # Prepare
    # Prepare : retrieve cli args
    parser = main_parser()
    args = parser.parse_args()

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
                Assert(~taggedValue.isMatching),
                Assert(~taggedValue.isBound)
            ]
        with m.If(~Past(rst) & Past(taggedValue.writeEnabled)):
            # -- Write enabled bind the cell to a value, and the cell immediately matches the binded value.
            m.d.sync += [
                Assert(~taggedValue.isFree),
                Assert(taggedValue.isMatching),
                Assert(taggedValue.isBound)
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
                Assert(~taggedValue.isMatching),
                Assert(~taggedValue.isBound)
            ]
        with m.If(~Past(writeEnabled)):
            m.d.sync += [
                Assert(~taggedValue.isBound)
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
