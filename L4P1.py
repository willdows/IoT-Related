
# Imports
from itsc305gpiozero import Button
from time import sleep
import I2C_LCD_display
from mpu6500 import MPU6500
from machine import Pin, I2C
import network
import sys
from umqtt.simple import MQTTClient

# Wifi Config
WIFI_SSID = 'SLAVIC-MALWARE'
WIFI_PASSWORD = 'SLAVIC-MALWARE'

# ThingSpeak config
THINGSPEAK_MQTT_SERVER:   str = "mqtt3.thingspeak.com"
THINGSPEAK_MQTT_PORT:     int = "1883"
THINGSPEAK_CHANNEL_ID:    str = "2465106"
THINGSPEAK_CLIENT_ID:     str = "JTwAODgDOjwcKiEuCh4MKzs"
THINGSPEAK_USERNAME:      str = "JTwAODgDOjwcKiEuCh4MKzs"
THINGSPEAK_PASSWORD:      str = "eKxA2tcpKSYGixsalrdggU94"
THINGSPEAK_PUBLISH_TOPIC: str = f"channels/{THINGSPEAK_CHANNEL_ID}/publish"

# LCD Init
mylcd = I2C_LCD_display.lcd()
mylcd.lcd_clear()
mylcd.backlight(1)

# Menu Init
menu_list = ["Gyro","Acceleration","Temperature"]
position = 0

# Button init
buttonClockwise = Button(16, bounce_time = 13)
buttonCounterClock = Button(17, bounce_time = 13)
buttonPressed = Button(18, bounce_time = 13)

# Sensor init
sdaPIN=Pin(14)
sclPIN=Pin(15)
i2c=I2C(1,sda=sdaPIN, scl=sclPIN, freq=40000)
addr = 0x68

# Initialize the MPU sensor
sensorMPU = MPU6500(i2c, address=addr,wh_response=0x68)

# Publish
def publish_data(sensor_in):
    client = MQTTClient(client_id=THINGSPEAK_CLIENT_ID, server=THINGSPEAK_MQTT_SERVER, user=THINGSPEAK_USERNAME, password=THINGSPEAK_PASSWORD, ssl=False)
    client.connect()

    pub_topic = "field1=" + str(sensor_in)
    client.publish(THINGSPEAK_PUBLISH_TOPIC, pub_topic)
    print("Published: " + pub_topic)


# Establish wifi connection
def connect():
    attempt_count = 0
    max_attempts = 30
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Connecting to network: {WIFI_SSID}")
        attempt_count += 1
        if attempt_count >= max_attempts:
            sys.exit()
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass

    print(f"Connected to: {WIFI_SSID}")
    

def updateScreen():
    global position
    mylcd.lcd_clear()

    if position > 2:
        position = 0
    elif position < 0:
        position = 2
    else:
        position = position

    menu_option = menu_list[position]
    mylcd.lcd_display_string(menu_option)

def buttonRotate():
    global position
    if buttonCounterClock.value == 0:
        position += 1
    elif buttonCounterClock.value == 1:
        position -= 1

    updateScreen()

def pressedbutton():
    global position
    mylcd.lcd_clear()
    if position == 0:
       # print(f'{sensorMPU.gyro=}')  
        senseout = str(sensorMPU.gyro)
        mylcd.lcd_clear()
        mylcd.lcd_display_string(senseout)
        publish_data(senseout)

    elif position == 1:
       # print(f'{sensorMPU.acceleration=}')
        senseout = str(sensorMPU.acceleration)
        mylcd.lcd_clear()
        mylcd.lcd_display_string(senseout)
        publish_data(senseout)

    elif position == 2:
        #print(f'{sensorMPU.temperature=}')
        senseout = str(sensorMPU.temperature)
        mylcd.lcd_clear()
        mylcd.lcd_display_string(senseout)
        publish_data(senseout)
    
    else:
        x = 0

    sleep(0.5)


buttonClockwise.when_pressed = buttonRotate
buttonPressed.when_pressed = pressedbutton

connect()

try:
    while True:
        i=1
       # print(position)
        sleep(0.5)

except:
    print("Exiting Program...")