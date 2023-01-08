from micropython import const
from nextion import *
from nvm.language_select_nvm import LanguageSelectVM
from nvm.wifi_scan_nvm import WiFiScanNVM

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

class AutomateEverythingCommandsProcessor(CommandsProcessor):

    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN) -> None:
        self.processors = []

        wifiScanNVM = WiFiScanNVM(renderer, wlan)
        self.processors.append(wifiScanNVM)

        languageSelectNVM = LanguageSelectVM(renderer)
        self.processors.append(languageSelectNVM)


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
