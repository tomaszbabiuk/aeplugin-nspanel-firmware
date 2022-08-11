package uitester.vm

import EntityType
import NextionRenderer
import RendereableNVM
import SvgToNextionConverter
import Point
import RequestType
import java.nio.charset.Charset

/***
 * [Data] [InterfaceValueOfController] [Instance Id Low] [Instance Id High]
 */
class ControlControllerNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {

    private val svgToNextion = SvgToNextionConverter()
    val atticIcon = svgToNextion.convert("C:\\Users\\tombab\\Downloads\\attic.svg", 100f, 100f)
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
                data[1] == EntityType.InterfaceValueOfController.dataByte
    }

    override fun control(data: ByteArray) {
        renderer.render("vis loadingBtn,1")

        val instanceIdLow = data[2]
        val instanceIdHigh = data[3]
        val instanceId: UInt = instanceIdHigh.toUByte()*256U + instanceIdLow.toUByte()
        if (instanceId == 200U) {
                renderer.render("titleTxt.txt=\"Controller 10XPf\"")
                renderer.render("minValTxt.txt=\"10°C\"")
                renderer.render("maxValTxt.txt=\"40°C\"")
                renderer.render("descTxt.txt=\"Heating\"")
                renderer.render("vis markerTxt,1")
                renderer.render("unitTxt.txt=\"°C\"")
                renderer.render("step.val=50") //0.5°C
                renderer.render("valSlr.maxval=60") //(40-10)*2... steps per range
                renderer.render("valSlr.val=4") //min val + 4 steps
                renderer.render("valueTxt.val=1200")

                renderImageToNextion(174, 47, atticIcon)
        }

        renderer.render("vis loadingBtn,0")
        renderer.render("vis applyBtn,1")
    }
}