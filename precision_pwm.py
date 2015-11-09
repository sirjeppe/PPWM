try:
    import RPi.GPIO
except:
    raise Exception('RPi.GPIO module seems to be missing')
import time
from multiprocessing import Process, Value


class PPWM_process(Process):

    _run = None
    _pin = 0
    _target_frequency = None
    _duty_cycle = None
    _resolution = None
    _dc = 0.5
    _pc = 0.5
    _s = 0.02
    _dirty = None
    _running = False

    def __init__(self, run, dirty, pin, target_frequency, duty_cycle, resolution=100.0):
        self._pin = pin
        self._target_frequency = target_frequency
        self._duty_cycle = duty_cycle
        self._resolution = resolution
        self._run = run
        self._dirty = dirty
        super(PPWM_process, self).__init__()

    def _calc_dc_pc(self):
        pause_cycle = self._resolution.value - self._duty_cycle.value
        self._dc = self._duty_cycle.value / self._resolution.value - 0.03
        self._pc = pause_cycle / self._resolution.value

    def _calc_s(self):
        self._s = 1 / self._target_frequency.value

    def _sleep(self, start, stop_delta):
        now = start
        if time.time() - start >= stop_delta:
            return start + stop_delta
        if stop_delta >= 0.0001:
            time.sleep(stop_delta - 0.000098)
            return start + stop_delta
        while now - start < stop_delta:
            now = time.time()
        return now

    def run(self):
        while self._run.value:
            self._calc_s()
            self._calc_dc_pc()
            self._dirty.value = False
            if self._duty_cycle.value == self._resolution.value:
                RPi.GPIO.output(self._pin, RPi.GPIO.HIGH)
                while not self._dirty.value:
                    self._sleep(time.time(), 0.1)
            elif self._duty_cycle.value <= 0:
                RPi.GPIO.output(self._pin, RPi.GPIO.LOW)
                while not self._dirty.value:
                    self._sleep(time.time(), 0.1)
            else:
                last = time.time()
                while not self._dirty.value:
                    RPi.GPIO.output(self._pin, RPi.GPIO.HIGH)
                    self._sleep(time.time(), self._s * self._dc)
                    RPi.GPIO.output(self._pin, RPi.GPIO.LOW)
                    now = self._sleep(time.time(), self._s * self._pc)
                    self._s = self._s * ((1 / (now - last)) / self._target_frequency.value)
                    last = now


class PPWM:

    _p = None
    _target_frequency = None
    _duty_cycle = None
    _resolution = None
    _run = None
    _dirty = None
    _pin = 0

    def __init__(self, pin, target_frequency, duty_cycle, resolution=100.0):
        self._pin = pin
        self._target_frequency = Value('d', target_frequency)
        self._duty_cycle = Value('d', duty_cycle)
        self._resolution = Value('d', resolution)
        self._run = Value('i', 1)
        self._dirty = Value('i', 0)

    def start(self):
        self._p = PPWM_process(self._run, self._dirty, self._pin, self._target_frequency, self._duty_cycle, self._resolution)
        self._p.start()

    def stop(self):
        self._run.value = 0
        self._dirty.value = 1
        self._p.join()

    def set_duty_cycle(self, dc):
        self._duty_cycle.value = float(dc)
        self._dirty.value = 1

    def set_frequency(self, freq):
        self._target_frequency.value = float(freq)
        self._dirty.value = 1
