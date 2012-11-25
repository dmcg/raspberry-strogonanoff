import unittest
from strogonanoff_sender import *
from time import time

def instrumented_busy_wait_until(end_time):
    result = []
    while (True):
        t = time()
        result.append(t)
        if t >= end_time:
            return result

class Strogonanoff_SenderTest(unittest.TestCase):

    def test_int_to_bit_list(self):
        self.assertEqual([0], int_to_bit_list(0, 1))
        self.assertEqual([1], int_to_bit_list(1, 1))
        self.assertEqual([1, 0], int_to_bit_list(1, 2))
        self.assertEqual([0, 1], int_to_bit_list(2, 2))
        self.assertEqual([1, 1, 0, 0], int_to_bit_list(3, 4))

    def test_encode_as_state_list(self):
        self.assertEqual([0], encode_as_state_list([0]))
        self.assertEqual([0, 0, 0], encode_as_state_list([1]))
        self.assertEqual([0, 1, 1, 1], encode_as_state_list([0, 1]))
        self.assertEqual([0, 0, 0, 1], encode_as_state_list([1, 0]))

    def test_encode_packet(self):
        preamble = [0] * 26
        postamble = [0, 0]

        self.assertEquals(preamble + [1] + postamble, encode_packet([]))
        self.assertEquals(preamble + [1] + [0, 1, 1, 1] + postamble, encode_packet([0, 1]))

    def test_command_as_bit_list(self):
        self.assertEquals(int_to_bit_list(channel_codes[0][0], 32) + int_to_bit_list(on_code, 16),
            command_as_bit_list(1, 1, True))
        self.assertEquals(int_to_bit_list(channel_codes[1][2], 32) + int_to_bit_list(off_code, 16),
            command_as_bit_list(2, 3, False))

    def test_busy_wait_until(self):
        end_time = time() + default_pulse_width
        times = instrumented_busy_wait_until(end_time)
        self.assertTrue(time() - end_time < default_pulse_width / 10)
        self.assertTrue(len(times) > 10)

if __name__ == "__main__":
    unittest.main()