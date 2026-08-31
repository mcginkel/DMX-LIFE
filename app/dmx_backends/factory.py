"""
Constructs the configured output backend.
"""
from app.dmx_backends.base import DMXBackendError

BACKEND_ARTNET = 'artnet'
BACKEND_ENTTEC_USB = 'enttec_usb'

# Selection value -> human label, for the Setup UI and error messages.
SUPPORTED_BACKENDS = {
    BACKEND_ARTNET: 'Art-Net',
    BACKEND_ENTTEC_USB: 'Enttec DMX USB Pro',
}

DEFAULT_OUTPUT = {
    'backend': BACKEND_ARTNET,
    'artnet': {'ip': '255.255.255.255', 'port': 6454, 'universe': 0, 'packet_size': 512},
    'enttec_usb': {'port': ''},
}


def create_backend(config):
    """
    Build the backend named by `output.backend`, from its own settings.

    Both backends' settings can be present at once, so switching in the UI
    does not discard the other's; only `output.backend` decides which is
    constructed.

    Raises:
        DMXBackendError: the configured backend is not one we implement.
    """
    output = (config or {}).get('output') or {}
    selection = output.get('backend', BACKEND_ARTNET)

    if selection == BACKEND_ARTNET:
        from app.dmx_backends.artnet import ArtNetBackend
        settings = output.get('artnet') or {}
        defaults = DEFAULT_OUTPUT['artnet']
        return ArtNetBackend(
            ip=settings.get('ip', defaults['ip']),
            port=settings.get('port', defaults['port']),
            universe=settings.get('universe', defaults['universe']),
            packet_size=settings.get('packet_size', defaults['packet_size']),
        )

    if selection == BACKEND_ENTTEC_USB:
        from app.dmx_backends.enttec_usb import EnttecUsbBackend
        settings = output.get('enttec_usb') or {}
        return EnttecUsbBackend(port=settings.get('port', ''))

    known = ', '.join(sorted(SUPPORTED_BACKENDS))
    raise DMXBackendError(
        f"Unknown output backend '{selection}'. Configure output.backend as one of: {known}"
    )
