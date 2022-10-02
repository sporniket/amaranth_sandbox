### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional

### test deps ###
from amaranth.sim import Simulator, Delay, Settle
from amaranth.cli import (
    main_parser,
)  # READ amaranth/cli.py to find out parameters and what it does.
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial
from amaranth.back import rtlil, cxxrtl, verilog
import inspect
import subprocess

from demux import Demux


class TestOfDemux:
    def setup(self):
        self.m = m = Module()
        self.channelCount = channelCount = 3
        m.submodules.demux = demux = Demux(channelCount)

        # Prepare : prepare the test bench : workaround sim bug , override clk and rst
        nameOfClockDomain = "sync"
        m.domains.sync = sync = ClockDomain(nameOfClockDomain)
        self.rst = rst = Signal()
        sync.rst = rst
        # Prepare : prepare the test bench : workaround sim bug , input signals of interest
        self.dataIn = dataIn = Signal(demux.input.shape())
        m.d.comb += demux.input.eq(dataIn)
        self.setupVerify()

    def setupVerify(self):
        m = self.m
        rst = self.rst
        demux = m.submodules.demux
        for i in range(0, self.channelCount):
            with m.If(~Past(rst) & (Past(demux.input) == i)):
                m.d.sync += [
                    Assert(demux.output == (1 << i)),
                    Assert(~(demux.outOfRange)),
                ]
        with m.If(~Past(rst) & (Past(demux.input) == self.channelCount)):
            m.d.sync += [Assert(demux.output == 0), Assert(demux.outOfRange)]

    def run(self, platform=None):
        fragment = Fragment.get(self.m, platform)
        generate_type = "il"  # "il" -> rtlil / "cc" -> cxxrtl
        name = "top"  # name of module
        output = rtlil.convert(
            fragment,
            ports=[self.rst, ClockSignal("sync")] + self.m.submodules.demux.ports(),
        )

        # target file
        outputFileNameBase = (
            f"tmp.{self.__class__.__name__}__{inspect.currentframe().f_code.co_name}"
        )
        outputFileName = f"{outputFileNameBase}.il"
        sbyFileName = f"{outputFileNameBase}.sby"

        # generate rtlil
        print(f"Generating {outputFileName}...")
        with open(outputFileName, "wt") as f:
            f.write(output)

        # generate sby config
        configLines = [
            "[tasks]",
            "bmc",
            "cover",
            "",
            "[options]",
            "bmc: mode bmc",
            "cover: mode cover",
            "depth 2",
            "multiclock off",
            "",
            "[engines]",
            "smtbmc boolector",
            "",
            "[script]",
            f"read_ilang {outputFileName}",
            "prep -top top",
            "",
            "[files]",
            f"{outputFileName}",
        ]
        print(f"Generating {sbyFileName}...")
        with open(sbyFileName, "wt") as f:
            f.write("\n".join(configLines))

        print(f"Running sby -f {sbyFileName}...")
        with subprocess.Popen(["sby", "-f", sbyFileName]) as proc:
            if proc.returncode != 0:
                exit(proc.returncode)


def run():
    test = TestOfDemux()
    test.setup()
    test.run()


if __name__ == "__main__":
    run()
