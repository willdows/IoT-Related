"""
Written by Lubos Kuzma
December 2022

!!! Written in MicroPython for Pico-W !!!

Example of MQTT protocol Publish function
This example uses MQTT v3.11 to subscribe to "Field 5" topic of my private ThingSpeak Channel

""" 

from time import sleep
from random import randint
from umqtt.simple import MQTTClient
import network
import machine
from usocket import socket

# Need to create device to handle privledges, API key not needed anymore

MQTT_CLIENT_ID = "will_test" # This is for your own client identification. Can be anything
MQTT_USERNAME = "willdows8" #This is the ThingsSpeak's Author
MQTT_PASSWD = "2MHMZ9CB1GH6PTS8" #This is the MQTT API Key found under My Profile in ThingSpeak
MQTT_HOST = "mqtt3.thingspeak.com" #This is the ThingSpeak hostname
MQTT_PORT = 1883 #Typical port # for MQTT protocol. If using TLS -> 8883
CHANNEL_ID = "2465106" #Channel ID found on ThingSpeak website
MQTT_WRITE_APIKEY = "" # Write API Key found under ThingSpeak Channel Settings
MQTT_PUBLISH_TOPIC = "channels/" + CHANNEL_ID + "/publish"
WIFI_SSID = "eduroam"
WIFI_PASSWD = "Brightspace@99"
WIFI_USER = "william.lohmann@edu.sait.ca"

WiFiLed = machine.Pin("LED", machine.Pin.OUT)
WiFiLed.value(0)

def w5x00_init():
    spi=SPI(0,2_000_000, mosi=Pin(19),miso=Pin(16),sck=Pin(18))
    nic = network.WIZNET5K(spi,Pin(17),Pin(20))
    nic.active(True)
    nic.ifconfig('dhcp')

    print('IP address :', nic.ifconfig())
    while not nic.isconnected():
        sleep(1)
        print(nic.regs())



wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.scan()
wlan.isconnected()

#wlan.connect(WIFI_SSID, WIFI_PASSWD)
wlan.connect(WIFI_SSID, key=(network.WLAN.WPA2_ENT, WIFI_USER, WIFI_PASSWD))

while not wlan.isconnected():
    machine.idle()

print("Connected to Wifi")
WiFiLed.value(1)

""" create client instance"""
client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, user=MQTT_USERNAME, password=MQTT_PASSWD, ssl=False)
client.connect(clean_session=True)


while True:
    sleep(1)
    pub_topic = "field1=" + str(randint(0, 500)/100) #publish random number between 0.00 and 4.99 to Field 5 of ThingSpeak Channel
    client.publish(MQTT_PUBLISH_TOPIC, pub_topic)
    print("Published: " + pub_topic)