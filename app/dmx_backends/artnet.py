"""
Art-Net output backend - ArtDmx over UDP.
"""
import socket

from app.dmx_backends.base import FRAME_SIZE, DMXBackend, DMXBackendError

ARTNET_ID = b'Art-Net\x00'
OP_OUTPUT = 0x5000
PROTOCOL_VERSION = 14
DEFAULT_PORT = 6454


class ArtNetBackend(DMXBackend):
    """
    Sends raw ArtDmx packets to a configured address.

    No discovery (ArtPoll) and no ArtSync: the operator configures the
    destination directly, unicast or broadcast, which is what this system
    has always done.
    """

    def __init__(self, ip, port=DEFAULT_PORT, universe=0, packet_size=FRAME_SIZE):
        super().__init__()
        self.ip = ip
        self.port = int(port)
        self.universe = int(universe)
        self.packet_size = int(packet_size)
        self._socket = None
        self._header = self._build_header()

    def _build_header(self):
        """
        The 18-byte ArtDmx header preceding the channel data.

        Byte order is per the Art-Net spec and deliberately mixed: the opcode
        and universe are little-endian, the protocol version and data length
        are big-endian.

        The sequence byte stays 0, which the spec defines as "receiver shall
        not perform sequence checking". That is what this system has always
        put on the wire, so it is preserved deliberately rather than by
        omission - changing it alters how a node treats packet ordering.
        """
        header = bytearray()
        header.extend(ARTNET_ID)
        header.extend(OP_OUTPUT.to_bytes(2, 'little'))
        header.extend(PROTOCOL_VERSION.to_bytes(2, 'big'))
        header.append(0)                                    # sequence
        header.append(0)                                    # physical
        header.extend(self.universe.to_bytes(2, 'little'))
        header.extend(self.packet_size.to_bytes(2, 'big'))  # data length
        return bytes(header)

    def build_packet(self, frame):
        """The complete ArtDmx packet for one frame. Separated out so the
        wire format can be asserted on without opening a socket."""
        self._validate_frame(frame)
        return self._header + bytes(frame)

    def connect(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except socket.error as error:
            self._socket = None
            self._mark_failed(error)
            raise DMXBackendError(f"Could not open Art-Net socket: {error}") from error

    def send(self, frame):
        packet = self.build_packet(frame)
        if self._socket is None:
            self.connect()
        try:
            self._socket.sendto(packet, (self.ip, self.port))
        except socket.error as error:
            self._mark_failed(error)
            raise DMXBackendError(f"Art-Net send to {self.ip}:{self.port} failed: {error}") from error
        self._mark_connected()

    def disconnect(self):
        if self._socket is not None:
            try:
                self._socket.close()
            except socket.error:
                pass
            self._socket = None

    def describe(self):
        return f"Art-Net {self.ip}:{self.port} universe {self.universe}"
