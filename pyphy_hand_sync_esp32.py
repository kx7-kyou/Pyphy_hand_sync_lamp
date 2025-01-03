import network
import socket
import machine
import time
from machine import Pin, SoftI2C
from neopixel import NeoPixel
import ssd1306

pin = Pin(14, Pin.OUT)
np = NeoPixel(pin, 12)
i2c = SoftI2C(sda=Pin(22), scl=Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

display.fill(0)
display.show()

#wifi setting
ssid = 'SSID'
password = 'PW'

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)
sta_if.active(True)
sta_if.connect(ssid, password)

while not sta_if.isconnected():
    print('Connecting to WiFi:', ssid+":"+password)
    time.sleep(1)

print('Connected to WiFi')
print('IP Address:', sta_if.ifconfig()[0])

#PWM pin setting
led = machine.Pin(2, machine.Pin.OUT)
pwm = machine.PWM(led)
pwm.freq(1000)

#UDP socket setting
UDP_IP = sta_if.ifconfig()[0]  #ip
UDP_PORT = 1235
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print('Listening for incoming UDP messages...')

def display_rgb(r, g, b):

    display.fill(0)

    display.text("R: {}".format(r), 0, 0)
    display.text("G: {}".format(g), 0, 20)
    display.text("B: {}".format(b), 0, 40)

    display.show()
    return 0

while True:
    
    data, addr = sock.recvfrom(1024)
    RGB = data.decode() #decoding
    print(f"Received RGB: {RGB}")

    RGB = RGB.strip('[]')
    RGB_values = RGB.split(",")

    if len(RGB_values) == 3:
        try:
            r, g, b = [int(value) for value in RGB_values]
            
            
            for i in range(0, 12):
                np[i] = (r, g, b)
            np.write()
            display_rgb(r, g, b)
            
        except ValueError:
            print(f"Invalid RGB values received: {RGB_values}")
    else:
        print(f"Incorrect number of values in the received data: {RGB_values}")

