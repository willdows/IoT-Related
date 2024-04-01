# Imports
from itsc305gpiozero import Button
from time import sleep
import I2C_LCD_display
from mpu6500 import MPU6500
from machine import Pin, I2C
import network
import sys
from umqtt.simple import MQTTClient
import ubinascii

# Wifi Config
WIFI_SSID = 'SLAVIC-MALWARE'
WIFI_PASSWORD = 'SLAVIC-MALWARE'

# AWS IoT Core configuration
MQTT_CLIENT = str(ubinascii.hexlify(machine.unique_id()))
MQTT_SERVER = "a1wjy3l0nuj5ms-ats.iot.us-east-1.amazonaws.com"
AWS_CERT = "certs/cert.txt"
AWS_KEY = "certs/private.txt"
AWS_PORT = 8883
AWS_TOPIC = "Lab4"

# Function to publish sensor data
def publish_data(data):
    test = open(AWS_CERT,'rb').read()
    client = MQTTClient(client_id=MQTT_CLIENT, 
                        server=MQTT_SERVER, 
                        # port=AWS_PORT, 
                        # keepalive=10000, 
                        ssl=True, 
                        ssl_params={
                            "cert": open(AWS_CERT,'rb').read(), 
                            "key": open(AWS_KEY,'rb').read(), 
                            'server_side': False
                        }
                    )
    # client.settimeout = 1000
    client.connect()
    client.publish(AWS_TOPIC, data)
    print("Uploaded")
    client.disconnect()


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