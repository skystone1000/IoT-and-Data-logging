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
        time.sleep(.5) #trying to make the display update with each pass of the hall sensor
        print('rpm:{0:.1f} speed:{1:.0f} distance:{2}'.format(rpm,speed,distance)) #this only prints rpm, speed, and distance
        


except KeyboardInterrupt:
    print('Guess that\'s the end of your trip, huh?')
    GPIO.cleanup()
