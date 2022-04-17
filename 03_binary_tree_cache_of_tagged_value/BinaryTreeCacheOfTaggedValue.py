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

    def __init__(self, tagValue: int, tagShape:Shape, valueShape:Shape):
        pass

    def ports(self) -> List[Signal]:
        pass

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
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
