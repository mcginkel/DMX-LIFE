"""
The contract every DMX output backend satisfies.
"""
import time
from abc import ABC, abstractmethod

FRAME_SIZE = 512


class DMXBackendError(Exception):
    """
    The single failure type a backend raises.

    Each backend translates its own transport's exceptions into this
    (socket.error for Art-Net, serial.SerialException for USB), so the
    output thread catches one exception type and never needs to know which
    transport is underneath it.
    """


class DMXBackend(ABC):
    """
    A transport that can carry a 512-channel DMX frame.

    Four operations, matching what the output thread actually needs. A
    backend owns its own connection state and reports it in the shape the
    connection-status API already returns, so which backend is active makes
    no difference to anything above this interface.
    """

    def __init__(self):
        self._connection_status = {
            'connected': True,
            'last_error_time': 0,
            'error_message': None,
        }

    @abstractmethod
    def connect(self):
        """Open the underlying transport. Raises DMXBackendError on failure."""

    @abstractmethod
    def send(self, frame):
        """
        Transmit one complete frame.

        Args:
            frame: 512 bytes of channel values.

        Raises:
            DMXBackendError: the frame could not be transmitted.
            ValueError: the frame is not exactly 512 bytes.
        """

    @abstractmethod
    def disconnect(self):
        """Close the underlying transport. Must be safe to call when not connected."""

    def get_connection_status(self):
        """Current status as {connected, last_error_time, error_message}."""
        return self._connection_status.copy()

    # -- helpers shared by every backend ---------------------------------

    @staticmethod
    def _validate_frame(frame):
        """A frame is exactly 512 channels; anything else is never transmitted."""
        if frame is None or len(frame) != FRAME_SIZE:
            raise ValueError(
                f"Frame must be exactly {FRAME_SIZE} bytes, got "
                f"{'None' if frame is None else len(frame)}"
            )

    def _mark_connected(self):
        """Record a successful transmission. Returns True if this was a recovery."""
        recovered = not self._connection_status['connected']
        self._connection_status['connected'] = True
        self._connection_status['error_message'] = None
        return recovered

    def _mark_failed(self, error):
        """Record a failed transmission. Returns True if this was a new failure."""
        was_connected = self._connection_status['connected']
        self._connection_status['connected'] = False
        self._connection_status['last_error_time'] = time.time()
        self._connection_status['error_message'] = str(error)
        return was_connected
