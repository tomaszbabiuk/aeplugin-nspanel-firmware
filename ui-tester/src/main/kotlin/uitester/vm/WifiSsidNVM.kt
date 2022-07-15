package uitester.vm

import NextionRenderer
import RendereableNVM

class WifiSsidNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {
    override fun checkMatch(data: ByteArray): Boolean {
        return data.size > 2 && data[0] == 0x01.toByte() && data[1] == 0x01.toByte()
    }

    override fun control(data: ByteArray) {
        val ssid = String(data.drop(2).toByteArray())
        println("Selected ssid=$ssid")
        renderer.render("page wifiPassword")
    }
}