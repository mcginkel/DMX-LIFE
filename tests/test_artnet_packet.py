"""
ArtDmx wire format.

The reference bytes below were captured from the StupidArtnet-based
implementation this backend replaces, configured exactly as the application
configured it (simplified off, net 0, subnet 0). They are what the venue rig
has always received, so any change to them is a change to what reaches the
lights - which is the risk this test exists to catch.
"""
import pytest

from app.dmx_backends.artnet import ArtNetBackend

# Captured from StupidArtnet: ip=10.10.11.10, universe=1, packet_size=512
REFERENCE_HEADER = bytes.fromhex('41 72 74 2d 4e 65 74 00 00 50 00 0e 00 00 01 00 02 00'.replace(' ', ''))


def header_of(**kwargs):
    settings = {'ip': '10.10.11.10', 'universe': 1, 'packet_size': 512}
    settings.update(kwargs)
    return ArtNetBackend(**settings).build_packet(bytes(512))[:18]


def test_header_matches_the_reference_capture():
    assert header_of() == REFERENCE_HEADER


def test_packet_is_header_plus_512_channel_bytes():
    frame = bytes(range(256)) * 2
    packet = ArtNetBackend(ip='10.10.11.10', universe=1).build_packet(frame)
    assert len(packet) == 18 + 512
    assert packet[:18] == REFERENCE_HEADER
    assert packet[18:] == frame


def test_artnet_id_and_opcode():
    header = header_of()
    assert header[0:8] == b'Art-Net\x00'
    assert header[8:10] == b'\x00\x50', 'OpOutput 0x5000, little-endian'
    assert header[10:12] == b'\x00\x0e', 'protocol version 14, big-endian'


def test_sequence_and_physical_are_zero():
    # Sequence 0 tells the receiver not to perform ordering checks. This is
    # what the previous implementation put on the wire on every frame.
    header = header_of()
    assert header[12] == 0, 'sequence'
    assert header[13] == 0, 'physical'


@pytest.mark.parametrize('universe, expected', [
    (0,   b'\x00\x00'),
    (1,   b'\x01\x00'),
    (2,   b'\x02\x00'),
    (15,  b'\x0f\x00'),
    (16,  b'\x10\x00'),
    (255, b'\xff\x00'),
])
def test_universe_is_little_endian(universe, expected):
    assert header_of(universe=universe)[14:16] == expected


@pytest.mark.parametrize('packet_size, expected', [
    (512, b'\x02\x00'),
    (256, b'\x01\x00'),
    (24,  b'\x00\x18'),
])
def test_data_length_is_big_endian(packet_size, expected):
    assert header_of(packet_size=packet_size)[16:18] == expected


@pytest.mark.parametrize('frame', [b'', bytes(511), bytes(513), None])
def test_wrong_sized_frame_is_rejected(frame):
    with pytest.raises(ValueError):
        ArtNetBackend(ip='10.10.11.10').build_packet(frame)
