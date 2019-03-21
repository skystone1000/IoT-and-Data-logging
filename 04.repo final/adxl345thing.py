
# publish
from __future__ import print_function
import paho.mqtt.publish as publish
import psutil
import string
import random
# publish end

import smbus
import time
from time import sleep

# select the correct i2c bus for this revision of Raspberry Pi
revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

# ADXL345 constants
EARTH_GRAVITY_MS2 = 9.80665
SCALE_MULTIPLIER = 0.004

DATA_FORMAT = 0x31
BW_RATE = 0x2C
POWER_CTL = 0x2D

BW_RATE_1600HZ = 0x0F
BW_RATE_800HZ = 0x0E
BW_RATE_400HZ = 0x0D
BW_RATE_200HZ = 0x0C
BW_RATE_100HZ = 0x0B
BW_RATE_50HZ = 0x0A
BW_RATE_25HZ = 0x09

RANGE_2G = 0x00
RANGE_4G = 0x01
RANGE_8G = 0x02
RANGE_16G = 0x03

MEASURE = 0x08
AXES_DATA = 0x32

string.alphanum = '1234567890avcdefghijklmnopqrstuvwxyzxABCDEFGHIJKLMNOPQRSTUVWXYZ'

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
mqttAPIKey = "IWXEECF95W6JFCKY"

tTransport = "websockets"
tPort = 80

# Create the topic string.
topic = "channels/" + channelID + "/publish/" + writeAPIKey


class ADXL345:
    address = None

    def __init__(self, address=0x53):
        self.address = address
        self.setBandwidthRate(BW_RATE_100HZ)
        self.setRange(RANGE_2G)
        self.enableMeasurement()

    def enableMeasurement(self):
        bus.write_byte_data(self.address, POWER_CTL, MEASURE)

    def setBandwidthRate(self, rate_flag):
        bus.write_byte_data(self.address, BW_RATE, rate_flag)

    # set the measurement range for 10-bit readings
    def setRange(self, range_flag):
        value = bus.read_byte_data(self.address, DATA_FORMAT)

        value &= ~0x0F;
        value |= range_flag;
        value |= 0x08;

        bus.write_byte_data(self.address, DATA_FORMAT, value)

    # returns the current reading from the sensor for each axis
    #
    # parameter gforce:
    #    False (default): result is returned in m/s^2
    #    True           : result is returned in gs
    def getAxes(self, gforce=False):
        bytes = bus.read_i2c_block_data(self.address, AXES_DATA, 6)

        x = bytes[0] | (bytes[1] << 8)
        if (x & (1 << 16 - 1)):
            x = x - (1 << 16)

        y = bytes[2] | (bytes[3] << 8)
        if (y & (1 << 16 - 1)):
            y = y - (1 << 16)

        z = bytes[4] | (bytes[5] << 8)
        if (z & (1 << 16 - 1)):
            z = z - (1 << 16)

        x = x * SCALE_MULTIPLIER
        y = y * SCALE_MULTIPLIER
        z = z * SCALE_MULTIPLIER

        if gforce == False:
            x = x * EARTH_GRAVITY_MS2
            y = y * EARTH_GRAVITY_MS2
            z = z * EARTH_GRAVITY_MS2

        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)

        return {"x": x, "y": y, "z": z}


if __name__ == "__main__":
    # if run directly we'll just create an instance of the class and output
    # the current readings
    adxl345 = ADXL345()
    while True:
        axes = adxl345.getAxes(True)
        print("ADXL345 on address :")
        print("   x = {:.3f}G".format(axes['x']))
        print("   y = {:.3f}G".format(axes['y']))
        print("   z = {:.3f}G".format(axes['z']))
        time.sleep(.5)
        clientID = 'bac4207e751a45a7aa9078e1563ea339'

        # Create a random clientID.
        for x in range(1, 16):
            clientID += random.choice(string.alphanum)
        
        # get the system performance data over 20 seconds.
        axisX = axes['x']
        axisY = axes['y']
        axisZ = axes['z']
        
        # build the payload string.
        payload = "field1=" + str(axisX) + "field2=" + str(axisY) + "&field3=" + str(axisZ)
        
        # attempt to publish this data to the topic.
        try:
            publish.single(topic, payload, hostname=mqttHost, transport=tTransport, port=tPort,
                           auth={'username': mqttUsername, 'password': mqttAPIKey})
            print(" Published axis X =", axisX, " axis Y =", axisY, "axis Z =", axisZ, " to host: ", mqttHost, " clientID= ", clientID)
        except:
            print("There was an error while publishing the data.")        
