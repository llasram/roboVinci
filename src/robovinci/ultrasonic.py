import eventlet
import eventlet.event as event
pigpio = eventlet.import_patched('pigpio')
import robovinci.pins as pins

class Ultrasonic(object):
    STATE_QUIET = 0
    STATE_ACTIVE = 1

    def __init__(self):
        self._event = event.Event()
        self._state = self.STATE_QUIET
        self._tick_up = 0
        self._echo_cb = None
        self._start()

    def _start(self):
        pigpio.set_mode(pins.ULTRASONIC_TRIGGER, pigpio.OUTPUT)
        pigpio.set_mode(pins.ULTRASONIC_ECHO, pigpio.INPUT)
        pigpio.write(pins.ULTRASONIC_TRIGGER, 0)
        self._echo_cb = pigpio.callback(
            pins.ULTRASONIC_ECHO, pigpio.EITHER_EDGE, self._on_echo)

    def __del__(self):
        cb = self._echo_cb
        if cb is not None:
            cb.cancel()

    def _finish_echo(self, distance):
        pigpio.set_watchdog(pins.ULTRASONIC_ECHO, 0)
        self._event.send(distance)

    def _on_echo(self, _, level, tick):
        if self._state != self.STATE_ACTIVE:
            return
        elif level == 2:
            self._finish_echo(-1.0)
        elif level == 1:
            self._tick_up = tick
        elif level == 0:
            delta = pigpio.tickDiff(self._tick_up, tick)
            self._finish_echo(delta * 0.017)

    def _activate(self):
        pigpio.set_watchdog(pins.ULTRASONIC_ECHO, 1000)
        pigpio.gpio_trigger(pins.ULTRASONIC_TRIGGER)

    def measure(self):
        activator = False
        if self._state == self.STATE_QUIET:
            activator = True
            self._state = self.STATE_ACTIVE
            self._activate()
        distance = self._event.wait()
        if activator:
            self._state = self.STATE_QUIET
            self._event.reset()
        return distance

    def __call__(self):
        return self.measure()
