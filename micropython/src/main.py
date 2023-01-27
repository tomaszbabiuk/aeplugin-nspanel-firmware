import time
import network
from machine import UART
from nextion import *
from setup import createSetupActions
from control import createControlActions
from config import ConfigManager

uart = UART(2, 115200)
uart.init(115200, bits=8, parity=None, stop=1, tx=16, rx=17)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

configManager = ConfigManager()
writer = NextionWriter(uart)

actionsBag = []
createSetupActions(actionsBag, writer, wlan, configManager)
createControlActions(actionsBag, writer)
parser = NextionReader(uart, actionsBag)

while True:
    parser.readAndParse()
    time.sleep_ms(50)