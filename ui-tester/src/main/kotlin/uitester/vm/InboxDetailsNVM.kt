package uitester.vm

import NextionRenderer
import RendereableNVM

class InboxDetailsNVM(renderer: NextionRenderer) : RendereableNVM(renderer) {
    override fun checkMatch(data: ByteArray): Boolean {
        return data.size == 3 && data[0] == 0x00.toByte() && data[1] == 0x04.toByte()
    }

    override fun control(data: ByteArray) {
        //val messageId = data[2]
        renderer.render("subjectTxt.txt=\"This is message subject\"")
        renderer.render("timeTxt.txt=\"5m ago\"")
        renderer.render("bodyTxt.txt=\"This is message body, a very, very, very long one... Lorem ipsum et dolores colorez\"")
        renderer.render("vis loadingBtn,0")
    }
}