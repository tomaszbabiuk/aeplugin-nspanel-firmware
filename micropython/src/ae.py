from micropython import const
from nextion import *
import network

RequestType_Data = const(0x00)
RequestType_UISelection = const (0x01)

EntityType_SSIDs = const(0x00)
EntityType_SSIDSelection = const(0x01)
EntityType_WiFiPassword = const(0x02)
EntityType_InboxSubjects = const(0x03)
EntityType_InboxBody = const(0x04)
EntityType_DevicesPage = const(0x05)
EntityType_InterfaceValueOfState = const(0x06)
EntityType_StateSelection = const(0x07)
EntityType_InterfaceValueOfController = const(0x08)
EntityType_ValueSelection = const(0x09)
EntityType_InterfaceValueOfColor = const(0x0A)
EntityType_ColorSelection = const(0x0B)



class WiFiScanNVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN):
        super().__init__(renderer)
        self.wlan = wlan

    def checkMatch(self, data: bytearray):
        return len(data) == 2 and data[0] == RequestType_Data and data[1] == EntityType_SSIDs

    def control(self, data: bytearray):
        scans = self.wlan.scan()
        self.renderer.render('wifiSsid.scanResult.txt="', insertDelimeter = False)
        first = True
        for scan in scans:
            if not first:
                self.renderer.render(';', insertDelimeter = False)
            
            self.renderer.render(scan[0], insertDelimeter = False)
            first = False

        self.renderer.render('"')
        self.renderer.render('page wifiSsid')


class AutomateEverythingCommandsProcessor(CommandsProcessor):

    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN) -> None:
        self.processors = []
        wifiScanNVM = WiFiScanNVM(renderer, wlan)
        self.processors.append(wifiScanNVM)

    def process(self, command: bytearray):
        for processor in self.processors:
            match = processor.checkMatch(command)
            if (match):
                print("Processor selected {}".format(processor.__class__))
                processor.control(command)
                break
            else:
                print("No match")
