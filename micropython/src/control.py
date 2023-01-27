from micropython import const
from config import ConfigManager
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
EntityType_Scaning = const(0x10)
EntityType_InterfaceValueOfColor = const(0x0A)
EntityType_ColorSelection = const(0x0B)
EntityType_LanguageSelection = const(0x0C)
EntityType_ConnectionState = const(0x0D)
EntityType_LeftButtonConfig = const(0x0E)
EntityType_RightButtonConfig = const(0x0F)
EntityType_ReadyToUpgrade = const(0x10)

class IconResolver:
    def resolve(self, name: str):
        # TODO
        #     x0  x1  y1  y2
        p1 = (10, 10, 20, 20)
        p2 = (15, 15, 30, 30)
        return [p1, p2]

class NextionImageWriter:
    def __init__(self, writer: NextionWriter, iconResolver: IconResolver) -> None:
        self.writer = writer
        self.iconResolver = iconResolver

    def writeImage(self, xRel: int, yRel: int, name):
        lines = self.iconResolver.resolve(name)
        for it in lines:
            line = "line {},{},{},{},WHITE".format(xRel + it[0], yRel + it[1], xRel + it[2], yRel + it[3])
            self.writer.write(line)


class ColorSelectedNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 7 and data[0] == RequestType_UISelection and data[1] == EntityType_ColorSelection

    def act(self, data: bytearray):
        instanceIdLSB = data[2]
        instanceIdMSB = data[3]
        instanceId = instanceIdMSB*256 + instanceIdLSB
        valueHueLSB = data[4]
        valueHueMSB = data[5]
        valueHue = valueHueMSB*256 + valueHueLSB
        valueBrightness = data[6]
        print("Color selected, instance id={}, hue={}, brightness={}".format(instanceId, valueHue, valueBrightness))
        self.writer.write("page control")


class ControlColorNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImageWriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_Data and data[1] == EntityType_InterfaceValueOfColor

    def act(self, data: bytearray):
        self.writer.write("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh*256 + instanceIdLow
        if instanceId == 0x03:
            self.writer.write('titleTxt.txt="Lamp 20X"')
            self.writer.write("hueSlr.val=124") #min val + 4 steps
            self.writer.write("brightSlr.val=90")
            self.imagewriter.writeImage(174, 57, "buttonIcon")

        self.writer.write("vis loadingBtn,0")
        self.writer.write("vis applyBtn,1")


class ControlControllerNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImageWriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_Data and EntityType_InterfaceValueOfController

    def act(self, data: bytearray):
        self.writer.write("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh* 256 + instanceIdLow
        if instanceId == 0x02:
            self.writer.write('titleTxt.txt="Controller 10XPf"')
            self.writer.write('minValTxt.txt="10°C"')
            self.writer.write('maxValTxt.txt="40°C"')
            self.writer.write("vis markerTxt,1")
            self.writer.write('unitTxt.txt="°C"')
            self.writer.write("step.val=50") #0.5°C
            self.writer.write("valSlr.maxval=60") #(40-10)*2... steps per range
            self.writer.write("valSlr.val=4") #min val + 4 steps
            self.writer.write("valueTxt.val=1200")
            self.imagewriter.writeImage(174, 57, "atticIcon")

        self.writer.write("vis loadingBtn,0")
        self.writer.write("vis applyBtn,1")


class ControllerSelectedNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 8 and data[0] == RequestType_UISelection and data[1] == EntityType_ValueSelection

    def act(self, data: bytearray):
        instanceIdLSB = data[2]
        instanceIdMSB = data[3]
        instanceId = instanceIdMSB*256 + instanceIdLSB
        valueLSB = data[4]
        valueB2 = data[5]
        valueB3 = data[6]
        valueMSB = data[7]
        value = valueMSB* 16777216 + valueB3*65536 + valueB2*256 + valueLSB
        print("Value selected, instance id={}, value={}".format(instanceId, value))
        self.writer.write("page control")


class ControlNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImageWriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_DevicesPage

    def boolToNumber(self, b: bool):
        if b:
            return 1
        else:
            return 0

    def writePager(self, prevEnabled: bool, nextEnabled: bool):
        self.writer.write("vis prevPageBtn,{}".format(self.boolToNumber(prevEnabled)))
        self.writer.write("vis nextPageBtn,{}".format(self.boolToNumber(nextEnabled)))
        self.writer.write("vis loadingBtn,0")
    
    def writeEmptySlot(self, slot: int):
        self.writer.write("vis background{}Txt,0".format(slot))
        self.writer.write("vis name{}Txt,0".format(slot))
        self.writer.write("vis desc{}Txt,0".format(slot))
        self.writer.write("vis marker{}Txt,0".format(slot))
        self.writer.write("vis slo${}Btn,0".format(slot))

    def writeControlSlot(self, slot: int, instanceId: int, controlType: int, name: str, description: str, state: str, signaled: bool):
        self.writer.write("instanceId{}.val={}".format(slot, instanceId))
        self.writer.write("vis background{}Txt,1".format(slot))
        self.writer.write("vis name{}Txt,1".format(slot))
        self.writer.write('name{}Txt.txt="{}"'.format(slot, name))
        self.writer.write("vis desc{}Txt,1".format(slot))
        self.writer.write('desc{}Txt.txt="{}"'.format(slot, description))
        self.writer.write("vis marker{}Txt,{}".format(slot, self.boolToNumber(signaled)))
        self.writer.write("vis slot{}Btn,1".format(slot))
        self.writer.write('slot{}Btn.txt="{}"'.format(slot, state))
        self.writer.write("type{}.val={}".format(slot, controlType))

    def act(self, data: bytearray):
        page = data[2]
        if page == 0x00:
            self.writeControlSlot(0, 1,0,"Recuperator", "---", "II gear", True)
            self.writeControlSlot(1, 2,1,"Radiator valve", "Opening state: 12%", "Regulation", False)
            self.writeControlSlot(2, 3,2,"Ceiling lamp", "12W", "On", True)
            self.writeControlSlot(3, 4,0,"Desk lamp", "0W", "Off", False)
            self.writeControlSlot(4, 5,1,"Door", "---", "Closed", False)

            self.imagewriter.writeImage(65, 47, "atticIcon")
            self.imagewriter.writeImage(65, 102, "buttonIcon")
            self.imagewriter.writeImage(65, 157, "boilerIcon")
            self.imagewriter.writeImage(65, 212, "blindsIcon")
            self.imagewriter.writeImage(65, 267, "bullhornIcon")
            self.writePager(prevEnabled = False, nextEnabled = True)
        else:
            self.writeControlSlot(0, 6,0,"Window contactron", "---", "Disarmed", True)
            self.writeControlSlot(1, 7,0,"Motion sensor", "---", "Disarmed", False)
            self.writeEmptySlot(2)
            self.writeEmptySlot(3)
            self.writeEmptySlot(4)

            self.imagewriter.writeImage(65, 47, "atticIcon")
            self.imagewriter.writeImage(65, 102, "buttonIcon")
            self.writePager(prevEnabled = True, nextEnabled = False)


class ControlStateNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImageWriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 5 and data[0] == RequestType_Data and data[1] == EntityType_InterfaceValueOfState

    def act(self, data: bytearray):
        self.writer.write("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        statePageNo = data[4]
        instanceId = instanceIdHigh*256 + instanceIdLow
        if instanceId == 0x01:
            if statePageNo == 0x00:
                self.writer.write("titleTxt.txt=\"Recuperator\"")
                self.writer.write("intValTxt.txt=\"II gear\"")
                self.writer.write("vis markerTxt,1")
                self.imagewriter.writeImage(63, 47, "atticIcon")

                self.writer.write("vis slot0Btn,1")
                self.writer.write("slot0Btn.txt=\"Gear I\"")
                self.writer.write("vis slot1Btn,1")
                self.writer.write("slot1Btn.txt=\"Gear II\"")
                self.writer.write("vis slot2Btn,1")
                self.writer.write("slot2Btn.txt=\"Gear III\"")
                self.writer.write("vis slot3Btn,1")
                self.writer.write("slot3Btn.txt=\"Gear IV\"")
                self.writer.write("vis slot4Btn,1")
                self.writer.write("slot4Btn.txt=\"Gear V\"")
                self.writer.write("vis slot5Btn,1")
                self.writer.write("slot5Btn.txt=\"Gear VI\"")
                self.writer.write("vis pageUpBtn,1")
                self.writer.write("pageUpBtn.pco=42260")
                self.writer.write("tsw pageUpBtn,0")
                self.writer.write("vis pageDownBtn,1")
            else:
                self.writer.write("vis slot0Btn,1")
                self.writer.write("slot0Btn.txt=\"Gear VII\"")
                self.writer.write("vis slot1Btn,1")
                self.writer.write("slot1Btn.txt=\"Gear VIII\"")
                self.writer.write("vis slot2Btn,0")
                self.writer.write("vis slot3Btn,0")
                self.writer.write("vis slot4Btn,0")
                self.writer.write("vis slot5Btn,0")
                self.writer.write("vis pageUpBtn,1")
                self.writer.write("pageUpBtn.pco=0")
                self.writer.write("tsw pageUpBtn,1")
                self.writer.write("vis pageDownBtn,0")

        else:
            if instanceId == 0x02:
                self.writer.write("titleTxt.txt=\"Radiator valve\"")
                self.writer.write("intValTxt.txt=\"Regulation\"")
                self.writer.write("vis markerTxt,0")
                self.imagewriter.writeImage(63, 47, "buttonIcon")

        self.writer.write("vis loadingBtn,0")


class InboxDetailsNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_InboxBody
    
    def act(self, data: bytearray):
        messageId = data[2]
        print("Displaying details of message {}".format(messageId))
        self.writer.write("subjectTxt.txt=\"This is message subject\"")
        self.writer.write("timeTxt.txt=\"5m ago\"")
        self.writer.write("bodyTxt.txt=\"This is message body, a very, very, very long one... Lorem ipsum et dolores colorez\"")
        self.writer.write("vis loadingBtn,0")


class InboxNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_InboxSubjects

    def act(self, data: bytearray):
        page = data[2]
        if page == 0x00:
            self.writer.write("vis slot0Btn,1")
            self.writer.write("slot0Btn.txt=\"Thank you for choosing Automate Everything\"")
            self.writer.write("slot0Btn.font=2")

            self.writer.write("vis slot1Btn,1")
            self.writer.write("slot1Btn.txt=\"Automation enabled\"")
            self.writer.write("slot1Btn.font=2")

            self.writer.write("vis slot2Btn,1")
            self.writer.write("slot2Btn.txt=\"Automation disabled\"")
            self.writer.write("slot2Btn.font=1")

            self.writer.write("vis slot3Btn,1")
            self.writer.write("slot3Btn.txt=\"A problem with sensor one\"")
            self.writer.write("slot3Btn.font=1")

            self.writer.write("vis slot4Btn,1")
            self.writer.write("slot4Btn.txt=\"A problem with sensor two\"")
            self.writer.write("slot4Btn.font=1")

            self.writer.write("vis slot5Btn,1")
            self.writer.write("slot5Btn.txt=\"A problem with sensor three\"")
            self.writer.write("slot5Btn.font=1")

            self.writer.write("vis slot6Btn,1")
            self.writer.write("slot6Btn.txt=\"System is DOWN\"")
            self.writer.write("slot6Btn.font=1")

            self.writer.write("vis slot7Btn,1")
            self.writer.write("slot7Btn.txt=\"System is UP\"")
            self.writer.write("slot7Btn.font=1")

            self.writer.write("vis prevPageBtn,0")
            self.writer.write("vis nextPageBtn,1")
            self.writer.write("vis loadingBtn,0")
        else:
            self.writer.write("vis slot0Btn,1")
            self.writer.write("slot0Btn.txt=\"Page 2, message 1\"")
            self.writer.write("slot0Btn.font=2")

            self.writer.write("vis slot1Btn,1")
            self.writer.write("slot1Btn.txt=\"Page 2, message 2\"")
            self.writer.write("slot1Btn.font=2")

            self.writer.write("vis slot2Btn,0")
            self.writer.write("vis slot3Btn,0")
            self.writer.write("vis slot4Btn,0")
            self.writer.write("vis slot5Btn,0")
            self.writer.write("vis slot6Btn,0")
            self.writer.write("vis slot7Btn,0")

            self.writer.write("vis prevPageBtn,1")
            self.writer.write("vis nextPageBtn,0")
            self.writer.write("vis loadingBtn,0")


class StateSelectedNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 5 and data[0] == RequestType_UISelection and data[1] == EntityType_StateSelection

    def act(self, data: bytearray):
        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh*256 + instanceIdLow
        stateSlotNo = data[4]
        print("State selected, instance id={}, state slot no={}".format(instanceId, stateSlotNo))
        self.writer.write("page control")


def createControlActions(actionsBag, writer: NextionWriter):
    iconResolver = IconResolver()
    imagewriter = NextionImageWriter(writer, iconResolver)
    
    colorSelectedNVM = ColorSelectedNVM(writer)
    actionsBag.append(colorSelectedNVM)

    controlColorNVM = ControlColorNVM(writer, imagewriter)
    actionsBag.append(controlColorNVM)

    controlControllerNVM = ControlControllerNVM(writer, imagewriter)
    actionsBag.append(controlControllerNVM)

    controllerSelectedNVM = ControllerSelectedNVM(writer)
    actionsBag.append(controllerSelectedNVM)

    controlNVM = ControlNVM(writer, imagewriter)
    actionsBag.append(controlNVM)

    controlStateNVM = ControlStateNVM(writer, imagewriter)
    actionsBag.append(controlStateNVM)

    inboxDetailsNVM = InboxDetailsNVM(writer)
    actionsBag.append(inboxDetailsNVM)
    
    inboxNVM = InboxNVM(writer)
    actionsBag.append(inboxNVM)
    
    stateSelectedNVM = StateSelectedNVM(writer)
    actionsBag.append(stateSelectedNVM)
