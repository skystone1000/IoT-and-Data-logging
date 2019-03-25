from __future__ import print_function
import paho.mqtt.publish as publish
import psutil
import string
import random

import RPi.GPIO as GPIO 
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pulse = 0
distance = 0
rpm = 0.00
speed = 0.00
wheel_c = 260 #circumfrence of the wheel in cm
hall = 14
elapse = 0.00
multiplier = 0

start = time.time()

GPIO.setup(hall, GPIO.IN, pull_up_down = GPIO.PUD_UP)

string.alphanum='1234567890avcdefghijklmnopqrstuvwxyzxABCDEFGHIJKLMNOPQRSTUVWXYZ'

# The ThingSpeak Channel ID.
# Replace <YOUR-CHANNEL-ID> with your channel ID.
channelID = "439590"

# The Write API Key for the channel.
# Replace <YOUR-CHANNEL-WRITEAPIKEY> with your write API key.
writeAPIKey = "YZ9R34P22L8MIEZM"

# The Hostname of the ThingSpeak MQTT broker.
mqttHost = "mqtt.thingspeak.com"

# You can use any Username.
mqttUsername = "adxl345"

# Your MQTT API Key from Account > My Profile.
mqttAPIKey ="IWXEECF95W6JFCKY"


tTransport = "websockets"
tPort = 80



# Create the topic string.
topic = "channels/" + channelID + "/publish/" + writeAPIKey


def get_rpm():
    return rpm

def get_speed():
    return speed

def get_distance():
    return distance

def get_elapse():
    return elapse 

def get_pulse(number):
    global elapse,distance,start,pulse,speed,rpm,multiplier
    cycle = 0
    pulse+=1
    cycle+=1
    if pulse > 0:
        elapse = time.time() - start
        pulse-=1
    if cycle > 0:
        distance += wheel_c
        cycle -= 1
    multiplier = 3600/elapse
    speed = (wheel_c*multiplier)/100000
    rpm = 1/elapse *60
   #below is the converter from kmph to mph 
    #speed = speed*0.621371

    start = time.time()



try:
    time.sleep(1)
    GPIO.add_event_detect(hall,GPIO.FALLING,callback = get_pulse,bouncetime=20)
    while True:
        time.sleep(2) #trying to make the display update with each pass of the hall sensor
        print('rpm:{0:.1f} speed:{1:.0f} distance:{2}'.format(rpm,speed,distance)) #this only prints rpm, speed, and distance
        
        clientID='bac4207e751a45a7aa9078e1563ea339'

        # Create a random clientID.
        for x in range(1,16):
            clientID+=random.choice(string.alphanum)
    
        # get the system performance data over 2 seconds.
        cpuPercent = rpm
        ramPercent = speed
    
        # build the payload string.
        payload = "field1=" + str(cpuPercent) + "&field2=" + str(ramPercent)
    
    
        # attempt to publish this data to the topic.
        try:
            publish.single(topic, payload, hostname=mqttHost, transport=tTransport, port=tPort,auth={'username':mqttUsername,'password':mqttAPIKey})
    
        except (KeyboardInterrupt):
            break
    
        except:
            print ("There was an error while publishing the data.")
    


except KeyboardInterrupt:
    print('Guess that\'s the end of your trip, huh?')
    GPIO.cleanup()
