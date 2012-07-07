import unittest
from raspwitch import *

class Test(unittest.TestCase):

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
        postamble = [0] * 5

        self.assertEquals(preamble + [1] + postamble, encode_packet([]))
        self.assertEquals(preamble + [1] + [0, 1, 1, 1] + postamble, encode_packet([0, 1]))

    def test_command_as_bit_list(self):
        self.assertEquals(int_to_bit_list(channel_codes[0][0], 32) + int_to_bit_list(on_code, 16),
            command_as_bit_list(1, 1, True))
        self.assertEquals(int_to_bit_list(channel_codes[1][2], 32) + int_to_bit_list(off_code, 16),
            command_as_bit_list(2, 3, False))

    def test_send(self):
        capturingPin = lambda: None # get around to this
        send(capturingPin, [0, 1, 1, 1, 0], 0.005)

    def func_test(self):
        from quick2wire.gpio import Pin, exported
        with exported(Pin(3, Pin.Out)) as out_pin:
            send_command(out_pin, 1, 1, True)


if __name__ == "__main__":
    unittest.main()