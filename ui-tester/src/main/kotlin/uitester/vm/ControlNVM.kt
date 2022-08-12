package uitester.vm

import EntityType
import NextionRenderer
import RendereableNVM
import SvgToNextionConverter
import Point

class ControlNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {

    private val svgToNextion = SvgToNextionConverter()
    val atticIcon = svgToNextion.convert("C:\\Users\\tombab\\Downloads\\attic.svg", 40f, 40f)
    val buttonIcon = svgToNextion.convert("C:\\Users\\tombab\\Downloads\\button.svg", 40f, 40f)
    val boilerIcon = svgToNextion.convert("C:\\Users\\tombab\\Downloads\\boiler.svg", 40f, 40f)
    val blindsIcon = svgToNextion.convert("C:\\Users\\tombab\\Downloads\\blinds.svg", 40f, 40f)
    val bullhornIcon = svgToNextion.convert("C:\\Users\\tombab\\Downloads\\bullhorn.svg", 40f, 40f)

    private fun renderImageToNextion(xRel: Int, yRel: Int, points: List<Point>) {
        points.forEach {
            val line = "line ${xRel + it.x0},${yRel + it.y0},${xRel + it.x1},${yRel + it.y1},WHITE"
            renderer.render(line)
        }
    }

    override fun checkMatch(data: ByteArray): Boolean {
        return data.size == 3 && data[0] == RequestType.Data.dataByte && data[1] == EntityType.DevicesPage.dataByte
    }

    override fun control(data: ByteArray) {
        val page = data[2]
        if (page == 0x00.toByte()) {
            renderControlSlot(0, 1,0,"Recuperator", "---", "II gear", true)
            renderControlSlot(1, 2,1,"Radiator valve", "Opening state: 12%", "Regulation", false)
            renderControlSlot(2, 3,2,"Ceiling lamp", "12W", "On", true)
            renderControlSlot(3, 4,0,"Desk lamp", "0W", "Off", false)
            renderControlSlot(4, 5,1,"Door", "---", "Closed", false)

            renderImageToNextion(65, 47, atticIcon)
            renderImageToNextion(65, 102, buttonIcon)
            renderImageToNextion(65, 157, boilerIcon)
            renderImageToNextion(65, 212, blindsIcon)
            renderImageToNextion(65, 267, bullhornIcon)
            renderPager(prevEnabled = false, nextEnabled = true)
        } else {
            renderControlSlot(0, 6,0,"Window contactron", "---", "Disarmed", true)
            renderControlSlot(1, 7,0,"Motion sensor", "---", "Disarmed", false)
            renderEmptySlot(2)
            renderEmptySlot(3)
            renderEmptySlot(4)

            renderImageToNextion(65, 47, atticIcon)
            renderImageToNextion(65, 102, buttonIcon)
            renderPager(prevEnabled = true, nextEnabled = false)
        }
    }

    private fun renderControlSlot(slot: Int, instanceId: Int, controlType: Int, name: String, description: String, state: String, signaled: Boolean) {
        renderer.render("instanceId${slot}.val=$instanceId")
        renderer.render("vis background${slot}Txt,1")
        renderer.render("vis name${slot}Txt,1")
        renderer.render("name${slot}Txt.txt=\"$name\"")
        renderer.render("vis desc${slot}Txt,1")
        renderer.render("desc${slot}Txt.txt=\"$description\"")
        renderer.render("vis marker${slot}Txt,${if (signaled) "1" else "0"}")
        renderer.render("vis slot${slot}Btn,1")
        renderer.render("slot${slot}Btn.txt=\"${state}\"")
        renderer.render("type${slot}.val=${controlType}")
    }

    private fun renderEmptySlot(slot: Int) {
        renderer.render("vis background${slot}Txt,0")
        renderer.render("vis name${slot}Txt,0")
        renderer.render("vis desc${slot}Txt,0")
        renderer.render("vis marker${slot}Txt,0")
        renderer.render("vis slot${slot}Btn,0")
    }

    private fun renderPager(prevEnabled: Boolean, nextEnabled: Boolean) {
        renderer.render("vis prevPageBtn,${if (prevEnabled) "1" else "0"}")
        renderer.render("vis nextPageBtn,${if (nextEnabled) "1" else "0"}")
        renderer.render("vis loadingBtn,0")
    }
}