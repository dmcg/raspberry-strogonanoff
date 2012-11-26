import wiringpi

wiringpi.wiringPiSetup()

class WiringPin:

    def __init__(self, gpio_number, direction="out"):
        self.gpio_number = gpio_number
        self.direction = direction

    def export(self):
        wiringpi.pinMode(self.gpio_number,
            wiringpi.OUTPUT if self.direction == "out" else wiringpi.INPUT)
        return self

    def set_value(self, value):
        wiringpi.digitalWrite(self.gpio_number, value)

    def get_value(self):
        return wiringpi.digitalRead(self.gpio_number)

    def unexport(self):
        pass # for now