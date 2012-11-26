import unittest
#from strogonanoff_receiver import *
from time import time
import sys

default_pulse_width = 500e-6
min_default_pulse_width = 0.8 * default_pulse_width
max_default_pulse_width = 1.2 * default_pulse_width

min_preamble_width = 24 * default_pulse_width
max_preamble_width = 28 * default_pulse_width

def is_preamble(level, duration):
    return level == 0 and min_preamble_width <= duration and duration <= max_preamble_width

def is_first_pulse(level, duration):
    return level == 1 and min_default_pulse_width <= duration and duration <= max_default_pulse_width

def p(s):
    print s,
#    sys.stdout.flush()

noise = 0
looking_for_end_of_first_pulse = 1
capturing = 2

class StateMachine:

    def __init__(self, accumulator):
        self.accumulator = accumulator
        self.reset()

    def on_pulse(self, level, duration):
        if self.state == noise and is_preamble(level, duration):
            self.state = looking_for_end_of_first_pulse
        elif self.state == looking_for_end_of_first_pulse:
            if not is_first_pulse(level, duration):
                self.state = noise
            else:
                self.sync_pulse_width = duration
                self.state = capturing
        elif self.state == capturing:
            if self.is_long_pulse(duration):
                self.accumulator.on_long(level)
            elif self.is_short_pulse(duration):
                self.accumulator.on_short("*")
            else:
                self.reset()

    def reset(self):
        self.accumulator.reset()
        self.state = noise

    def is_short_pulse(self, duration):
        return 0.9 * self.sync_pulse_width <= duration and duration <= 1.1 * self.sync_pulse_width

    def is_long_pulse(self, duration):
        return 3 * 0.9 * self.sync_pulse_width <= duration and duration <= 3 * 1.1 * self.sync_pulse_width

class Accumulator:

    def on_short(self, level):
        p("*")

    def on_long(self, level):
        p("***")

    def reset(self):
        p("X")

def poll(pin, callback):
    level = 0
    start_t = time()
    while True:
        if pin.get_value() != level:
            now = time()
            callback(level, now - start_t)
            level = 1 - level
            start_t = now


class Strogonanoff_ReceiverTest(unittest.TestCase):

    def test_poll(self):
        from WiringPin import WiringPin
        pin = WiringPin(0, "in")
        accumulator = Accumulator()
        state_machine = StateMachine(accumulator)
        poll(pin, state_machine.on_pulse)

    def test_accumulate(self):
        pass

if __name__ == "__main__":
    unittest.main()

