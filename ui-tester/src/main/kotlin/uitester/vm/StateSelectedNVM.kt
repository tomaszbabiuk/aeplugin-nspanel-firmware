package uitester.vm

import NextionRenderer
import RendereableNVM

class StateSelectedNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {
    override fun checkMatch(data: ByteArray): Boolean {
        return data.size == 4 && data[0] == 0x01.toByte() && data[1] == 0x07.toByte()
    }

    override fun control(data:ByteArray) {
        val instanceId = data[2]
        val slotId = data[3]
        println("State selected, instance id=$instanceId, slot id=$slotId")
        renderer.render("page control")
    }
}