from machine import Pin
import time
    
class Button:
    def __init__(self, pin):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)
        
        
    def isPressed(self, callback):
        if self.button.value() == 0:
            callback()
        else:
            print("Button is not pressed")
        
