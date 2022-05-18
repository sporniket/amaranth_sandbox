### local deps
### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional
### test deps ###

# FIXME : enums
# -- SYSTEM
T1_trace_each_instruction   = 0b1000000000000000
T0_trace_control_flow       = 0b0100000000000000
S_supervisor                = 0b0010000000000000
M_supervisor_main           = 0b0001000000000000
I_interrupt_treshold_7      = 0b0000011100000000

# -- USER
X_extends   = 0b00010000
N_negative  = 0b00001000
Z_zero      = 0b00000100
V_overflow  = 0b00000010
C_carry     = 0b00000001

class StatusRegisterUnit(Elaboratable):
    """
    The unit tasked with maintaining the status register, update the flags at each clock.
    """

    def __init__(self):
        # internal register
        self.value = Signal(shape=unsigned(16), reset=S_supervisor | M_supervisor_main)

        # inputs
        self.Operation = Signal(unsigned(2)) # 00=or ; 01=xor ; 10=and ; 11=set
        self.DataIn = Signal(unsigned(16))
        self.OperationStrobe = Signal() # if asserted, perform the operation using the data input
        self.SystemDataStrobe = Signal # if negated, do not change the system byte

        # outputs
        # -- programmer view
        self.StatusRegister = Signal(unsigned(16), reset_less=True, name="SR") # supervisor
        self.ConditionCodeRegister = Signal(unsigned(16), reset_less=True, name="CCR") # user
        # -- individual flags view
        # -- -- system
        self.Trace = Signal(unsigned(2), reset_less=True, name="T")
        self.Supervisor = Signal(reset_less=True, name="S")
        self.MainOrInterrupt = Signal(reset_less=True, name="M")
        self.InterruptLevel = Signal(unsigned(3), reset_less=True, name="I")
        # -- -- user
        self.Extends = Signal(reset_less=True, name="X")
        self.Negative = Signal(reset_less=True, name="N")
        self.Zero = Signal(reset_less=True, name="Z")
        self.Overflow = Signal(reset_less=True, name="V")
        self.Carry = Signal(reset_less=True, name="C")

    def ports(self) -> List[Signal]:
        return [
            # inputs
            self.Operation,
            self.DataIn,
            self.OperationStrobe,
            self.SystemDataStrobe,

            # outputs
            # -- programmer view
            self.StatusRegister,
            self.ConditionCodeRegister,
            # -- individual flags view
            # -- -- system
            self.Trace,
            self.Supervisor,
            self.MainOrInterrupt,
            self.InterruptLevel,
            # -- -- user
            self.Extends,
            self.Negative,
            self.Zero,
            self.Overflow,
            self.Carry
        ]
    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.comb += [
            # extract all outputs from the internal registers
            self.StatusRegister.eq(self.value),
            self.ConditionCodeRegister.eq(Cat(self.value[:8],Const(0, unsigned(8)))),
            # -- system
            self.Trace.eq(self.value[14:16]),
            self.Supervisor.eq(self.value[13]),
            self.MainOrInterrupt.eq(self.value[12]),
            self.InterruptLevel.eq(self.value[8:11]),
            # -- user
            self.Extends.eq(self.value[4]),
            self.Negative.eq(self.value[3]),
            self.Zero.eq(self.value[2]),
            self.Overflow.eq(self.value[1]),
            self.Carry.eq(self.value[0])
        ]

        return m
