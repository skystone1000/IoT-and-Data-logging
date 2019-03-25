import csv , os
from time import gmtime, strftime

# rpm
import RPi.GPIO as GPIO
import time
# rpm end

# adxl code
import smbus
import time
from time import sleep

# rpm
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# rpm end

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
# adxl code end


startTime = 1

# rpm
pulse = 0
distance = 0
rpm = 0.00
speed = 0.00
wheel_c = 260  # circumfrence of the wheel in cm
hall = 14
elapse = 0.00
multiplier = 0

start = time.time()
GPIO.setup(hall, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_rpm():
    return rpm

def get_speed():
    return speed

def get_distance():
    return distance

def get_elapse():
    return elapse

def get_pulse(number):
    global elapse, distance, start, pulse, speed, rpm, multiplier
    cycle = 0
    pulse += 1
    cycle += 1
    if pulse > 0:
        elapse = time.time() - start
        pulse -= 1
    if cycle > 0:
        distance += wheel_c
        cycle -= 1
    multiplier = 3600 / elapse
    speed = (wheel_c * multiplier) / 100000
    rpm = 1 / elapse * 60
    # below is the converter from kmph to mph
    # speed = speed*0.621371
    start = time.time()
# rpm end

# adxl
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


#log the data
# Function to create a csv with the specified header.
def createLog(header):
    # Write the header of the csv file.
    with open ( '/home/pi/' + str(startTime) + '.csv' , 'wb' ) as f:
        w = csv.writer(f)
        w.writerow(header)

# Function to append to the current log file.
def updateLog(data):
    with open ( '/home/pi/' + str(startTime) + '.csv' , 'a' ) as f:
        w = csv.writer(f)
        w.writerow(data)

# Function to close the log and rename it to include end time.
def closeLog():
    endTime = datetime.datetime.today().strftime( '%Y%m%d%H%M%S' )
    os.rename( 'home/pi/' + str(startTime) + '.csv' , 'logs/' + startTime + "_" +
endTime + '.csv' )



if __name__ == "__main__":
    # if run directly we'll just create an instance of the class and output
    # the current readings
    adxl345 = ADXL345()

    time.sleep(1)
    GPIO.add_event_detect(hall, GPIO.FALLING, callback=get_pulse, bouncetime=20)
    
    
    header=["time","axisX" ," axisY "," axisZ" ,"Rpm","Speed","Distance"]
    createLog(header)

    while(True):
        time.sleep(.5)  # trying to make the display update with each pass of the hall sensor
        print('rpm:{0:.1f} speed:{1:.0f} distance:{2}'.format(rpm, speed,
                                                              distance))  # this only prints rpm, speed, and distance
    
        axes = adxl345.getAxes(True)
        print("ADXL345 on address :")
        print("   x = {:.3f}G".format(axes['x']))
        print("   y = {:.3f}G".format(axes['y']))
        print("   z = {:.3f}G".format(axes['z']))
        time.sleep(.5)
        # adxl end
    
        # get the system performance data over 20 seconds.
        axisX = axes['x']
        axisY = axes['y']
        axisZ = axes['z']
        Rpm = rpm
        Speed = speed
        Distance = distance
        
        data=[strftime("%Y-%m-%d %H:%M:%S", gmtime()),axisX ,axisY ,axisZ ,Rpm,Speed,Distance]
        updateLog(data)

        try:
            print("")

        except KeyboardInterrupt:
            print('Guess that\'s the end of your trip, huh?')
            closeLog()
            GPIO.cleanup()
                  