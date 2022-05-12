### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional
### test deps ###
from amaranth.sim import Simulator, Delay, Settle, Tick
from amaranth.cli import main_parser, main_runner # READ amaranth/cli.py to find out parameters and what it does.
from amaranth.asserts import * # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

class SimpleOr(Elaboratable):
    """
    out = left | right
    """

    def __init__(self):
        self.left = Signal()
        self.right = Signal()
        self.out = Signal()

    def ports(self) -> List[Signal]:
        return [
            self.left, self.right, self.out
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        m.d.comb += [
            self.out.eq(self.left | self.right)
        ]
        return m


class EightInputsOr(Elaboratable):
    """
    Combine eight entry into an OR-ed signal.
    """

    def __init__(self):
        self.out = Signal()
        self.d0 = Signal()
        self.d1 = Signal()
        self.d2 = Signal()
        self.d3 = Signal()
        self.d4 = Signal()
        self.d5 = Signal()
        self.d6 = Signal()
        self.d7 = Signal()

    def ports(self) -> List[Signal]:
        return [
            self.d0, self.d1, self.d2, self.d3, self.d4, self.d5, self.d6, self.d7,
            self.out
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        # instanciate submodules
        # -- level 0, 4 simple OR
        m.submodules.or_0_0 = or_0_0 = SimpleOr()
        m.submodules.or_0_1 = or_0_1 = SimpleOr()
        m.submodules.or_0_2 = or_0_2 = SimpleOr()
        m.submodules.or_0_3 = or_0_3 = SimpleOr()
        # -- level 1, 2 simple OR
        m.submodules.or_1_0 = or_1_0 = SimpleOr()
        m.submodules.or_1_1 = or_1_1 = SimpleOr()

        # wire ports
        m.d.comb += [
            # in
            or_0_0.left.eq(self.d0),
            or_0_0.right.eq(self.d1),
            or_0_1.left.eq(self.d2),
            or_0_1.right.eq(self.d3),
            or_0_2.left.eq(self.d4),
            or_0_2.right.eq(self.d5),
            or_0_3.left.eq(self.d6),
            or_0_3.right.eq(self.d7),
            # from level 0 to level 1
            or_1_0.left.eq(or_0_0.out),
            or_1_0.right.eq(or_0_1.out),
            or_1_1.left.eq(or_0_2.out),
            or_1_1.right.eq(or_0_3.out),
            # from level 1 to out
            self.out.eq(or_1_0.out | or_1_1.out)
        ]
        return m

class TestBench(Elaboratable):
    """
    The test bench encapsulate the 'device under test' (dut) to give a predictable access to the ports of the dut.

    The goal is to get a 'gtkw' file with signals using the expected dut signal names (e.g. 'foo') instead of the name
    inside the simulator (e.g. 'foo$4') that would make the traces confusing.
    """
    def __init__(self):
        self.dut = EightInputsOr()
        self.sync = ClockDomain()
        self.out = Signal()
        self.d0 = Signal()
        self.d1 = Signal()
        self.d2 = Signal()
        self.d3 = Signal()
        self.d4 = Signal()
        self.d5 = Signal()
        self.d6 = Signal()
        self.d7 = Signal()

    def ports(self) -> List[Signal]:
        return [
            self.sync.clk, self.sync.rst,
            # for the input ports, list the ports from the dut
            self.dut.d0, self.dut.d1, self.dut.d2, self.dut.d3, self.dut.d4, self.dut.d5, self.dut.d6, self.dut.d7,
            # for the output ports, list the ports from the bench
            self.out
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        m.submodules.dut = self.dut
        m.domains.sync = self.sync

        # wire everything
        m.d.comb += [
            # outputs
            self.out.eq(self.dut.out),

            #inputs
            self.dut.d0.eq(self.d0),
            self.dut.d1.eq(self.d1),
            self.dut.d2.eq(self.d2),
            self.dut.d3.eq(self.d3),
            self.dut.d4.eq(self.d4),
            self.dut.d5.eq(self.d5),
            self.dut.d6.eq(self.d6),
            self.dut.d7.eq(self.d7)
        ]

        return m

# callback when simulating
def onSimulate(m: Module, dut: Elaboratable):
    print('--> onSimulate')

    # prepare simulator
    sim = Simulator(m)
    sim.add_clock(1e-6)

    def process():
        # set each of the input the active one
        yield
        yield dut.d0.eq(1)
        yield
        yield dut.d0.eq(0)
        yield
        yield dut.d1.eq(1)
        yield
        yield dut.d1.eq(0)
        yield
        yield dut.d2.eq(1)
        yield
        yield dut.d2.eq(0)
        yield
        yield dut.d3.eq(1)
        yield
        yield dut.d3.eq(0)
        yield
        yield dut.d4.eq(1)
        yield
        yield dut.d4.eq(0)
        yield
        yield dut.d5.eq(1)
        yield
        yield dut.d5.eq(0)
        yield
        yield dut.d6.eq(1)
        yield
        yield dut.d6.eq(0)
        yield
        yield dut.d7.eq(1)
        yield
        yield dut.d7.eq(0)
        yield
        yield

    sim.add_sync_process(process)
    with sim.write_vcd("test.vcd", "test.gtkw", traces=dut.ports()):
        sim.run()

def onGenerateForCoverage(parser, args, m:Module, dut: Elaboratable):
    print('--> onGenerateForCoverage')

    # prepare some other signals
    rst = m.submodules.bench.sync.rst

    with m.If(Past(rst)):
        m.d.sync += [
            Assert(~dut.out)
        ]
    with m.If(~Past(rst) &
        (Past(dut.d0) | Past(dut.d1) | Past(dut.d2) | Past(dut.d3) | Past(dut.d4) | Past(dut.d5) | Past(dut.d6) | Past(dut.d7))):
        m.d.sync += [
            Assert(dut.out)
        ]
    with m.If(~Past(rst) &
        (~(Past(dut.d0) | Past(dut.d1) | Past(dut.d2) | Past(dut.d3) | Past(dut.d4) | Past(dut.d5) | Past(dut.d6) | Past(dut.d7)))):
        m.d.sync += [
            Assert(~dut.out)
        ]
    # Execute
    main_runner(parser, args, m, ports=dut.ports())

### Test suite ###
if __name__ == "__main__":
    # Prepare
    # Prepare : retrieve cli args
    parser = main_parser()
    args = parser.parse_args()

    # Prepare : prepare test bench
    m = Module()
    m.submodules.bench = bench = TestBench()

    if args.action == "generate":
        onGenerateForCoverage(parser, args, m, bench.dut)
    else:
        onSimulate(m, bench)
