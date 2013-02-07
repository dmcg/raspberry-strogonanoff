#!/usr/bin/env python

from time import time
from strogonanoff_common import *


min_default_pulse_width = 0.7 * default_pulse_width
max_default_pulse_width = 1.3 * default_pulse_width

min_preamble_width = 15 * default_pulse_width
max_preamble_width = 30 * default_pulse_width

def is_preamble(level, duration):
    return level == 0 and min_preamble_width <= duration and duration <= max_preamble_width

def is_first_pulse(level, duration):
    return level == 1 and min_default_pulse_width <= duration and duration <= max_default_pulse_width


def channel_and_button_for(command):
    for row in range(0, len(channel_codes)):
        for col in range(0, len(channel_codes[row])):
            if channel_codes[row][col] == command:
                return (row + 1, col + 1)
    return (-1, -1)

def on_or_off_for(code):
    if code == on_code:
        return True
    elif code == off_code:
        return False
    else:
        return None

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
                self.accumulator.on_short(level)
            else:
                self.on_error()

    def on_error(self):
        self.reset()

    def reset(self):
        self.accumulator.on_error()
        self.state = noise

    def is_short_pulse(self, duration):
        return 0.9 * self.sync_pulse_width <= duration and duration <= 1.1 * self.sync_pulse_width

    def is_long_pulse(self, duration):
        return 3 * 0.9 * self.sync_pulse_width <= duration and duration <= 3 * 1.1 * self.sync_pulse_width

class Accumulator:

    def __init__(self, result_callback, error_callback = None):
        self.result_callback = result_callback
        self.error_callback = error_callback
        self.reset()

    def on_short(self, level):
        self._new_bit(0)

    def on_long(self, level):
        self._new_bit(1)

    def on_error(self):
        if self.error_callback is not None:
            self.error_callback()
        self.reset()

    def get_command(self):
        return self.result & 0xffffffff

    def get_state_code(self):
        return self.result >> 32

    def reset(self):
        self.result = long(0)
        self.bit_count = 0

    def _new_bit(self, bit):
        self.result = self.result | (bit & 0x01) << self.bit_count
        self.bit_count = self.bit_count + 1
        if self.bit_count == 48:
            channel_and_button = channel_and_button_for(self.get_command())
            state = on_or_off_for(self.get_state_code())
            self.result_callback(channel_and_button[0], channel_and_button[1], state)
            self.reset()

def poll(pin, callback):
    level = 0
    start_t = time()
    while True:
        if pin.get_value() != level:
            now = time()
            callback(level, now - start_t)
            level = 1 - level
            start_t = now

if __name__ == "__main__":
    from WiringPin import WiringPin
    pin = WiringPin(0, "in")

    def print_callback(channel, button, state):
        print channel, button, state, state_machine.sync_pulse_width

    def error_callback():
        print "error"

    accumulator = Accumulator(print_callback, None)

    state_machine = StateMachine(accumulator)
    poll(pin, state_machine.on_pulse)
