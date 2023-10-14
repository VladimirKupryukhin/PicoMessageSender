from machine import Pin
import time
    
class Button:
    def __init__(self, pin):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)
        
        
    def isPressed(self):
        if self.button.value() == 0:
            print("Button is pressed")
        else:
            print("Button is not pressed")
        
