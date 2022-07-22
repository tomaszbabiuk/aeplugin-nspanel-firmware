package uitester.vm

import NextionRenderer
import RendereableNVM
import SvgToNextionConverter
import Point
import eu.automateeverything.data.automation.EvaluationResultDto
import eu.automateeverything.data.automation.NextStatesDto
import eu.automateeverything.data.automation.State
import eu.automateeverything.data.localization.Resource

class ControlDetailsNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {

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
        return data.size == 4 && data[0] == 0x00.toByte() && data[1] == 0x06.toByte()
    }

    override fun control(data: ByteArray) {
        renderer.render("vis loadingBtn,1")

        val instanceId = data[2]
        val statePageId = data[3]
        if (instanceId == 0x00.toByte()) {
            if (statePageId == 0x00.toByte()) {
                renderer.render("titleTxt.txt=\"Recuperator\"")
                renderer.render("intValTxt.txt=\"II gear\"")
                renderer.render("descTxt.txt=\"\"")
                renderer.render("vis markerTxt,1")
                renderImageToNextion(63, 47, atticIcon)

                renderer.render("vis slot0Btn,1")
                renderer.render("slot0Btn.txt=\"Gear I\"")
                renderer.render("vis slot1Btn,1")
                renderer.render("slot1Btn.txt=\"Gear II\"")
                renderer.render("vis slot2Btn,1")
                renderer.render("slot2Btn.txt=\"Gear III\"")
                renderer.render("vis slot3Btn,1")
                renderer.render("slot3Btn.txt=\"Gear IV\"")
                renderer.render("vis slot4Btn,1")
                renderer.render("slot4Btn.txt=\"Gear V\"")
                renderer.render("vis slot5Btn,1")
                renderer.render("slot5Btn.txt=\"Gear VI\"")
                renderer.render("vis pageUpBtn,1")
                renderer.render("pageUpBtn.pco=42260")
                renderer.render("tsw pageUpBtn,0")
                renderer.render("vis pageDownBtn,1")
            } else {
                renderer.render("vis slot0Btn,1")
                renderer.render("slot0Btn.txt=\"Gear VII\"")
                renderer.render("vis slot1Btn,1")
                renderer.render("slot1Btn.txt=\"Gear VIII\"")
                renderer.render("vis slot2Btn,0")
                renderer.render("vis slot3Btn,0")
                renderer.render("vis slot4Btn,0")
                renderer.render("vis slot5Btn,0")
                renderer.render("vis pageUpBtn,1")
                renderer.render("pageUpBtn.pco=0")
                renderer.render("tsw pageUpBtn,1")
                renderer.render("vis pageDownBtn,0")
            }

        } else if (instanceId == 0x01.toByte()) {
            renderer.render("titleTxt.txt=\"Radiator valve\"")
            renderer.render("intValTxt.txt=\"Regulation\"")
            renderer.render("descTxt.txt=\"Opening level 12%\\rDelay 30s\"")
            renderer.render("vis markerTxt,0")
            renderImageToNextion(63, 47, buttonIcon)
        }

        renderer.render("vis loadingBtn,0")
    }
}