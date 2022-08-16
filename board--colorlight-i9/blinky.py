### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional

__all__ = ["Blinky"]

class Blinky(Elaboratable):
    """A one second cycle, 50% duty blinking led driver
    
    Striped down version of the amaranth-board 'blinky'."""

    def elaborate(self, platform):
        m = Module()
        
        led = platform.request("led",0)

        clk_freq = platform.default_clk_frequency
        timer = Signal(range(int(clk_freq//2)), reset=int(clk_freq//2) - 1)
        blink = Signal(reset=1)

        m.d.comb += led.eq(blink)
        with m.If(timer == 0):
            m.d.sync += timer.eq(timer.reset)
            m.d.sync += blink.eq(~blink)
        with m.Else():
            m.d.sync += timer.eq(timer - 1)
        
        return m
