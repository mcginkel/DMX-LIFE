"""
Enttec DMX USB Pro wire format.

Asserted against the published Widget API 1.44 "Output Only Send DMX Packet"
message (label 6), not against a capture - no hardware is needed to check
the framing, which is the point of testing it separately from the device.
"""
import pytest

from app.dmx_backends.enttec_usb import EnttecUsbBackend

PORT = '/dev/tty.usbserial-TEST'


def packet_for(frame=None):
    return EnttecUsbBackend(port=PORT).build_packet(bytes(512) if frame is None else frame)


def test_delimiters_and_label():
    packet = packet_for()
    assert packet[0] == 0x7E, 'start delimiter'
    assert packet[1] == 6, 'label: Output Only Send DMX Packet'
    assert packet[-1] == 0xE7, 'end delimiter'


def test_data_length_is_little_endian_and_counts_the_start_code():
    packet = packet_for()
    # 512 channels + 1 start code = 513 = 0x0201
    assert packet[2] == 0x01, 'length LSB'
    assert packet[3] == 0x02, 'length MSB'
    assert int.from_bytes(packet[2:4], 'little') == 513


def test_start_code_precedes_the_channel_data():
    assert packet_for()[4] == 0x00, 'DMX start code'


def test_channel_values_are_carried_verbatim():
    frame = bytes(range(256)) * 2
    packet = packet_for(frame)
    assert packet[5:-1] == frame


def test_total_packet_length():
    # 4 header bytes + start code + 512 channels + 1 end delimiter
    assert len(packet_for()) == 518


def test_full_scale_frame_is_not_escaped():
    # The Pro's framing has no escaping, so a channel holding 0x7E or 0xE7
    # must pass through unchanged rather than being treated as a delimiter.
    frame = bytes([0x7E, 0xE7] + [255] * 510)
    packet = packet_for(frame)
    assert packet[5] == 0x7E
    assert packet[6] == 0xE7
    assert packet[-1] == 0xE7


@pytest.mark.parametrize('frame', [b'', bytes(511), bytes(513), None])
def test_wrong_sized_frame_is_rejected(frame):
    with pytest.raises(ValueError):
        EnttecUsbBackend(port=PORT).build_packet(frame)
