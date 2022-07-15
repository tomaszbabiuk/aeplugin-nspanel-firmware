package uitester.vm

import NextionRenderer
import RendereableNVM

class WifiScanNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {
    override fun checkMatch(data: ByteArray): Boolean {
        return data.size == 2 && data[0] == 0x00.toByte() && data[1] == 0x00.toByte()
    }

    override fun control(data:ByteArray) {
        renderer.render("wifiSsid.scanResult.txt=\"network1;network2;network3\"")
        renderer.render("page wifiSsid")
    }
}