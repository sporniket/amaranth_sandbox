### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional
### test deps ###
from amaranth.sim import Simulator, Delay, Settle

class Bleeper(Elaboratable):
    """
    A dummy component that output a signal alternating between high and low.
    """

    def __init__(self):
        self.q = Signal(unsigned(1), reset=0)

    def ports(self) -> List[Signal]:
        return [
            self.q
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        m.d.sync += self.q.eq(~self.q)
        return m

### Test suite ###
if __name__ == "__main__":
    m = Module()
    m.submodules.bleeper = bleeper = Bleeper()

    #workaround sim bug
    q = Signal(unsigned(1), reset=0)
    bleeper.q.eq(q)

    sim = Simulator(m)
    sim.add_clock(1e-6)

    def process():
        # just let the time pass
        yield
        yield
        yield
        yield

    sim.add_sync_process(process) # or sim.add_sync_process(process), see below
    with sim.write_vcd("test.vcd", "test.gtkw", traces=bleeper.ports()):
        sim.run()
