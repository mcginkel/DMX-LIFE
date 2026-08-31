"""
Enttec DMX USB Pro backend - Widget API 1.44 framing over a serial port.
"""
from app.dmx_backends.base import FRAME_SIZE, DMXBackend, DMXBackendError

START_DELIMITER = 0x7E
END_DELIMITER = 0xE7
LABEL_OUTPUT_ONLY_SEND_DMX = 6
DMX_START_CODE = 0x00
BAUD_RATE = 250000


class EnttecUsbBackend(DMXBackend):
    """
    Sends frames to a DMX USB Pro as "Output Only Send DMX Packet" messages.

    The widget's own microcontroller generates the DMX break and
    mark-after-break from each message, so frame timing is the device's
    responsibility rather than this process's - which is why the Pro was
    chosen over a bare FTDI interface.
    """

    def __init__(self, port, baud_rate=BAUD_RATE):
        super().__init__()
        self.port = port
        self.baud_rate = int(baud_rate)
        self._serial = None

    def build_packet(self, frame):
        """
        One Widget API message. Separated out so the framing can be asserted
        on without a serial port present.

        Layout: 0x7E, label, data-length LSB, data-length MSB, then the data
        (a DMX start code followed by the 512 channel values), then 0xE7.
        The length is little-endian and counts the start code.
        """
        self._validate_frame(frame)
        data_length = FRAME_SIZE + 1  # start code + channels
        packet = bytearray()
        packet.append(START_DELIMITER)
        packet.append(LABEL_OUTPUT_ONLY_SEND_DMX)
        packet.append(data_length & 0xFF)
        packet.append((data_length >> 8) & 0xFF)
        packet.append(DMX_START_CODE)
        packet.extend(frame)
        packet.append(END_DELIMITER)
        return bytes(packet)

    def connect(self):
        try:
            import serial  # imported here so Art-Net installs need no pyserial
        except ImportError as error:
            raise DMXBackendError(
                "pyserial is required for the Enttec USB backend but is not installed"
            ) from error

        try:
            self._serial = serial.Serial(self.port, baudrate=self.baud_rate, timeout=1)
        except Exception as error:
            # serial.SerialException for the usual cases; OSError for a
            # device that disappears between listing and opening.
            self._serial = None
            self._mark_failed(error)
            raise DMXBackendError(f"Could not open serial port {self.port}: {error}") from error

    def send(self, frame):
        packet = self.build_packet(frame)
        if self._serial is None:
            self.connect()
        try:
            self._serial.write(packet)
        except Exception as error:
            self._mark_failed(error)
            raise DMXBackendError(f"Enttec write to {self.port} failed: {error}") from error
        self._mark_connected()

    def disconnect(self):
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

    def describe(self):
        return f"Enttec DMX USB Pro on {self.port}"
