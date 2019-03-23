#!/usr/bin/python
import time , datetime , sys
import pygame , time , os , csv
from pygame.locals import *


# Globals
rpm = 0
speed = 0
coolantTemp = 20
intakeTemp = 0
MAF = 0
throttlePosition = 0
timingAdvance = 0
engineLoad = 0
tach_iter = 0
gear = 0
connection = None
dtc = None
WHITE = (255,255,255)


# Set up the window. If piTFT flag is set, set up the window for the screen. Elsecreate it normally for use on normal monitor.

pygame.init()
pygame.mouse.set_visible(0)
windowSurface = pygame.display.set_mode((320,240))




# Helper function to draw the given string at coordinate x,y, relative to center.
def drawText(string, x, y, font):
	if font == "readout" :
		text = readoutFont.render(string, True , WHITE)
	elif font == "label" :
		text = labelFont.render(string, True , WHITE)
	elif font == "fps" :
		text = fpsFont.render(string, True , WHITE)
	textRect = text.get_rect()
	textRect.centerx = windowSurface.get_rect().centerx + x
	textRect.centery = windowSurface.get_rect().centery + y
	windowSurface.blit(text, textRect)


# Set up fonts
pygame.init()
readoutFont = pygame.font.Font( "E:\SGGS\supra\display\Mohave-Regular.ttf" ,30)
labelFont = pygame.font.Font( "E:\SGGS\supra\display\Mohave-Regular.ttf" ,20)
fpsFont = pygame.font.Font( "E:\SGGS\supra\display\Mohave-Regular.ttf" ,10)

# Set the caption.
pygame.display.set_caption("TEAM PRAVEG")

# Create a clock object to use so we can log every second.
clock = pygame.time.Clock()



# Run the game loop
while True :
	for event in pygame.event.get():
		if event.type == QUIT:
			
			pygame.quit()
			sys.exit()

	
	
	
	# Draw the RPM readout and label.
	drawText( str (rpm), -5, -10, "readout" )
	drawText( "RPM" , -5, 20, "label" )
		
	# Draw the intake temp readout and label.
#	drawText( str (intakeTemp) + "\xb0C" , 190, 105, "readout" )
#	drawText( "Intake" , 190, 140, "label" )
		
	# Draw the coolant temp readout and label.
	drawText( str (coolantTemp) + "\xb0C" , -120, 60, "readout" )
	drawText( "Coolant" , -130, 95, "label" )
		
	# Draw the gear readout and label.
	drawText( str (gear), -130, -105, "readout" )
	drawText( "Gear" , -130, -80, "label" )
		
	# Draw the speed readout and label.
	drawText( str (speed) + " mph" , 120, 60, "readout" )
	drawText( "Speed" , 130, 95, "label" )


	# Draw the throttle position readout and label.
	drawText( str (throttlePosition) + " %" , 130, -105, "readout" )
	drawText( "Throttle" , 130, -80, "label" )
		
	# Draw the MAF readout and label.
#	drawText( str (MAF) + " g/s" , -150, -145, "readout" )
#	drawText( "MAF" , -190, -110, "label" )
		
	# Draw the engine load readout and label.
#	drawText( str (engineLoad) + " %" , 0, -145, "readout" )
#	drawText( "Load" , 0, -110, "label" )

		

	# Update the clock.
	dt = clock.tick()

	

	
	# draw the window onto the screen
	pygame.display.update()
