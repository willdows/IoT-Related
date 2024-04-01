from time import sleep
import network, machine

WIFI_SSID = ""
WIFI_PASS = ""

WifiLed = machine.Pin("LED", machine.Pin.OUT)
WifiLed.value(0)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.scan()
wlan.isconnected()
wlan.connect(WIFI_SSID, WIFI_PASS)

while not wlan.isconnected():
    machine.idle()

print("Connected to WiFi")
WifiLed.value(1)

while True:
    print("computing")
    sleep(5)
    if not wlan.isconnected():
        print("disconnected from WiFi")
        WifiLed.value(0)
