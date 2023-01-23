import json
from micropython import const

Config_Filename = const("config.json")
Field_Language = const("lang")
Field_SSID = const("ssid")
Field_Password = const("password")
Field_LeftButtonAction = const("leftButtonAction")
Field_LeftButtonTimeInSec = const("leftButtonTimeInSec")
Field_RightButtonAction = const("rightButtonAction")
Field_RightButtonTimeInSec = const("rightButtonTimeInSec")


class ConfigManager:
    def __init__(self) -> None:
        self.password = bytearray()
        self.ssid = bytearray()
        self.lang = 0
        self.leftButtonAction = 0
        self.leftButtonTime = 0
        self.rightButtonAction = 0
        self.rightButtonTime = 0

    def setPassword(self, password: bytearray) -> None:
        self.password = password

    def getPassword(self) -> str:
        return self.password.decode('utf-8')

    def setSsid(self, ssid: bytearray) -> None:
        self.ssid = ssid

    def getSsid(self) -> str:
        return self.ssid.decode('utf-8')

    def setLanguage(self, lang: int) -> None:
        self.lang = lang

    def setLeftButtonConfig(self, action: int, time: int) -> None:
        self.leftButtonAction = action
        self.leftButtonTime = time

    def setRightButtonConfig(self, action: int, time: int) -> None:
        self.rightButtonAction = action
        self.rightButtonTime = time

    def save(self) -> None:
        config = { Field_Language: self.lang, Field_SSID: str(self.ssid), Field_Password: str(self.password), Field_LeftButtonAction: self.leftButtonAction, Field_LeftButtonTimeInSec: self.leftButtonTime, Field_RightButtonAction: self.rightButtonAction, Field_RightButtonTimeInSec: self.rightButtonTime }

        with open(Config_Filename, "w") as config_file:
            json.dump(config, config_file)
        pass

    def load(self):
        with open(Config_Filename, "r") as config_file:
            config = json.load(config_file)
            
            self.language = config[Field_Language]
            print(self.language)

            self.ssid = config[Field_SSID]
            print(self.ssid)
            # print("LeftButtonAction: {}".format(config[Field_Language]))
            # print("LeftButtonTime: {}".format(config[Field_Language]))
            # print("RightButtonAction: {}".format(config[Field_Language]))
            # print("LeftButtonTime: {}".format(config[Field_Language]))