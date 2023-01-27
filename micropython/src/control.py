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

class NextionImagewriter:
    def __init__(self, writer: NextionWriter, iconResolver: IconResolver) -> None:
        self.writer = writer
        self.iconResolver = iconResolver

    def renderImageToNextion(self, xRel: int, yRel: int, name):
        lines = self.iconResolver.resolve(name)
        for it in lines:
            line = "line {},{},{},{},WHITE".format(xRel + it[0], yRel + it[1], xRel + it[2], yRel + it[3])
            self.writer.render(line)


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
        self.writer.render("page control")


class ControlColorNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImagewriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_Data and data[1] == EntityType_InterfaceValueOfColor

    def act(self, data: bytearray):
        self.writer.render("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh*256 + instanceIdLow
        if instanceId == 0x03:
            self.writer.render('titleTxt.txt="Lamp 20X"')
            self.writer.render("hueSlr.val=124") #min val + 4 steps
            self.writer.render("brightSlr.val=90")
            self.imagewriter.renderImageToNextion(174, 57, "buttonIcon")

        self.writer.render("vis loadingBtn,0")
        self.writer.render("vis applyBtn,1")


class ControlControllerNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImagewriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 4 and data[0] == RequestType_Data and EntityType_InterfaceValueOfController

    def act(self, data: bytearray):
        self.writer.render("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh* 256 + instanceIdLow
        if instanceId == 0x02:
            self.writer.render('titleTxt.txt="Controller 10XPf"')
            self.writer.render('minValTxt.txt="10°C"')
            self.writer.render('maxValTxt.txt="40°C"')
            self.writer.render("vis markerTxt,1")
            self.writer.render('unitTxt.txt="°C"')
            self.writer.render("step.val=50") #0.5°C
            self.writer.render("valSlr.maxval=60") #(40-10)*2... steps per range
            self.writer.render("valSlr.val=4") #min val + 4 steps
            self.writer.render("valueTxt.val=1200")
            self.imagewriter.renderImageToNextion(174, 57, "atticIcon")

        self.writer.render("vis loadingBtn,0")
        self.writer.render("vis applyBtn,1")


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
        self.writer.render("page control")


class ControlNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImagewriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_DevicesPage

    def boolToNumber(self, b: bool):
        if b:
            return 1
        else:
            return 0

    def renderPager(self, prevEnabled: bool, nextEnabled: bool):
        self.writer.render("vis prevPageBtn,{}".format(self.boolToNumber(prevEnabled)))
        self.writer.render("vis nextPageBtn,{}".format(self.boolToNumber(nextEnabled)))
        self.writer.render("vis loadingBtn,0")
    
    def renderEmptySlot(self, slot: int):
        self.writer.render("vis background{}Txt,0".format(slot))
        self.writer.render("vis name{}Txt,0".format(slot))
        self.writer.render("vis desc{}Txt,0".format(slot))
        self.writer.render("vis marker{}Txt,0".format(slot))
        self.writer.render("vis slo${}Btn,0".format(slot))

    def renderControlSlot(self, slot: int, instanceId: int, controlType: int, name: str, description: str, state: str, signaled: bool):
        self.writer.render("instanceId{}.val={}".format(slot, instanceId))
        self.writer.render("vis background{}Txt,1".format(slot))
        self.writer.render("vis name{}Txt,1".format(slot))
        self.writer.render('name{}Txt.txt="{}"'.format(slot, name))
        self.writer.render("vis desc{}Txt,1".format(slot))
        self.writer.render('desc{}Txt.txt="{}"'.format(slot, description))
        self.writer.render("vis marker{}Txt,{}".format(slot, self.boolToNumber(signaled)))
        self.writer.render("vis slot{}Btn,1".format(slot))
        self.writer.render('slot{}Btn.txt="{}"'.format(slot, state))
        self.writer.render("type{}.val={}".format(slot, controlType))

    def act(self, data: bytearray):
        page = data[2]
        if page == 0x00:
            self.renderControlSlot(0, 1,0,"Recuperator", "---", "II gear", True)
            self.renderControlSlot(1, 2,1,"Radiator valve", "Opening state: 12%", "Regulation", False)
            self.renderControlSlot(2, 3,2,"Ceiling lamp", "12W", "On", True)
            self.renderControlSlot(3, 4,0,"Desk lamp", "0W", "Off", False)
            self.renderControlSlot(4, 5,1,"Door", "---", "Closed", False)

            self.imagewriter.renderImageToNextion(65, 47, "atticIcon")
            self.imagewriter.renderImageToNextion(65, 102, "buttonIcon")
            self.imagewriter.renderImageToNextion(65, 157, "boilerIcon")
            self.imagewriter.renderImageToNextion(65, 212, "blindsIcon")
            self.imagewriter.renderImageToNextion(65, 267, "bullhornIcon")
            self.renderPager(prevEnabled = False, nextEnabled = True)
        else:
            self.renderControlSlot(0, 6,0,"Window contactron", "---", "Disarmed", True)
            self.renderControlSlot(1, 7,0,"Motion sensor", "---", "Disarmed", False)
            self.renderEmptySlot(2)
            self.renderEmptySlot(3)
            self.renderEmptySlot(4)

            self.imagewriter.renderImageToNextion(65, 47, "atticIcon")
            self.imagewriter.renderImageToNextion(65, 102, "buttonIcon")
            self.renderPager(prevEnabled = True, nextEnabled = False)


class ControlStateNVM(NextionAction):
    def __init__(self, writer: NextionWriter, imagewriter: NextionImagewriter):
        super().__init__(writer)
        self.imagewriter = imagewriter

    def checkMatch(self, data: bytearray):
        return len(data) == 5 and data[0] == RequestType_Data and data[1] == EntityType_InterfaceValueOfState

    def act(self, data: bytearray):
        self.writer.render("vis loadingBtn,1")

        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        statePageNo = data[4]
        instanceId = instanceIdHigh*256 + instanceIdLow
        if instanceId == 0x01:
            if statePageNo == 0x00:
                self.writer.render("titleTxt.txt=\"Recuperator\"")
                self.writer.render("intValTxt.txt=\"II gear\"")
                self.writer.render("vis markerTxt,1")
                self.imagewriter.renderImageToNextion(63, 47, "atticIcon")

                self.writer.render("vis slot0Btn,1")
                self.writer.render("slot0Btn.txt=\"Gear I\"")
                self.writer.render("vis slot1Btn,1")
                self.writer.render("slot1Btn.txt=\"Gear II\"")
                self.writer.render("vis slot2Btn,1")
                self.writer.render("slot2Btn.txt=\"Gear III\"")
                self.writer.render("vis slot3Btn,1")
                self.writer.render("slot3Btn.txt=\"Gear IV\"")
                self.writer.render("vis slot4Btn,1")
                self.writer.render("slot4Btn.txt=\"Gear V\"")
                self.writer.render("vis slot5Btn,1")
                self.writer.render("slot5Btn.txt=\"Gear VI\"")
                self.writer.render("vis pageUpBtn,1")
                self.writer.render("pageUpBtn.pco=42260")
                self.writer.render("tsw pageUpBtn,0")
                self.writer.render("vis pageDownBtn,1")
            else:
                self.writer.render("vis slot0Btn,1")
                self.writer.render("slot0Btn.txt=\"Gear VII\"")
                self.writer.render("vis slot1Btn,1")
                self.writer.render("slot1Btn.txt=\"Gear VIII\"")
                self.writer.render("vis slot2Btn,0")
                self.writer.render("vis slot3Btn,0")
                self.writer.render("vis slot4Btn,0")
                self.writer.render("vis slot5Btn,0")
                self.writer.render("vis pageUpBtn,1")
                self.writer.render("pageUpBtn.pco=0")
                self.writer.render("tsw pageUpBtn,1")
                self.writer.render("vis pageDownBtn,0")

        else:
            if instanceId == 0x02:
                self.writer.render("titleTxt.txt=\"Radiator valve\"")
                self.writer.render("intValTxt.txt=\"Regulation\"")
                self.writer.render("vis markerTxt,0")
                self.imagewriter.renderImageToNextion(63, 47, "buttonIcon")

        self.writer.render("vis loadingBtn,0")


class InboxDetailsNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_InboxBody
    
    def act(self, data: bytearray):
        messageId = data[2]
        print("Displaying details of message {}".format(messageId))
        self.writer.render("subjectTxt.txt=\"This is message subject\"")
        self.writer.render("timeTxt.txt=\"5m ago\"")
        self.writer.render("bodyTxt.txt=\"This is message body, a very, very, very long one... Lorem ipsum et dolores colorez\"")
        self.writer.render("vis loadingBtn,0")


class InboxNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 3 and data[0] == RequestType_Data and data[1] == EntityType_InboxSubjects

    def act(self, data: bytearray):
        page = data[2]
        if page == 0x00:
            self.writer.render("vis slot0Btn,1")
            self.writer.render("slot0Btn.txt=\"Thank you for choosing Automate Everything\"")
            self.writer.render("slot0Btn.font=2")

            self.writer.render("vis slot1Btn,1")
            self.writer.render("slot1Btn.txt=\"Automation enabled\"")
            self.writer.render("slot1Btn.font=2")

            self.writer.render("vis slot2Btn,1")
            self.writer.render("slot2Btn.txt=\"Automation disabled\"")
            self.writer.render("slot2Btn.font=1")

            self.writer.render("vis slot3Btn,1")
            self.writer.render("slot3Btn.txt=\"A problem with sensor one\"")
            self.writer.render("slot3Btn.font=1")

            self.writer.render("vis slot4Btn,1")
            self.writer.render("slot4Btn.txt=\"A problem with sensor two\"")
            self.writer.render("slot4Btn.font=1")

            self.writer.render("vis slot5Btn,1")
            self.writer.render("slot5Btn.txt=\"A problem with sensor three\"")
            self.writer.render("slot5Btn.font=1")

            self.writer.render("vis slot6Btn,1")
            self.writer.render("slot6Btn.txt=\"System is DOWN\"")
            self.writer.render("slot6Btn.font=1")

            self.writer.render("vis slot7Btn,1")
            self.writer.render("slot7Btn.txt=\"System is UP\"")
            self.writer.render("slot7Btn.font=1")

            self.writer.render("vis prevPageBtn,0")
            self.writer.render("vis nextPageBtn,1")
            self.writer.render("vis loadingBtn,0")
        else:
            self.writer.render("vis slot0Btn,1")
            self.writer.render("slot0Btn.txt=\"Page 2, message 1\"")
            self.writer.render("slot0Btn.font=2")

            self.writer.render("vis slot1Btn,1")
            self.writer.render("slot1Btn.txt=\"Page 2, message 2\"")
            self.writer.render("slot1Btn.font=2")

            self.writer.render("vis slot2Btn,0")
            self.writer.render("vis slot3Btn,0")
            self.writer.render("vis slot4Btn,0")
            self.writer.render("vis slot5Btn,0")
            self.writer.render("vis slot6Btn,0")
            self.writer.render("vis slot7Btn,0")

            self.writer.render("vis prevPageBtn,1")
            self.writer.render("vis nextPageBtn,0")
            self.writer.render("vis loadingBtn,0")


class StateSelectedNVM(NextionAction):
    def checkMatch(self, data: bytearray):
        return len(data) == 5 and data[0] == RequestType_UISelection and data[1] == EntityType_StateSelection

    def act(self, data: bytearray):
        instanceIdLow = data[2]
        instanceIdHigh = data[3]
        instanceId = instanceIdHigh*256 + instanceIdLow
        stateSlotNo = data[4]
        print("State selected, instance id={}, state slot no={}".format(instanceId, stateSlotNo))
        self.writer.render("page control")


def createControlActions(actionsBag, writer: NextionWriter):
    iconResolver = IconResolver()
    imagewriter = NextionImagewriter(writer, iconResolver)
    
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
