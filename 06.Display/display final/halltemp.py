import csv, os
from time import gmtime, strftime
# rpm
import RPi.GPIO as GPIO
import time
# adxl code
import smbus
import time
from time import sleep
# display
import time, datetime, sys
import pygame, time, os, csv
from pygame.locals import *
#temp
import glob

# Globals
rpm = 0
speed = 0
coolantTemp = 20
throttlePosition = 0
timingAdvance = 0
gear = 0
black = (0,0,0)
WHITE = (255,255,255)

#temp dec
os.system('modprobe w1-gpio')                              # load one wire communication device kernel modules
os.system('modprobe w1-therm')                                                 
base_dir = '/sys/bus/w1/devices/'                          # point to the address
device_folder = glob.glob(base_dir + '28*')[0]             # find device with address starting from 28*
device_file = device_folder + '/w1_slave'                  # store the details
#temp dec end

# rpm
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# rpm end

# select the correct i2c bus for this revision of Raspberry Pi
revision = ([l[12:-1] for l in open('/proc/cpuinfo', 'r').readlines() if l[:8] == "Revision"] + ['0000'])[0]
bus = smbus.SMBus(1 if int(revision, 16) >= 4 else 0)

startTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# rpm
pulse = 0
distance = 0
rpm = 0
speed = 0
wheel_c = 62.8  # circumfrence of the wheel in cm
hall = 14
elapse = 0.00
multiplier = 0

start = time.time()
GPIO.setup(hall, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# display

# Set up the window. If piTFT flag is set, set up the window for the screen. Elsecreate it normally for use on normal monitor.
pygame.init()
pygame.mouse.set_visible(0)
windowSurface = pygame.display.set_mode((607, 287))
bg = pygame.image.load("b1.jpg")

#temp func
def read_temp_raw():
   f = open(device_file, 'r')
   lines = f.readlines()                                   # read the device details
   f.close()
   return lines

def read_temp():
   lines = read_temp_raw()
   while lines[0].strip()[-3:] != 'YES':                   # ignore first line
      time.sleep(0.2)
      lines = read_temp_raw()
   equals_pos = lines[1].find('t=')                        # find temperature in the details
   if equals_pos != -1:
      temp_string = lines[1][equals_pos+2:]
      temp_c = float(temp_string) / 1000.0                 # convert to Celsius
      temp_f = temp_c * 9.0 / 5.0 + 32.0                   # convert to Fahrenheit 
      return temp_c
#temp func end

# Helper function to draw the given string at coordinate x,y, relative to center.
def drawText(string, x, y, font):
    if font == "readout":
        text = readoutFont.render(string, True,black )
    elif font == "label":
        text = labelFont.render(string, True,black)
    elif font == "fps":
        text = fpsFont.render(string, True, black)
    textRect = text.get_rect()
    textRect.centerx = windowSurface.get_rect().centerx + x
    textRect.centery = windowSurface.get_rect().centery + y
    windowSurface.blit(text, textRect)

# Set up fonts
pygame.init()
readoutFont = pygame.font.Font("Mohave-Regular.ttf", 30)
labelFont = pygame.font.Font("Mohave-Regular.ttf", 20)
fpsFont = pygame.font.Font("Mohave-Regular.ttf", 10)

# Set the caption.
pygame.display.set_caption("TEAM PRAVEG")

# Create a clock object to use so we can log every second.
clock = pygame.time.Clock()
# display end

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

# log the data
# Function to create a csv with the specified header.
def createLog(header):
    # Write the header of the csv file.
    with open('/home/pi/' + str(startTime) + '.csv', 'wb') as f:
        w = csv.writer(f)
        w.writerow(header)

# Function to append to the current log file.
def updateLog(data):
    with open('/home/pi/' + str(startTime) + '.csv', 'a') as f:
        w = csv.writer(f)
        w.writerow(data)

# Function to close the log and rename it to include end time.
def closeLog():
    endTime = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    os.rename('home/pi/' + str(startTime) + '.csv', 'logs/' + startTime + "_" +
              endTime + '.csv')

if __name__ == "__main__":
    # if run directly we'll just create an instance of the class and output
    # the current readings
    time.sleep(1)
    GPIO.add_event_detect(hall, GPIO.FALLING, callback=get_pulse, bouncetime=20)
    #header = ["time", "axisX", " axisY ", " axisZ", "Rpm", "Speed", "Distance"]
    #createLog(header)
    while (True):
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        windowSurface.blit(bg,(10,10))            

        # Draw the RPM readout and label.
        drawText(str(int(rpm)), -5, -10, "readout")
        drawText("RPM", -5, 20, "label")

        # Draw the intake temp readout and label.
        #   drawText( str (intakeTemp) + "\xb0C" , 190, 105, "readout" )
        #   drawText( "Intake" , 190, 140, "label" )

        # Draw the coolant temp readout and label.
        drawText(str(coolantTemp) + "\xb0C", -120, 60, "readout")
        drawText("Coolant", -130, 95, "label")

        # Draw the gear readout and label.
        drawText(str(int(distance)), -130, -105, "readout")   #Distance in cm
        drawText("Distance", -130, -80, "label")

        # Draw the speed readout and label.
        drawText(str(int(speed)) + "kmph", 120, 60, "readout")
        drawText("Speed", 130, 95, "label")

        # Draw the throttle position readout and label.
        drawText(str(throttlePosition) + " %", 130, -105, "readout")
        drawText("Throttle", 130, -80, "label")

        # Draw the MAF readout and label.
        #   drawText( str (MAF) + " g/s" , -150, -145, "readout" )
        #   drawText( "MAF" , -190, -110, "label" )

        # Draw the engine load readout and label.
        #   drawText( str (engineLoad) + " %" , 0, -145, "readout" )
        #   drawText( "Load" , 0, -110, "label" )

        # Update the clock.
        dt = clock.tick()
        # draw the window onto the screen
        pygame.display.update()
        print('rpm:{0:.1f} speed:{1:.0f} distance:{2}'.format(rpm, speed,distance))  # this only prints rpm, speed, and distance        
        time.sleep(.5)
        # adxl end

        # temp output
        print(read_temp())                                      # Print temperature
        coolantTemp = read_temp()
        # temp end  rem to pass to the display

        # get the system performance data over 20 seconds.
        Rpm = rpm
        Speed = speed
        Distance = distance
        data = [strftime("%Y-%m-%d %H:%M:%S", gmtime()), Rpm, Speed, Distance,coolantTemp]
        updateLog(data)
        windowSurface.fill(black)
        time.sleep(.5)  # trying to make the display update with each pass of the hall sensor
        try:
            print("")
        except KeyboardInterrupt:
            print('Guess that\'s the end of your trip, huh?')
            closeLog()
            GPIO.cleanup()
