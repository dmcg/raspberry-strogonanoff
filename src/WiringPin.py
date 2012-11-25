import wiringpi

wiringpi.wiringPiSetup()

class WiringPin:

    def __init__(self, gpio_number):
        self.gpio_number = gpio_number

    def export(self):
        wiringpi.pinMode(self.gpio_number, wiringpi.OUTPUT)
        return self

    def set_value(self, value):
        wiringpi.digitalWrite(self.gpio_number, value)

    def unexport(self):
        pass # for now