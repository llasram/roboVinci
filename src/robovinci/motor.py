import time
import eventlet
import eventlet.event as event
pigpio = eventlet.import_patched('pigpio')
import robovinci.pins as pins

LEFT = 0
RIGHT = 1

_PINS = {
    LEFT: [
        pins.MOTOR_LEFT_FORWARD,
        pins.MOTOR_LEFT_REVERSE,
        pins.MOTOR_LEFT_PWM,
        ],
    RIGHT: [
        pins.MOTOR_RIGHT_FORWARD,
        pins.MOTOR_RIGHT_REVERSE,
        pins.MOTOR_RIGHT_PWM,
        ],
    }

class _Updater(object):
    def __init__(self, side, ttime=2):
        forward, reverse, pwm = _PINS[side]
        self._pin_forward = forward
        self._pin_reverse = reverse
        self._pin_pwm = pwm
        self._event = event.Event()
        self._current = 0
        self._target = 0
        self._delay = ttime / 100.0
        self._step = 100.0 / ttime
        self._thread = None
        self._finished = False
        self._start()

    def _start(self):
        pigpio.set_mode(self._pin_forward, pigpio.OUTPUT)
        pigpio.write(self._pin_forward, 0)
        pigpio.set_mode(self._pin_reverse, pigpio.OUTPUT)
        pigpio.write(self._pin_reverse, 0)
        pigpio.set_mode(self._pin_pwm, pigpio.OUTPUT)
        pigpio.set_PWM_dutycycle(self._pin_pwm, 0)
        pigpio.set_PWM_range(self._pin_pwm, 100)
        self._thread = eventlet.spawn_n(self._watch)

    def _sign(self, x):
        if x == 0:
            return 0
        elif x < 0:
            return -1
        else:
            return 1

    def _write_pins(self, forward, reverse):
        pigpio.write(self._pin_forward, forward)
        pigpio.write(self._pin_reverse, reverse)

    def _update(self):
        now = time.time()
        last = now - self._delay
        current = self._current
        target = self._target
        while True:
            diff = target - current
            sign = self._sign(diff)
            step = max(1, int((now - last) * self._step))
            step = sign * min(abs(diff), step)
            osign = self._sign(current)
            current = current + step
            nsign = self._sign(current)
            if osign != nsign:
                self._write_pins(0, 0)
            pigpio.set_PWM_dutycycle(self._pin_pwm, abs(current))
            if osign != nsign:
                if nsign == -1:
                    self._write_pins(0, 1)
                elif nsign == 1:
                    self._write_pins(1, 0)
            self._current = current
            if current == target or self._finished:
                break
            last = now
            eventlet.sleep(self._delay)
            target = self._target

    def _signal(self):
        if not self._event.ready():
            self._event.send()

    def _watch(self):
        while True:
            self._event.wait()
            if self._finished:
                break
            self._update()
            if not self._finished:
                self._event.reset()

    def stop(self):
        self._finished = True
        self._signal()

    def get(self):
        return self._current

    def set(self, speed):
        sign = self._sign(speed)
        speed = speed if abs(speed) <= 100 else (sign * 100)
        self._target = speed
        self._signal()

class Motor(object):
    def __init__(self, side, ttime=2):
        self._updater = _Updater(side, ttime)

    def get(self):
        return self._updater.get()

    def set(self, speed):
        self._updater.set(speed)

    def __del__(self):
        self._updater.stop()
