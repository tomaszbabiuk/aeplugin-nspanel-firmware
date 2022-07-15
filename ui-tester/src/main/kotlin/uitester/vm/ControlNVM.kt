package uitester.vm

import NextionRenderer
import RendereableNVM

class ControlNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {

    override fun checkMatch(data: ByteArray): Boolean {
        return data.size == 3 && data[0] == 0x00.toByte() && data[1] == 0x05.toByte()
    }

    override fun control(data: ByteArray) {
        val page = data[2]
        if (page == 0x00.toByte()) {
            renderControlSlot(0, "Recuperator", "---", "II gear", true)
            renderControlSlot(1, "Radiator valve", "Opening state: 12%", "Regulation", false)
            renderControlSlot(2, "Ceiling lamp", "12W", "On", true)
            renderControlSlot(3, "Desk lamp", "0W", "Off", false)
            renderControlSlot(4, "Door", "---", "Closed", false)
            renderPager(prevEnabled = false, nextEnabled = true)
        } else {
            renderControlSlot(0, "Window contactron", "---", "Disarmed", true)
            renderControlSlot(1, "Motion sensor", "---", "Disarmed", false)
            renderEmptySlot(2)
            renderEmptySlot(3)
            renderEmptySlot(4)
            renderPager(prevEnabled = true, nextEnabled = false)
        }
    }

    private fun renderControlSlot(slot: Int, name: String, description: String, state: String, signaled: Boolean) {
        renderer.render("vis background${slot}Txt,1")
        renderer.render("vis name${slot}Txt,1")
        renderer.render("name${slot}Txt.txt=\"${name}\"")
        renderer.render("vis desc${slot}Txt,1")
        renderer.render("desc${slot}Txt.txt=\"${description}\"")
        renderer.render("vis marker${slot}Txt,${if (signaled) "1" else "0"}")
        renderer.render("vis icon${slot}Pct,1")
        renderer.render("vis slot${slot}Btn,1")
        renderer.render("slot${slot}Btn.txt=\"${state}\"")
    }

    private fun renderEmptySlot(slot: Int) {
        renderer.render("vis background${slot}Txt,0")
        renderer.render("vis name${slot}Txt,0")
        renderer.render("vis desc${slot}Txt,0")
        renderer.render("vis marker${slot}Txt,0")
        renderer.render("vis icon${slot}Pct,0")
        renderer.render("vis slot${slot}Btn,0")
    }

    private fun renderPager(prevEnabled: Boolean, nextEnabled: Boolean) {
        renderer.render("vis prevPageBtn,${if (prevEnabled) "1" else "0"}")
        renderer.render("vis nextPageBtn,${if (nextEnabled) "1" else "0"}")
        renderer.render("vis loadingBtn,0")
    }
}