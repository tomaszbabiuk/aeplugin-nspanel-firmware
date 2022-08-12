package uitester.vm

import EntityType
import NextionRenderer
import RendereableNVM
import SvgToNextionConverter
import Point
import RequestType
import java.nio.charset.Charset

/***
 * [Data] [InterfaceValueOfColor] [Instance Id LSB] [Instance Id MSB]
 */
class ControlColorNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {

    private val svgToNextion = SvgToNextionConverter()
    val buttonIcon = svgToNextion.convert("C:\\Users\\tombab\\Downloads\\button.svg", 100f, 100f)

    private fun renderImageToNextion(xRel: Int, yRel: Int, points: List<Point>) {
        points.forEach {
            val line = "line ${xRel + it.x0},${yRel + it.y0},${xRel + it.x1},${yRel + it.y1},WHITE"
            renderer.render(line)
        }
    }

    override fun checkMatch(data: ByteArray): Boolean {
        return data.size == 4 &&
                data[0] == RequestType.Data.dataByte &&
                data[1] == EntityType.InterfaceValueOfColor.dataByte
    }

    override fun control(data: ByteArray) {
        renderer.render("vis loadingBtn,1")

        val instanceIdLow = data[2]
        val instanceIdHigh = data[3]
        val instanceId: UInt = instanceIdHigh.toUByte()*256U + instanceIdLow.toUByte()
        if (instanceId == 3U) {
                renderer.render("titleTxt.txt=\"Lamp 20X\"")
                renderer.render("hueSlr.val=124") //min val + 4 steps
                renderer.render("brightSlr.val=90")

                renderImageToNextion(174, 57, buttonIcon)
        }

        renderer.render("vis loadingBtn,0")
        renderer.render("vis applyBtn,1")
    }
}