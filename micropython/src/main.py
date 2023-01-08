import time
import network
from machine import UART
from nextion import *
from ae import AutomateEverythingCommandsProcessor

uart = UART(2, 115200)
uart.init(115200, bits=8, parity=None, stop=1, tx=16, rx=17)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

renderer = NextionRenderer(uart)
processor = AutomateEverythingCommandsProcessor(renderer, wlan)
parser = NextionParser(uart, processor)

while True:
    parser.readAndParse()
    time.sleep_ms(100)
    