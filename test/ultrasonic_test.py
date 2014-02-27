import eventlet
import robovinci.pins as pins
import robovinci.ultrasonic as ultrasonic

from nose.tools import *
import mock

def tickDiff(tstart, tend):
    return tend - tstart

@mock.patch('robovinci.ultrasonic.pigpio')
def test_basic(pigpio):
    pigpio.tickDiff = tickDiff
    us = ultrasonic.Ultrasonic()
    t = eventlet.spawn(lambda: us.measure())
    eventlet.sleep(0)
    us._on_echo(pins.ULTRASONIC_ECHO, 1, 0)
    us._on_echo(pins.ULTRASONIC_ECHO, 0, 1000)
    assert_equal(17.0, t.wait())
