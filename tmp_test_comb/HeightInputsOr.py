### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional
### test deps ###
from amaranth.sim import Simulator, Delay, Settle, Tick

class SimpleOr(Elaboratable):
    """
    out = left | right
    """

    def __init__(self):
        self.left = Signal()
        self.right = Signal()
        self.out = Signal()
        self.previousOut = Signal() # just to have a 'sync' clock domain...

    def ports(self) -> List[Signal]:
        return [
            self.left, self.right, self.out
        ]

    def elaborate(self, platform: Platform) -> Module:
        print(f"Elaborate SimpleOr {self}")
        m = Module()
        m.d.comp += [
            self.out.eq(self.left | self.right)
        ]
        m.d.sync += [
            self.previousOut.eq(self.out)
        ]
        return m


class HeightInputOr(Elaboratable):
    """
    Combine eight entry into an OR-ed signal.
    """

    def __init__(self):
        self.out = Signal()
        self.previousOut = Signal() # just to have a 'sync' clock domain...
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
        m.d.sync += [
            self.previousOut.eq(self.out)
        ]
        return m

### Test suite ###
if __name__ == "__main__":
    m = Module()
    m.submodules.dut = dut = SimpleOr()#HeightInputOr()

    #workaround sim bug
    #out = Signal()
    #dut.out.eq(out)

    sim = Simulator(m)
    sim.add_clock(1e-6)

    def process():
        # set each of the input the active one
        yield dut.left.eq(1)#dut.d0.eq(1)
        yield Tick()
        yield dut.left.eq(0)
        yield dut.right.eq(1)
        yield Tick()
        yield Tick()
        yield Tick()

    sim.add_process(process)
    with sim.write_vcd("test.vcd", "test.gtkw", traces=dut.ports()):
        sim.run()
