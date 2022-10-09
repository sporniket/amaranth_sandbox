### main deps
from amaranth import *
from amaranth.build import Platform, Resource, Pins
#from amaranth_boards.resources import Pins
from typing import List, Dict, Tuple, Optional

### local deps
from slowbeat import SlowBeat
from counter import SlowRippleCounter
from decoder import Decoder

__all__ = ["ChaserGpio"]

class ChaserGpio(Elaboratable):
    """A one second cycle, 50% duty to drive a led on a target gpio of a connector.
    
    Striped down version of the amaranth-board 'blinky'."""

    def __init__(self, connectorName:str, connectorIndex:int, pinIndexes:Tuple[int], attrs = None):
        """Store the parameters for the elaboration

        Args:
            connectorName (str): The connector name
            connectorIndex (int): The connector name
            pinIndex (int): The index of the pin to use
            attrs (Attrs, optional): The attributes to setup the pin, platform dependant. Defaults to None.
        """
        self.connectorName = connectorName
        self.connectorIndex = connectorIndex
        self.targetPinIndexes = pinIndexes
        self.attrs = attrs

    def setup(self, platform):
        """Demonstrate how to setup some pins of the platform

        Args:
            platform (Platform): the platform to update.
        """

        for gpioIndex, targetPinIndex in enumerate(self.targetPinIndexes):
            # retrieve the targeted pin
            pin_name = platform.connectors[self.connectorName, self.connectorIndex].mapping[str(targetPinIndex)]
            print(f"pin name = {pin_name}")

            # setup pin as resource
            res = Resource("my_gpio",gpioIndex,Pins(pin_name, dir="o"))
            if self.attrs is not None:
                res.attrs.update(self.attrs)
            
            # append resource into platform
            platform.add_resources([res])

    def elaborate(self, platform):
        # Prepare
        m = Module()
        # -- submodules
        m.submodules.decoder = decoder = Decoder(len(self.targetPinIndexes))
        m.submodules.slowbeat = slowbeat = SlowBeat(3)
        m.submodules.counter = counter = SlowRippleCounter(decoder.input.shape().width)

        # -- configure the targeted pins as "my_gpio" with indexes starting from 0
        self.setup(platform)

        # Wiring
        # -- each gpio is selected with decoder and asserted with slowbeat
        # -- -- pin #0 is also selected when decoder is in error, for when 
        # -- -- the number of pins is not a power of 2. In this case it is usefull
        # -- -- to visually identify the first pin.
        for i in range(len(self.targetPinIndexes)):
            target = platform.request("my_gpio",i)
            if (i == 0):
                m.d.comb += target.eq((decoder.output[i] | decoder.outOfRange) & slowbeat.beat_p)
            else:
                m.d.comb += target.eq(decoder.output[i] & slowbeat.beat_p)

        # -- decoder is fed by counter
        m.d.comb += decoder.input.eq(counter.value)

        # -- counter is clocked by slowbeat
        m.d.comb += counter.beat.eq(slowbeat.beat_p)

        # DONE
        return m 