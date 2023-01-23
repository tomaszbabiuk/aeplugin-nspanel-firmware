from machine import UART
import os
import time

class CommandsProcessor():
    def process(self, command: bytearray):
        pass

class IconResolver:
    def resolve(self, name: str):
        # TODO
        #     x0  x1  y1  y2
        p1 = (10, 10, 20, 20)
        p2 = (15, 15, 30, 30)
        return [p1, p2]

class NextionRenderer:
    def __init__(self, uart: UART) -> None:
        self.uart = uart

    def render(self, buf, insertDelimeter = True):
        self.uart.write(buf)
        if insertDelimeter:
            self.uart.write(bytearray([0xff, 0xff, 0xff]))

    def _waitForACK(self):
        while True:
            time.sleep_ms(10)
            b = self.uart.read()
            if b != None:
                if len(b) == 1 and b[0] == 0x05:
                    break

    def _beginUpload(self, fileSize: int):
        self.render("whmi-wri {},115200,res0".format(fileSize))
        self._waitForACK()

    def _writeChunkAndWait(self, chunk: bytes):
        self.uart.write(chunk)
        self._waitForACK()

    def update(self, fileName: str):
        try:
            fileInfo = os.stat(fileName)
            fileSize = fileInfo[6]
            if (fileSize == 0):
                print("File {} is empty".format(fileName))
            else:
                print("File found: {}, {} bytes".format(fileName, fileSize))
                self._beginUpload(fileSize)
                total = 0
                with open(fileName, "rb") as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        total += len(chunk)
                        self._writeChunkAndWait(chunk)
        except OSError:
            print("File does not exist")


class NextionImageRenderer:
    def __init__(self, renderer: NextionRenderer, iconResolver: IconResolver) -> None:
        self.renderer = renderer
        self.iconResolver = iconResolver

    def renderImageToNextion(self, xRel: int, yRel: int, name):
        lines = self.iconResolver.resolve(name)
        for it in lines:
            line = "line {},{},{},{},WHITE".format(xRel + it[0], yRel + it[1], xRel + it[2], yRel + it[3])
            self.renderer.render(line)

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