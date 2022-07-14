import gnu.io.CommPort
import gnu.io.CommPortIdentifier
import gnu.io.SerialPort
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.nio.charset.Charset
import java.util.concurrent.BlockingQueue
import java.util.concurrent.LinkedBlockingQueue

private val writeQueue : BlockingQueue<ByteArray> = LinkedBlockingQueue()
private val asciiCharset = Charset.forName("ASCII")

private fun offerForNextion(content: ByteArray) {
    writeQueue.offer(content)
    writeQueue.offer(byteArrayOf(0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte()))
}

private fun offerForNextion(s: String) {
    offerForNextion(s.toByteArray(asciiCharset))
}

fun main(args: Array<String>) {
    println("Connecting to COM34")
    connect("COM34")
}

fun connect(portName: String) {
    val portIdentifier: CommPortIdentifier = CommPortIdentifier.getPortIdentifier(portName)
    if (portIdentifier.isCurrentlyOwned) {
        println("Error: Port is currently in use")
    } else {
        println("Connect 1/2")
        val commPort: CommPort = portIdentifier.open("UI-Tester", 6000)
        if (commPort is SerialPort) {
            println("Connect 2/2")
            val serialPort: SerialPort = commPort
            serialPort.setSerialPortParams(
                115200,
                SerialPort.DATABITS_8,
                SerialPort.STOPBITS_1,
                SerialPort.PARITY_NONE
            )
            println("BaudRate: " + serialPort.baudRate)
            println("DataBits: " + serialPort.dataBits)
            println("StopBits: " + serialPort.stopBits)
            println("Parity: " + serialPort.parity)
            println("FlowControl: " + serialPort.flowControlMode)
            val inputStream: InputStream = serialPort.inputStream
            val outputStream: OutputStream = serialPort.outputStream
            Thread(SerialReader(inputStream)).start()
            Thread(SerialWriter(outputStream)).start()
        } else {
            println("Error: Only serial ports are handled by this example.")
        }
    }
}

class SerialReader(var inputStream: InputStream) : Runnable {

    override fun run() {
        val ioBuffer = ByteArray(1024)
        try {
            while (true) {
                val inTheBuffer = inputStream.read(ioBuffer)
                if (inTheBuffer > 0) {
                    val data = ioBuffer.copyOfRange(0, inTheBuffer)
                    println(data.toHexString())

                    //request for scan result
                    if (data.size == 2 && data[0] == 0x00.toByte() && data[1] == 0x00.toByte()) {
                        offerForNextion("wifiSsid.scanResult.txt=\"network1;network2;network3\"")
                        offerForNextion("page wifiSsid")
                    }

                    //ssid selected
                    if (data.size > 2 && data[0] == 0x01.toByte() && data[1] == 0x01.toByte()) {
                        val ssid = String(data.drop(2).toByteArray())
                        println("Selected ssid=$ssid")
                        offerForNextion("page wifiPassword")
                    }

                    //password selected
                    if (data.size > 2 && data[0] == 0x01.toByte() && data[1] == 0x02.toByte()) {
                        val password = String(data.drop(2).toByteArray())
                        println("Typed password=$password")
                        offerForNextion("page connecting")

                        Thread.sleep(4000)

                        offerForNextion("page control")
                    }

                    //inbox subjects requested
                    if (data.size == 2 && data[0] == 0x00.toByte() && data[1] == 0x03.toByte()) {
                        offerForNextion("vis slot0Btn,1")
                        offerForNextion("slot0Btn.txt=\"Thank you for choosing Automate Everything\"")
                        offerForNextion("vis slot1Btn,1")
                        offerForNextion("slot1Btn.txt=\"Automation enabled\"")
                        offerForNextion("vis slot2Btn,1")
                        offerForNextion("slot2Btn.txt=\"Automation disabled\"")
                        offerForNextion("vis slot3Btn,1")
                        offerForNextion("slot3Btn.txt=\"A problem with sensor one\"")
                        offerForNextion("vis slot4Btn,0")
                        offerForNextion("vis slot5Btn,0")
                        offerForNextion("vis moreBtn,0")
                        offerForNextion("vis loadingBtn,0")
                    }
                }
                Thread.sleep(500)
            }
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }
}

class SerialWriter(out: OutputStream) : Runnable {
    var out: OutputStream

    private fun flush(chunk: ByteArray) {
        out.write(chunk)
        out.flush()
    }

    override fun run() {
        try {
            while (true) {
                if (writeQueue.isNotEmpty()) {
                    val replyData = writeQueue.poll()
                    flush(replyData)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    init {
        this.out = out
    }
}

fun ByteArray.toHexString() = joinToString(" ") { "%02X".format(it) }

