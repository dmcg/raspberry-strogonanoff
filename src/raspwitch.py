import time
import wiringpi

preamble = [0] * 26

channel_codes = [
    [859124533, 861090613, 892547893, 1395864373],
    [859124563, 861090643, 892547923, 1395864403],
    [859125043, 861091123, 892548403, 1395864883],
    [859132723, 861098803, 892556083, 1395872563]
]

on_code = 13107
off_code = 21299

default_pulse_width = 500 * 1e-6

# converts the lowest bit_count bits to a list of ints
def int_to_bit_list(i, bit_count):
    result = []
    shifted = i
    for i in range(0, bit_count):
        result.append(shifted & 0x01)
        shifted = shifted >> 1
    return result

# encodes 0 as a 1 count state change, 1 as a 3 count state change, starting
# with a change to low
def encode_as_state_list(bit_list):
    result = []
    state = 0
    for bit in bit_list:
        result.extend([state] if bit == 0 else [state, state, state])
        state = 1 - state
    return result

def encode_packet(bit_list):
    return preamble + [1] + encode_as_state_list(bit_list)

def command_as_bit_list(channel, button, on):
    return int_to_bit_list(
        channel_codes[channel - 1][button - 1], 32) + \
        int_to_bit_list(on_code if on else off_code, 16)

def busy_wait_until(end_time):
    while (time.time() <= end_time): pass

def send(pin, state_list, pulse_width):
    end_time = time.time()
    for state in state_list:
        end_time = end_time + pulse_width
        wiringpi.digitalWrite(8, state)
        busy_wait_until(end_time)

def send_command(pin, channel, button, on, pulse_width = default_pulse_width):
    send(pin, encode_packet(command_as_bit_list(channel, button, on)), pulse_width)

if __name__ == "__main__":
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(8, 1)
    for i in range(1, 6):
        send_command(8, 1, 1, True)
