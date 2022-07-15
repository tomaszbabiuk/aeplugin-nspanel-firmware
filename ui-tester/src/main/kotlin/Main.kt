import gnu.io.CommPort
import gnu.io.CommPortIdentifier
import gnu.io.SerialPort
import uitester.vm.*
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.util.concurrent.BlockingQueue
import java.util.concurrent.LinkedBlockingQueue

private val writeQueue: BlockingQueue<ByteArray> = LinkedBlockingQueue()


fun main(args: Array<String>) {
    //real device: COM9
    //simulator: COM34
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

    private val renderer = SerialNextionRenderer(writeQueue)
    private val viewModels = listOf(
        WifiScanNVM(renderer),
        WifiSsidNVM(renderer),
        WifiPasswordNVM(renderer),
        InboxNVM(renderer),
        InboxDetailsNVM(renderer),
        ControlNVM(renderer)
    )

    override fun run() {
        val ioBuffer = ByteArray(1024)
        try {
            while (true) {
                val inTheBuffer = inputStream.read(ioBuffer)
                if (inTheBuffer > 0) {
                    val data = ioBuffer.copyOfRange(0, inTheBuffer)
                    println(data.toHexString())

                    viewModels
                        .filter { it.checkMatch(data) }
                        .forEach { it.control(data) }
                }
                Thread.sleep(1000)
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

