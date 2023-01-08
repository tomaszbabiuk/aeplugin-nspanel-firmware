from machine import UART
from micropython import const

class CommandsProcessor():
    def process(self, command: bytearray):
        pass

class NextionRenderer:
    def __init__(self, uart: UART) -> None:
        self.uart = uart

    def render(self, buf, insertDelimeter = True):
        self.uart.write(buf)
        if insertDelimeter:
            self.uart.write(bytearray([0xff, 0xff, 0xff]))


class NextionParser:
    buffer = bytearray()

    def __init__(self, uart: UART, processor: CommandsProcessor):
        self.uart = uart
        self.processor = processor

    def hasFullCommand(self):
        bufLen = len(self.buffer)
        if bufLen >= 3 and self.buffer[-1] == self.buffer[-2] == self.buffer[-3] == 0xff:
            print("Got data from Nextion display")
            print(self.buffer)
            self.processor.process(self.buffer[:(bufLen-3)])

            return True
        return False

    def readAndParse(self):
        x  = self.uart.read()
        if x is not None:
            for byte in x:
                self.buffer.append(byte)
                clear = self.hasFullCommand()
                if clear:
                    self.buffer = bytearray()

class NextionViewModel:
    def __init__(self, renderer: NextionRenderer):
        self.renderer = renderer

    def checkMatch(self, data: bytearray):
        return False

    def control(self, data: bytearray):
        pass
