
import unittest
from strogonanoff_sender import *
from strogonanoff_receiver import *

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


class Strogonanoff_ReceiverTest(unittest.TestCase):

    def xtest_poll(self):
        from WiringPin import WiringPin
        pin = WiringPin(0, "in")

        def print_callback(channel, button, state):
            print channel, button, state, state_machine.sync_pulse_width

        def error_callback():
            print "error"

        accumulator = Accumulator(print_callback, None)

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

        accumulator = Accumulator(callback, None)
        state_changes = encode_as_state_list(command_as_bit_list(channel, button, True))
        pass_state_list_to_accumulator(state_changes, accumulator)
        self.assertEquals(4, self.found_channel)
        self.assertEquals(2, self.found_button)
        self.assertEquals(True, self.found_state)


if __name__ == "__main__":
    unittest.main()

