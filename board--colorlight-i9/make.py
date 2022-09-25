from colorlight_i9 import Colorlight_I9_V7_2_Platform
from blinky import *
from blinky_gpio import *
from amaranth import Elaboratable
from amaranth.build import Platform
from typing import List

def askContinue() -> bool:
    action = input("Continue ? (y/n) :")
    return action == "y"

def askContinueOrDie():
    action = input("Continue ? (y/n) :")
    if askContinue() is not True:
        print("Bye.")
        exit()


class TestRunner:
    @property
    def label(self)->str:
        return self._label
    
    @property
    def help(self):
        self._description
    
    def run(self):
        raise(RuntimeError("NOT IMPLEMENTED"))

class PlatformDemoTestRunner(TestRunner):
    def __init__(self, testLabel:str, testDescription:str, platform:Platform, testModule:Elaboratable):
        self._label = testLabel
        self._description = testDescription
        self.platform = platform
        self.module = testModule

    def run(self):
        print(f"========================[ START OF {self.label} ]============================")
        if len(self._description) > 0:
            print(self._description)
        self.platform.build(self.module, do_program = True)
        print(f"-- -- -- -- -- -- -- -- [ END OF {self.label} ] -- -- -- -- -- -- -- --")

class GroupOfTests(TestRunner):
    def __init__(self, testLabel:str, testDescription:str, tests:List[TestRunner]):
        self._label = testLabel
        self._description = testDescription
        self.tests = tests
    
    def run(self):
        print(f"========================[ START OF GROUP {self.label} ]============================")
        if len(self._description) > 0:
            print(self._description)
        if askContinue() is True:
            for test in self.tests:
                test.run()
        print(f"-- -- -- -- -- -- -- -- [ END OF GROUP {self.label} ] -- -- -- -- -- -- -- --")
    
if __name__ == "__main__":
    allTheTests = GroupOfTests(
        "Demonstration of platform 'Colorlight I9 v7.2'",
        "Build and upload a bunch of gateware demonstrating the platform resources",
        [
            PlatformDemoTestRunner("testing onboard LED", "Build and upload a gateware that makes onboard LED(s) blink", Colorlight_I9_V7_2_Platform(), Blinky()),
            GroupOfTests(
                "Testing expansion board connectors",
                "Test connectors p2..p6 of the expansion board needs to connect LEDs to one row of the connector, for each row",
                [
                    GroupOfTests(f"Connector 'p'#{conn_index}", "", [
                        GroupOfTests(
                            f"Testing connector 'p'#{conn_index} -- row 1", 
                            f"INSTALL test rig on row 1 of connector {conn_index}", 
                            [
                                PlatformDemoTestRunner(
                                    f"Pin Under Test : #{pin}", 
                                    "", 
                                    Colorlight_I9_V7_2_Platform(), 
                                    BlinkyGpio("p",conn_index,pin)
                                )
                                for pin in (5,7,9,11,13,17,23,25,27,29)
                            ]
                        ),
                        GroupOfTests(
                            f"Testing connector 'p'#{conn_index} -- row 2", 
                            f"INSTALL test rig on row 2 of connector {conn_index}", 
                            [
                                PlatformDemoTestRunner(
                                    f"Pin Under Test : #{pin}", 
                                    "", 
                                    Colorlight_I9_V7_2_Platform(), 
                                    BlinkyGpio("p",conn_index,pin)
                                )
                                for pin in (6,8,10,12,14,18,24,26,28,30)
                            ]
                        ),
                    ]
                    ) for conn_index in (2,)
                ]
            )
        ]
    ).run()
    print("ALL DONE.")