from machine import UART
import time
from nspanel import NsPanelParser

uart = UART(2, 115200)
uart.init(115200, bits=8, parity=None, stop=1, tx=16, rx=17)
parser = NsPanelParser(uart)

while True:
    parser.readAndParse()
    time.sleep_ms(100)
