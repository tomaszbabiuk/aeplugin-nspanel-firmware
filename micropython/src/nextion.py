from machine import UART

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
