from micropython import const
from credentialsmanager import CredentialsManager
from nextion import *

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
EntityType_InterfaceValueOfColor = const(0x0A)
EntityType_ColorSelection = const(0x0B)
EntityType_LanguageSelection = const(0x0C) # Change to 0x0C after new HMI is prepared
EntityType_ConnectionStateSelection = const(0x0D)
EntityType_LeftButtonConfig = const(0x0E)
EntityType_RightButtonConfig = const(0x0F)

class ColorSelectedNVM(NextionViewModel):
    def checkMatch(self, data: bytearray):
        return len(data) == 7 and data[0] == RequestType_UISelection and data[1] == EntityType_ColorSelection

    def control(self, data: bytearray):
        instanceIdLSB = data[2]
        instanceIdMSB = data[3]
        instanceId = instanceIdMSB*256 + instanceIdLSB
        valueHueLSB = data[4]
        valueHueMSB = data[5]
        valueHue = valueHueMSB*256 + valueHueLSB
        valueBrightness = data[6]
        print("Color selected, instance id={}, hue={}, brightness={}".format(instanceId, valueHue, valueBrightness))
        self.renderer.render("page control")


class ControlColorNVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer, imageRenderer: NextionImageRenderer):
        super().__init__(renderer)
        self.imageRenderer = imageRenderer

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_Data and data[1] == EntityType_InterfaceValueOfColor

    def control(self, data: bytearray):
        self.renderer.render("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh*256 + instanceIdLow
        if instanceId == 0x03:
            self.renderer.render('titleTxt.txt="Lamp 20X"')
            self.renderer.render("hueSlr.val=124") #min val + 4 steps
            self.renderer.render("brightSlr.val=90")
            self.imageRenderer.renderImageToNextion(174, 57, "buttonIcon")

        self.renderer.render("vis loadingBtn,0")
        self.renderer.render("vis applyBtn,1")


class ControlControllerNVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer, imageRenderer: NextionImageRenderer):
        super().__init__(renderer)
        self.imageRenderer = imageRenderer

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_Data and EntityType_InterfaceValueOfController

    def control(self, data: bytearray):
        self.renderer.render("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh* 256 + instanceIdLow
        if instanceId == 0x02:
            self.renderer.render('titleTxt.txt="Controller 10XPf"')
            self.renderer.render('minValTxt.txt="10°C"')
            self.renderer.render('maxValTxt.txt="40°C"')
            self.renderer.render("vis markerTxt,1")
            self.renderer.render('unitTxt.txt="°C"')
            self.renderer.render("step.val=50") #0.5°C
            self.renderer.render("valSlr.maxval=60") #(40-10)*2... steps per range
            self.renderer.render("valSlr.val=4") #min val + 4 steps
            self.renderer.render("valueTxt.val=1200")
            self.imageRenderer.renderImageToNextion(174, 57, "atticIcon")

        self.renderer.render("vis loadingBtn,0")
        self.renderer.render("vis applyBtn,1")


class ControllerSelectedNVM(NextionViewModel):
    def checkMatch(self, data: bytearray):
        return len(data) == 8 and data[0] == RequestType_UISelection and data[1] == EntityType_ValueSelection

    def control(self, data: bytearray):
        instanceIdLSB = data[2]
        instanceIdMSB = data[3]
        instanceId = instanceIdMSB*256 + instanceIdLSB
        valueLSB = data[4]
        valueB2 = data[5]
        valueB3 = data[6]
        valueMSB = data[7]
        value = valueMSB* 16777216 + valueB3*65536 + valueB2*256 + valueLSB
        print("Value selected, instance id={}, value={}".format(instanceId, value))
        self.renderer.render("page control")


class ControlNVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer, imageRenderer: NextionImageRenderer):
        super().__init__(renderer)
        self.imageRenderer = imageRenderer

    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_DevicesPage

    def boolToNumber(self, b: bool):
        if b:
            return 1
        else:
            return 0

    def renderPager(self, prevEnabled: bool, nextEnabled: bool):
        self.renderer.render("vis prevPageBtn,{}".format(self.boolToNumber(prevEnabled)))
        self.renderer.render("vis nextPageBtn,{}".format(self.boolToNumber(nextEnabled)))
        self.renderer.render("vis loadingBtn,0")
    
    def renderEmptySlot(self, slot: int):
        self.renderer.render("vis background{}Txt,0".format(slot))
        self.renderer.render("vis name{}Txt,0".format(slot))
        self.renderer.render("vis desc{}Txt,0".format(slot))
        self.renderer.render("vis marker{}Txt,0".format(slot))
        self.renderer.render("vis slo${}Btn,0".format(slot))

    def renderControlSlot(self, slot: int, instanceId: int, controlType: int, name: str, description: str, state: str, signaled: bool):
        self.renderer.render("instanceId{}.val={}".format(slot, instanceId))
        self.renderer.render("vis background{}Txt,1".format(slot))
        self.renderer.render("vis name{}Txt,1".format(slot))
        self.renderer.render('name{}Txt.txt="{}"'.format(slot, name))
        self.renderer.render("vis desc{}Txt,1".format(slot))
        self.renderer.render('desc{}Txt.txt="{}"'.format(slot, description))
        self.renderer.render("vis marker{}Txt,{}".format(slot, self.boolToNumber(signaled)))
        self.renderer.render("vis slot{}Btn,1".format(slot))
        self.renderer.render('slot{}Btn.txt="{}"'.format(slot, state))
        self.renderer.render("type{}.val={}".format(slot, controlType))

    def control(self, data: bytearray):
        page = data[2]
        if page == 0x00:
            self.renderControlSlot(0, 1,0,"Recuperator", "---", "II gear", True)
            self.renderControlSlot(1, 2,1,"Radiator valve", "Opening state: 12%", "Regulation", False)
            self.renderControlSlot(2, 3,2,"Ceiling lamp", "12W", "On", True)
            self.renderControlSlot(3, 4,0,"Desk lamp", "0W", "Off", False)
            self.renderControlSlot(4, 5,1,"Door", "---", "Closed", False)

            self.imageRenderer.renderImageToNextion(65, 47, "atticIcon")
            self.imageRenderer.renderImageToNextion(65, 102, "buttonIcon")
            self.imageRenderer.renderImageToNextion(65, 157, "boilerIcon")
            self.imageRenderer.renderImageToNextion(65, 212, "blindsIcon")
            self.imageRenderer.renderImageToNextion(65, 267, "bullhornIcon")
            self.renderPager(prevEnabled = False, nextEnabled = True)
        else:
            self.renderControlSlot(0, 6,0,"Window contactron", "---", "Disarmed", True)
            self.renderControlSlot(1, 7,0,"Motion sensor", "---", "Disarmed", False)
            self.renderEmptySlot(2)
            self.renderEmptySlot(3)
            self.renderEmptySlot(4)

            self.imageRenderer.renderImageToNextion(65, 47, "atticIcon")
            self.imageRenderer.renderImageToNextion(65, 102, "buttonIcon")
            self.renderPager(prevEnabled = True, nextEnabled = False)


class ControlStateNVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer, imageRenderer: NextionImageRenderer):
        super().__init__(renderer)
        self.imageRenderer = imageRenderer

    def checkMatch(self, data: bytearray):
        return len(data) == 5 and data[0] == RequestType_Data and data[1] == EntityType_InterfaceValueOfState

    def control(self, data: bytearray):
        self.renderer.render("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        statePageNo = data[4]
        instanceId = instanceIdHigh*256 + instanceIdLow
        if instanceId == 0x01:
            if statePageNo == 0x00:
                self.renderer.render("titleTxt.txt=\"Recuperator\"")
                self.renderer.render("intValTxt.txt=\"II gear\"")
                self.renderer.render("vis markerTxt,1")
                self.imageRenderer.renderImageToNextion(63, 47, "atticIcon")

                self.renderer.render("vis slot0Btn,1")
                self.renderer.render("slot0Btn.txt=\"Gear I\"")
                self.renderer.render("vis slot1Btn,1")
                self.renderer.render("slot1Btn.txt=\"Gear II\"")
                self.renderer.render("vis slot2Btn,1")
                self.renderer.render("slot2Btn.txt=\"Gear III\"")
                self.renderer.render("vis slot3Btn,1")
                self.renderer.render("slot3Btn.txt=\"Gear IV\"")
                self.renderer.render("vis slot4Btn,1")
                self.renderer.render("slot4Btn.txt=\"Gear V\"")
                self.renderer.render("vis slot5Btn,1")
                self.renderer.render("slot5Btn.txt=\"Gear VI\"")
                self.renderer.render("vis pageUpBtn,1")
                self.renderer.render("pageUpBtn.pco=42260")
                self.renderer.render("tsw pageUpBtn,0")
                self.renderer.render("vis pageDownBtn,1")
            else:
                self.renderer.render("vis slot0Btn,1")
                self.renderer.render("slot0Btn.txt=\"Gear VII\"")
                self.renderer.render("vis slot1Btn,1")
                self.renderer.render("slot1Btn.txt=\"Gear VIII\"")
                self.renderer.render("vis slot2Btn,0")
                self.renderer.render("vis slot3Btn,0")
                self.renderer.render("vis slot4Btn,0")
                self.renderer.render("vis slot5Btn,0")
                self.renderer.render("vis pageUpBtn,1")
                self.renderer.render("pageUpBtn.pco=0")
                self.renderer.render("tsw pageUpBtn,1")
                self.renderer.render("vis pageDownBtn,0")

        else:
            if instanceId == 0x02:
                self.renderer.render("titleTxt.txt=\"Radiator valve\"")
                self.renderer.render("intValTxt.txt=\"Regulation\"")
                self.renderer.render("vis markerTxt,0")
                self.imageRenderer.renderImageToNextion(63, 47, "buttonIcon")

        self.renderer.render("vis loadingBtn,0")


class InboxDetailsNVM(NextionViewModel):
    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_InboxBody
    
    def control(self, data: bytearray):
        messageId = data[2]
        print("Displaying details of message {}".format(messageId))
        self.renderer.render("subjectTxt.txt=\"This is message subject\"")
        self.renderer.render("timeTxt.txt=\"5m ago\"")
        self.renderer.render("bodyTxt.txt=\"This is message body, a very, very, very long one... Lorem ipsum et dolores colorez\"")
        self.renderer.render("vis loadingBtn,0")


class InboxNVM(NextionViewModel):
    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_InboxSubjects

    def control(self, data: bytearray):
        page = data[2]
        if page == 0x00:
            self.renderer.render("vis slot0Btn,1")
            self.renderer.render("slot0Btn.txt=\"Thank you for choosing Automate Everything\"")
            self.renderer.render("slot0Btn.font=2")

            self.renderer.render("vis slot1Btn,1")
            self.renderer.render("slot1Btn.txt=\"Automation enabled\"")
            self.renderer.render("slot1Btn.font=2")

            self.renderer.render("vis slot2Btn,1")
            self.renderer.render("slot2Btn.txt=\"Automation disabled\"")
            self.renderer.render("slot2Btn.font=1")

            self.renderer.render("vis slot3Btn,1")
            self.renderer.render("slot3Btn.txt=\"A problem with sensor one\"")
            self.renderer.render("slot3Btn.font=1")

            self.renderer.render("vis slot4Btn,1")
            self.renderer.render("slot4Btn.txt=\"A problem with sensor two\"")
            self.renderer.render("slot4Btn.font=1")

            self.renderer.render("vis slot5Btn,1")
            self.renderer.render("slot5Btn.txt=\"A problem with sensor three\"")
            self.renderer.render("slot5Btn.font=1")

            self.renderer.render("vis slot6Btn,1")
            self.renderer.render("slot6Btn.txt=\"System is DOWN\"")
            self.renderer.render("slot6Btn.font=1")

            self.renderer.render("vis slot7Btn,1")
            self.renderer.render("slot7Btn.txt=\"System is UP\"")
            self.renderer.render("slot7Btn.font=1")

            self.renderer.render("vis prevPageBtn,0")
            self.renderer.render("vis nextPageBtn,1")
            self.renderer.render("vis loadingBtn,0")
        else:
            self.renderer.render("vis slot0Btn,1")
            self.renderer.render("slot0Btn.txt=\"Page 2, message 1\"")
            self.renderer.render("slot0Btn.font=2")

            self.renderer.render("vis slot1Btn,1")
            self.renderer.render("slot1Btn.txt=\"Page 2, message 2\"")
            self.renderer.render("slot1Btn.font=2")

            self.renderer.render("vis slot2Btn,0")
            self.renderer.render("vis slot3Btn,0")
            self.renderer.render("vis slot4Btn,0")
            self.renderer.render("vis slot5Btn,0")
            self.renderer.render("vis slot6Btn,0")
            self.renderer.render("vis slot7Btn,0")

            self.renderer.render("vis prevPageBtn,1")
            self.renderer.render("vis nextPageBtn,0")
            self.renderer.render("vis loadingBtn,0")


class StateSelectedNVM(NextionViewModel):
    def checkMatch(self, data: bytearray):
        return len(data) == 5 and data[0] == RequestType_UISelection and data[1] == EntityType_StateSelection

    def control(self, data: bytearray):
        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh*256 + instanceIdLow
        stateSlotNo = data[4]
        print("State selected, instance id={}, state slot no={}".format(instanceId, stateSlotNo))
        self.renderer.render("page control")


class WifiPasswordNVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN, credentialsManager: CredentialsManager):
        super().__init__(renderer)
        self.wlan = wlan
        self.credentialsManager = credentialsManager

    def checkMatch(self, data: bytearray):
        return len(data) > 2 and data[0] == RequestType_UISelection and data[1] == EntityType_WiFiPassword

    def control(self, data: bytearray):
        password = data[2:]
        print("Typed password={}".format(password))
        self.credentialsManager.storePassword(password)
        self.renderer.render("page connecting")

        self.wlan.disconnect()
        self.wlan.connect(self.credentialsManager.ssid.decode('utf-8'), self.credentialsManager.password.decode('utf-8'))

        for x in range(1, 10):
            print("Checking network connection {}".format(x))
            time.sleep(1)
            if self.wlan.isconnected():
                break

        if self.wlan.isconnected():
            self.renderer.render("page control")
        else:
            self.renderer.render("page connectionLost")


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


class WiFiSsidNVM(NextionViewModel):
    def __init__(self, renderer: NextionRenderer, credentialsManager: CredentialsManager):
        super().__init__(renderer)
        self.credentialsManager = credentialsManager

    def checkMatch(self, data: bytearray):
        return len(data) > 2 and data[0] == RequestType_UISelection and data[1] == EntityType_SSIDSelection
    
    def control(self, data: bytearray):
        ssid = data[2:]
        print("Selected ssid={}".format(ssid))
        self.credentialsManager.storeSsid(ssid)
        self.renderer.render("page wifiPassword")


class LanguageSelectVM(NextionViewModel):

    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_UISelection and data[1] == EntityType_LanguageSelection

    def control(self, data: bytearray):
        lang = data[2]
        f = open('lang','w')
        f.write(str(lang))
        f.close()


class LeftButtonConfigNVM(NextionViewModel):

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_UISelection and data[1] == EntityType_LeftButtonConfig

    def control(self, data: bytearray):
        action = data[2]
        time = data[3]
        print("Left button configured, action: {}, time: {}".format(action, time))


class RightButtonConfigNVM(NextionViewModel):

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_UISelection and data[1] == EntityType_RightButtonConfig

    def control(self, data: bytearray):
        action = data[2]
        time = data[3]
        print("Right button configured, action: {}, time: {}".format(action, time))


class AutomateEverythingCommandsProcessor(CommandsProcessor):

    def __init__(self, renderer: NextionRenderer, wlan: network.WLAN, imageRenderer: NextionImageRenderer, credentialsManager: CredentialsManager) -> None:
        self.processors = []

        colorSelectedNVM = ColorSelectedNVM(renderer)
        self.processors.append(colorSelectedNVM)

        controlColorNVM = ControlColorNVM(renderer, imageRenderer)
        self.processors.append(controlColorNVM)

        controlControllerNVM = ControlControllerNVM(renderer, imageRenderer)
        self.processors.append(controlControllerNVM)

        controllerSelectedNVM = ControllerSelectedNVM(renderer)
        self.processors.append(controllerSelectedNVM)

        controlNVM = ControlNVM(renderer, imageRenderer)
        self.processors.append(controlNVM)

        controlStateNVM = ControlStateNVM(renderer, imageRenderer)
        self.processors.append(controlStateNVM)

        inboxDetailsNVM = InboxDetailsNVM(renderer)
        self.processors.append(inboxDetailsNVM)
        
        inboxNVM = InboxNVM(renderer)
        self.processors.append(inboxNVM)
        
        stateSelectedNVM = StateSelectedNVM(renderer)
        self.processors.append(stateSelectedNVM)

        wiFiPasswordNVM = WifiPasswordNVM(renderer, wlan, credentialsManager)
        self.processors.append(wiFiPasswordNVM)

        wifiScanNVM = WiFiScanNVM(renderer, wlan)
        self.processors.append(wifiScanNVM)

        wiFiSsidNVM = WiFiSsidNVM(renderer, credentialsManager)
        self.processors.append(wiFiSsidNVM)

        languageSelectNVM = LanguageSelectVM(renderer)
        self.processors.append(languageSelectNVM)

        leftButtonConfigNVM = LeftButtonConfigNVM(renderer)
        self.processors.append(leftButtonConfigNVM)

        rightButtonConfigNVM = RightButtonConfigNVM(renderer)
        self.processors.append(rightButtonConfigNVM)


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
