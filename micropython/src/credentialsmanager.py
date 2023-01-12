
class CredentialsManager:
    def __init__(self) -> None:
        self.password = bytearray()
        self.ssid = bytearray()

    def storePassword(self, password: bytearray) -> None:
        self.password = password
        f = open('password','w')
        f.write(str(password))
        f.close()

    def storeSsid(self, ssid: bytearray) -> None:
        self.ssid = ssid
        f = open('ssid','w')
        f.write(str(ssid))
        f.close()