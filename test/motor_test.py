import eventlet
import robovinci.pins as pins
import robovinci.motor as motor

from nose.tools import *
import mock

@mock.patch('robovinci.motor.pigpio')
def test_basic(pigpio):
    m = motor.Motor(side=motor.LEFT, ttime=0.5)
    assert_equal(0, m.get())
    m.set(50)
    assert_equal(0, m.get())
    eventlet.sleep(0.5)
    assert_equal(50, m.get())
    writes = pigpio.write.call_args_list
    assert_equal([mock.call(pins.MOTOR_LEFT_FORWARD, 0),
                  mock.call(pins.MOTOR_LEFT_REVERSE, 0)],
                 writes[:2])
    assert_equal([mock.call(pins.MOTOR_LEFT_FORWARD, 1),
                  mock.call(pins.MOTOR_LEFT_REVERSE, 0)],
                 writes[-2:])
    pwms = pigpio.set_PWM_dutycycle.call_args_list
    assert_equal(51, len(pwms))
    assert_equal(mock.call(pins.MOTOR_LEFT_PWM, 50), pwms[-1])
