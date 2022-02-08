import logging
import os

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
import atexit
import subprocess as sp
from datetime import datetime
from time import sleep
from itertools import cycle

logger = logging.getLogger(__name__)


class Backlight(object):
    SCREEN_ON = 0
    SCREEN_OFF = 1
    BL_DIR = "/sys/devices/platform/rpi_backlight/backlight/rpi_backlight"
    BL_POWER = os.path.join(BL_DIR, "bl_power")
    BL_BRIGHTNESS = os.path.join(BL_DIR, "brightness")

    def __init__(self, debug, brightness_steps):
        self.power_state = self.read_state(self.BL_POWER)
        if self.power_state == self.SCREEN_OFF:
            self.write_state(None, self.SCREEN_ON)
        self.max_brightness = 200
        self.brightness_state = self.read_state(self.BL_BRIGHTNESS)
        self.brightness_step = self.brightness_step_calc(brightness_steps)
        self.debug = debug

    def brightness_step_calc(self, steps):
        # Given the number of steps, find an interval that also satisfies a step being divisible by 5
        mb = self.max_brightness
        step_size = mb // steps
        step_size_m = step_size % 5
        step_size -= step_size_m
        return cycle(list(range(0, mb, step_size)))

    def read_state(self, fp):
        with open(fp, "r") as fp:
            status = int(fp.read())
        return status

    def write_state(self, fp, state):
        p = sp.Popen(["sudo", "su"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        command = "echo {} > {}".format(state, fp).encode()
        p.stdin.write(command)
        p.communicate()
        return state

    def cycle_backlight(self):
        new_value = next(self.brightness_step)
        if new_value == 0:
            self.power_state = self.write_state(self.BL_POWER, self.SCREEN_OFF)
            self.brightness_state = self.write_state(self.BL_BRIGHTNESS, new_value)
        else:
            if self.power_state == self.SCREEN_OFF:
                self.power_state = self.write_state(self.BL_POWER, self.SCREEN_ON)
            self.brightness_state = self.write_state(self.BL_BRIGHTNESS, new_value)

    def toggle_backlight(self):
        if self.power_state == self.SCREEN_OFF:
            self.power_state = self.write_state(self.BL_POWER, self.SCREEN_ON)
            if self.brightness_state == 0:
                self.brightness_state = self.write_state(self.BL_BRIGHTNESS, next(self.brightness_step))
        else:
            self.power_state = self.write_state(self.BL_POWER, self.SCREEN_OFF)


class ScreenButton(object):
    """
    With a pullup resistor the input pin will read a high state when button is not pressed. Conversely,
    pulldown resistor will read a low state when button is not pressed
    """

    def __init__(self, channel, gpio, debug, brightness_steps, toggle_duration_secs=3):
        self.channel = channel
        self.gpio = gpio
        self.bl = Backlight(debug=debug, brightness_steps=brightness_steps)
        self.debug = debug
        self.toggle_duration_secs = toggle_duration_secs
        self.last_pressed = None
        self._setup_pin()

    def _setup_pin(self):
        self.gpio.setup(self.channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.gpio.add_event_detect(
            self.channel, self.gpio.BOTH, callback=self.button_event, bouncetime=25
        )

    def button_event(self, *args, **kwargs):
        # High
        if GPIO.input(self.channel):
            return self.button_press()
        # Low
        else:
            return self.button_release()

    def button_press(self):
        self.last_pressed = datetime.now()

    def button_release(self):
        if not self.last_pressed:
            return self.bl.cycle_backlight()
        duration = datetime.now() - self.last_pressed
        self.last_pressed = None
        if duration.total_seconds() >= self.toggle_duration_secs:
            self.bl.toggle_backlight()
        else:
            self.bl.cycle_backlight()


if __name__ == "__main__":
    md = ScreenButton(
        channel=17, gpio=GPIO, brightness_steps=5, debug=False, toggle_duration_secs=1
    )
    atexit.register(GPIO.cleanup)
    while True:
        sleep(1)
