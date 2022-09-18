from colorlight_i9 import Colorlight_I9_V7_2_Platform
from blinky import *
from blinky_gpio import *

#Colorlight_I9_V7_2_Platform().build(Blinky(), do_program=True)

# list of addressable pins on the first row
row_one = (5,7,9,11,13,17,23,25,27,29)
print("========================[START testing connector 'p'#2 -- row 1]============================")
for pin in row_one:
    print(f"------------------------> Pin Under Test : #{pin}")
    Colorlight_I9_V7_2_Platform().build(BlinkyGpio("p",2,pin), do_program=True)
    action = input("Continue ? (y/n) :")
    if action == "n":
        break
print("========================[END testing connector 'p'#2]============================")

print("DONE.")