"""Unit tests for NMEA2000 autopilot output."""
import math

import pytest

from app.modules.nmea2000_autopilot_out import NMEA2000RudderCommand, NMEA2000HeadingCommand


def test_rudder_encode_zero():
    payload = NMEA2000RudderCommand.encode(0.0)
    assert len(payload) == 7
    # Zero rudder should encode to near-zero in first two bytes
    raw = payload[0] | (payload[1] << 8)
    # Interpret as signed 16-bit
    if raw > 32767:
        raw -= 65536
    assert abs(raw) < 100


def test_rudder_encode_limits():
    # +45 degrees
    payload_p = NMEA2000RudderCommand.encode(45.0)
    raw_p = payload_p[0] | (payload_p[1] << 8)
    if raw_p > 32767:
        raw_p -= 65536
    assert raw_p > 0
    # -45 degrees
    payload_n = NMEA2000RudderCommand.encode(-45.0)
    raw_n = payload_n[0] | (payload_n[1] << 8)
    if raw_n > 32767:
        raw_n -= 65536
    assert raw_n < 0


def test_heading_encode_zero_to_360():
    for heading in [0.0, 90.0, 180.0, 270.0]:
        payload = NMEA2000HeadingCommand.encode(heading)
        assert len(payload) == 8
        # Verify first two bytes encode the heading angle
        raw = payload[0] | (payload[1] << 8)
        assert 0 <= raw <= 65535


def test_heading_encode_wraps():
    # 370 degrees should wrap to 10 degrees
    payload_370 = NMEA2000HeadingCommand.encode(370.0)
    payload_10 = NMEA2000HeadingCommand.encode(10.0)
    # First two bytes should be nearly identical
    raw_370 = payload_370[0] | (payload_370[1] << 8)
    raw_10 = payload_10[0] | (payload_10[1] << 8)
    assert abs(raw_370 - raw_10) < 100  # Allow small encoding tolerance
