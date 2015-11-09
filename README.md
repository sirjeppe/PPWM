# PPWM (Precision PWM)
A software PWM Python module for Raspberry Pi 2 based on RPi.GPIO.

Each instance of PPWM creates its own process to avoid slowing down the main
thread running the code controlling the PPWM instances.

## How to use
PPWM builds on top of the [RPi.GPIO](http://sourceforge.net/projects/raspberry-gpio-python/) library so to use PPWM
you also need to install RPi.GPIO first. Please follow their instructions on how
to do so.

After having installed RPi.GPIO you are ready to use PPWM like so:
```python
import RPi.GPIO as GPIO
from precision_pwm import PPWM

# Setup GPIO pin properly.
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

# Create a PPWM instance with 60 Hz frequency and 50% duty cycle. Resolution
# (the 4:th argument to the PPWM constructor) is 100 by default.
p = PPWM(7, 60, 50)

# Call start() to initiate the PWM.
p.start()

# To change the duty cycle, use the set_duty_cycle() method:
p.set_duty_cycle(20)

# To change the frequency, use the set_frequency() method:
p.set_frequency(200)

# To stop the PWM use the stop() method:
p.stop()
```
