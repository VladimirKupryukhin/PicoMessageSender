# This example demonstrates a UART periperhal.

import bluetooth
import machine
import random
import struct
import time
from ble_advertising import advertising_payload
from button import Button

from micropython import const

BUTTON_PIN_1 = 12
BUTTON_PIN_2 = 15
BUTTON_PIN_3 = 19
BUTTON_PIN_4 = 16

led = machine.Pin('LED', machine.Pin.OUT)


_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("0000181a-0000-1000-8000-00805f9b34fb")
_UART_TX = (
    bluetooth.UUID("0000181a-0000-1000-8000-00805f9b34fb"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("0000181a-0000-1000-8000-00805f9b34fb"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


class BLESimplePeripheral:
    def __init__(self, ble, name="mpy-uart"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection. Alsways connects when there is an available node.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback



def demo():
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)

    def on_rx(v):
        print("RX", v)

    p.on_write(on_rx)
    
    def button1Callback():
        dataStr = "B1".encode()
        p.send(dataStr)
        print("Button1 pressed")

    def button2Callback():
        dataStr = "B2".encode()
        p.send(dataStr)
        print("Button2 pressed")
        
    def button3Callback():
        dataStr = "B3".encode()
        p.send(dataStr)
        print("Button3 pressed")

    def button4Callback():
        dataStr = "B4".encode()
        p.send(dataStr)
        print("Button4 pressed")

    button1 = Button(BUTTON_PIN_1)
    button2 = Button(BUTTON_PIN_2)
    button3 = Button(BUTTON_PIN_3)
    button4 = Button(BUTTON_PIN_4)
        
    shouldTurnOn = 1
    
    for x in range(50):
        led.value(shouldTurnOn)
        if (shouldTurnOn == 1) :
            shouldTurnOn = 0
        else:
            shouldTurnOn = 1
        
        time.sleep_ms(25)
        
    while True:
        if p.is_connected():    
            button1.isPressed(button1Callback)
            button2.isPressed(button2Callback)
            button3.isPressed(button3Callback)
            button4.isPressed(button4Callback)
            
            led.value(shouldTurnOn)
            if (shouldTurnOn == 1) :
                shouldTurnOn = 0
            else:
                shouldTurnOn = 1
            
            
            pass
        else:
            led.off()
                
                
                
        time.sleep_ms(100)


if __name__ == "__main__":
    demo()