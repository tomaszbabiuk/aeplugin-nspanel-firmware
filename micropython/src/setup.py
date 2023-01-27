from micropython import const
from config import ConfigManager
from nextion import *
from array import array

import network
import time

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
EntityType_Scaning = const(0x10)
EntityType_InterfaceValueOfColor = const(0x0A)
EntityType_ColorSelection = const(0x0B)
EntityType_LanguageSelection = const(0x0C)
EntityType_ConnectionState = const(0x0D)
EntityType_LeftButtonConfig = const(0x0E)
EntityType_RightButtonConfig = const(0x0F)
EntityType_ReadyToUpgrade = const(0x10)



class WifiPasswordAction(NextionAction):
    def __init__(self, renderer: NextionRenderer, configManager: ConfigManager):
        super().__init__(renderer)
        self.configManager = configManager

    def checkMatch(self, data: bytearray):
        return len(data) > 2 and data[0] == RequestType_UISelection and data[1] == EntityType_WiFiPassword

    def act(self, data: bytearray):
        password = data[2:]
        print("Typed password={}".format(password))
        self.configManager.setPassword(password)
        self.configManager.save()
        self.renderer.render("page connecting")


class ConnectingAction(NextionAction):
    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN, configManager: ConfigManager) :
        super().__init__(renderer)
        self.wlan = wlan
        self.configManager = configManager

    def checkMatch(self, data: bytearray):
        return len(data) == 2 and data[0] == RequestType_Data and data[1] == EntityType_ConnectionState

    def act(self, data: bytearray):
        self.wlan.disconnect()
        self.wlan.connect(self.configManager.getSsid(), self.configManager.getPassword())

        for x in range(1, 10):
            print("Checking network connection {}".format(x))
            time.sleep(1)
            if self.wlan.isconnected():
                break

        if self.wlan.isconnected():
            self.renderer.render("page setupSuccess")
        else:
            self.renderer.render("page setupFailure")


class SetupSuccessAction(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 2 and data[0] == RequestType_UISelection and data[1] == EntityType_ReadyToUpgrade

    def act(self, data: bytearray):
        self.renderer.update("control.tft")

class WelcomeAction(NextionAction):
    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN):
        super().__init__(renderer)
        self.wlan = wlan

    def checkMatch(self, data: bytearray):
        return len(data) == 2 and data[0] == RequestType_Data and data[1] == EntityType_SSIDs

    def act(self, data: bytearray):
        self.wlan.disconnect()
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


class WiFiSsidAction(NextionAction):
    def __init__(self, renderer: NextionRenderer, configManager: ConfigManager):
        super().__init__(renderer)
        self.configManager = configManager

    def checkMatch(self, data: bytearray):
        return len(data) > 2 and data[0] == RequestType_UISelection and data[1] == EntityType_SSIDSelection
    
    def act(self, data: bytearray):
        ssid = data[2:]
        print("Selected ssid={}".format(ssid))
        self.configManager.setSsid(ssid)
        self.renderer.render("page wifiPassword")


class LanguageSelectVM(NextionAction):
    def __init__(self, renderer: NextionRenderer, configManager: ConfigManager):
        super().__init__(renderer)
        self.configManager = configManager

    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_UISelection and data[1] == EntityType_LanguageSelection

    def act(self, data: bytearray):
        lang = data[2]
        self.configManager.setLanguage(lang)


class LeftButtonConfigAction(NextionAction):
    def __init__(self, renderer: NextionRenderer, configManager: ConfigManager):
        super().__init__(renderer)
        self.configManager = configManager

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_UISelection and data[1] == EntityType_LeftButtonConfig

    def act(self, data: bytearray):
        action = data[2]
        time = data[3]
        self.configManager.setLeftButtonConfig(action, time)


class RightButtonConfigAction(NextionAction):
    def __init__(self, renderer: NextionRenderer, configManager: ConfigManager):
        super().__init__(renderer)
        self.configManager = configManager

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_UISelection and data[1] == EntityType_RightButtonConfig

    def act(self, data: bytearray):
        action = data[2]
        time = data[3]
        self.configManager.setRightButtonConfig(action, time)



def createSetupActions(actionsBag, renderer: NextionRenderer, wlan: network.WLAN, configManager: ConfigManager):

    wiFiPasswordAction = WifiPasswordAction(renderer, configManager)
    actionsBag.append(wiFiPasswordAction)

    connectingAction = ConnectingAction(renderer, wlan, configManager)
    actionsBag.processors.append(connectingAction)

    welcomeAction = WelcomeAction(renderer, wlan)
    actionsBag.processors.append(welcomeAction)

    wiFiSsidAction = WiFiSsidAction(renderer, configManager)
    actionsBag.processors.append(wiFiSsidAction)

    languageSelectAction = LanguageSelectVM(renderer, configManager)
    actionsBag.processors.append(languageSelectAction)

    leftButtonConfigAction = LeftButtonConfigAction(renderer, configManager)
    actionsBag.processors.append(leftButtonConfigAction)

    rightButtonConfigAction = RightButtonConfigAction(renderer, configManager)
    actionsBag.processors.append(rightButtonConfigAction)

    setupSuccessAction = SetupSuccessAction(renderer)
    actionsBag.processors.append(setupSuccessAction)