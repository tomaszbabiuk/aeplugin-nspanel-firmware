import java.nio.charset.Charset
import java.util.concurrent.BlockingQueue

private val asciiCharset = Charset.forName("ASCII")


interface NextionRenderer {
    fun render(data: String)
}

class SerialNextionRenderer(private val sink: BlockingQueue<ByteArray>) : NextionRenderer {
    private fun offerForNextion(content: ByteArray) {
        sink.offer(content)
        sink.offer(byteArrayOf(0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte()))
    }

    private fun offerForNextion(s: String) {
        offerForNextion(s.toByteArray(asciiCharset))
    }

    override fun render(data: String) {
        offerForNextion(data)
    }
}