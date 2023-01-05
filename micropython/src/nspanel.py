from machine import UART
import time

# buffer = bytearray()

# def extractFullCommand(bytes):
#     if isinstance(bytes, bytearray):
#         print("Processing")
#         if len(bytes) >= 3 and bytes[-1] == bytes[-2] == bytes[-3] == 0xff:
#             print("Got command")
#             print(bytes)
#             return True
#     return False

# while True:
#     x  = uart.read()
#     if x is not None:
#         for byte in x:
#             buffer.append(byte)
#             clear = extractFullCommand(buffer)
#             if clear:
#                 buffer = bytearray()
#     time.sleep_ms(100)



class NsPanelParser:
    buffer = bytearray()

    def __init__(self, uart):
        self.uart = uart

    def hasFullCommand(self):
        if len(self.buffer) >= 3 and self.buffer[-1] == self.buffer[-2] == self.buffer[-3] == 0xff:
            print("Got command")
            print(self.buffer)
            return True
        return False

    def readAndParse(self):
        x  = uart.read()
        if x is not None:
            for byte in x:
                self.buffer.append(byte)
                clear = self.hasFullCommand()
                if clear:
                    self.buffer = bytearray()

uart = UART(2, 115200)
uart.init(115200, bits=8, parity=None, stop=1, tx=16, rx=17)