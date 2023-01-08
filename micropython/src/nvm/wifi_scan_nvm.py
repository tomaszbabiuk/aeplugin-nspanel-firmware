from nextion import *
from ae import *

import network

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
