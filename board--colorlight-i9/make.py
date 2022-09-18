from colorlight_i9 import Colorlight_I9_V7_2_Platform
from blinky import *
from blinky_gpio import *

def askContinue():
    action = input("Continue ? (y/n) :")
    if action == "n":
        print("Bye.")
        exit()

if __name__ == "__main__":
    print("========================[ START testing onboard LED ]============================")
    Colorlight_I9_V7_2_Platform().build(Blinky(), do_program=True)
    askContinue()

    # list of addressable pins on the first row
    row_one = (5,7,9,11,13,17,23,25,27,29)
    row_two = (6,8,10,12,14,18,24,26,28,30)

    conn_index = 2 # provision for future loop
    print(f"========================[START testing connector 'p'#{conn_index} -- row 1]============================")
    print(f"INSTALL test rig on first row of connector {conn_index}")
    askContinue()
    for pin in row_one:
        print(f"------------------------> Pin Under Test : #{pin}")
        Colorlight_I9_V7_2_Platform().build(BlinkyGpio("p",2,pin), do_program=True)
        askContinue()

    print(f"========================[START testing connector 'p'#{conn_index} -- row 2]============================")
    print(f"INSTALL test rig on second row of connector {conn_index}")
    askContinue()
    for pin in row_two:
        print(f"------------------------> Pin Under Test : #{pin}")
        Colorlight_I9_V7_2_Platform().build(BlinkyGpio("p",2,pin), do_program=True)
        askContinue()

    print(f"========================[END testing connector 'p'#{conn_index}]============================")

    print("ALL DONE.")