package uitester.vm

import NextionRenderer
import RendereableNVM

class WifiPasswordNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {
    override fun checkMatch(data: ByteArray): Boolean {
        return data.size > 2 && data[0] == 0x01.toByte() && data[1] == 0x02.toByte()
    }

    override fun control(data: ByteArray) {
        val password = String(data.drop(2).toByteArray())
        println("Typed password=$password")
        renderer.render("page connecting")

        Thread.sleep(3000)

        renderer.render("page control")
    }
}