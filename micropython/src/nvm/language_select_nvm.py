from nextion import *
from ae import *

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