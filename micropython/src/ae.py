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
EntityType_LanguageSelection = const(0x1C) # Change to 0x0C after new HMI is prepared

class WifiPasswordNVM(NextionViewModel):
    def checkMatch(self, data: bytearray):
        return len(data) > 2 and data[0] == RequestType_UISelection and data[1] == EntityType_WiFiPassword

    def control(self, data: bytearray):
        password = data[2:]
        print("Typed password={}".format(password))
        f = open('password','w')
        f.write(str(password))
        f.close()
        self.renderer.render("page connecting")
        # the control page should be called when the http/mqtt server gets data
        # Thread.sleep(3000)
        # renderer.render("page control")

class WiFiSsidNVM(NextionViewModel):
    def checkMatch(self, data: bytearray):
        return len(data) > 2 and data[0] == RequestType_UISelection and data[1] == EntityType_SSIDSelection
    
    def control(self, data: bytearray):
        ssid = data[2:]
        print("Selected ssid={}".format(ssid))
        f = open('ssid','w')
        f.write(str(ssid))
        f.close()
        self.renderer.render("page wifiPassword")


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


class LanguageSelectVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer):
        super().__init__(renderer)

    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_UISelection and data[1] == EntityType_LanguageSelection

    def control(self, data: bytearray):
        lang = data[2]
        f = open('lang','w')
        f.write(str(lang))
        f.close()


class AutomateEverythingCommandsProcessor(CommandsProcessor):

    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN) -> None:
        self.processors = []

        wifiScanNVM = WiFiScanNVM(renderer, wlan)
        self.processors.append(wifiScanNVM)

        languageSelectNVM = LanguageSelectVM(renderer)
        self.processors.append(languageSelectNVM)

        wiFiSsidNVM = WiFiSsidNVM(renderer)
        self.processors.append(wiFiSsidNVM)

        wiFiPasswordNVM = WifiPasswordNVM(renderer)
        self.processors.append(wiFiPasswordNVM)


    def process(self, command: bytearray):
        hasMatch = False
        for processor in self.processors:
            match = processor.checkMatch(command)
            if (match):
                print("Processor selected {}".format(processor.__class__))
                processor.control(command)
                hasMatch = True
                break
            
        if not hasMatch:
            print("No match")
