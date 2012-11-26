from time import time
from strogonanoff_common import *


default_pulse_width = 500e-6
min_default_pulse_width = 0.8 * default_pulse_width
max_default_pulse_width = 1.2 * default_pulse_width

min_preamble_width = 24 * default_pulse_width
max_preamble_width = 28 * default_pulse_width

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

def p(s):
    print s,

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

    def __init__(self, callback):
        self.callback = callback
        self.reset()

    def on_short(self, level):
        self._new_bit(0)

    def on_long(self, level):
        self._new_bit(1)

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
            self.callback(channel_and_button[0], channel_and_button[1], state)
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

def run_lengths(list):
    result = []
    if len(list) == 0:
        return result

    previous = list[0]
    count = 1
    for e in list[1:]:
        if e == previous:
            count = count + 1
        else:
            result.append((previous, count))
            previous = e
            count = 1
    result.append((previous, count))
    return result


def pass_state_list_to_accumulator(list, accumulator):
    for level_len in run_lengths(list):
        if level_len[1] == 1:
            accumulator.on_short(level_len[0])
        elif level_len[1] == 3:
            accumulator.on_long(level_len[0])
        else:
            raise "bad run length"

import unittest
from strogonanoff_sender import *


def printCallback(channel, button, state):
    print channel, button, state

class Strogonanoff_ReceiverTest(unittest.TestCase):

    def xtest_poll(self):
        from WiringPin import WiringPin
        pin = WiringPin(0, "in")
        accumulator = Accumulator(printCallback)
        state_machine = StateMachine(accumulator)
        poll(pin, state_machine.on_pulse)

    def test_lookup_channel(self):
        self.assertEquals((4, 2), channel_and_button_for(channel_codes[4 - 1][2 - 1]))
        self.assertEquals((-1, -1), channel_and_button_for(99))

    def test_accumulator(self):
        channel = 4
        button = 2

        def callback(channel, button, state):
            self.found_channel = channel
            self.found_button = button
            self.found_state = state

        accumulator = Accumulator(callback)
        state_changes = encode_as_state_list(command_as_bit_list(channel, button, True))
        pass_state_list_to_accumulator(state_changes, accumulator)
        self.assertEquals(4, self.found_channel)
        self.assertEquals(2, self.found_button)
        self.assertEquals(True, self.found_state)


if __name__ == "__main__":
    unittest.main()

