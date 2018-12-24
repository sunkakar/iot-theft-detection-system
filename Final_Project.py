'''
Class   : CSCI 43300
Name    : Sundeep Kakar, Navdeep Singh
Project : Theft Detection System 

'''
# Import Libraries #
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from picamera import PiCamera
from SimpleCV import *
from time import sleep
from datetime import datetime
from coapthon import defines

import os
import time
# RPi.GPIO library used with Buzzer and LED implementation
import RPi.GPIO as GPIO
from time import sleep


# Global Variables #

BuzzerPin = 11          # Buzzer GPIO Pin
LEDPin = 8              # LED GPIO Pin 
MODE_VAL = '0'          # Theft Detection System Mode Variable 


# IMAGE FUNCTIONS #

# Function: Takes Initial Image of object
def takeInitialImage():
   print("\nTaking Initial Image...")
   camera = PiCamera()
   camera.start_preview()   
   sleep(7)              # Delay added to let the camera adjust to the lighting
   camera.capture('/home/pi/Desktop/Initial_Item_Image/init_image.png')
   camera.stop_preview()
   camera.close()       # *Closeing important since Camera is envokes in multiple function 

# Function: Takes Images 
def takeImage():
   camera = PiCamera()      # Starts the camera
   camera.start_preview()   # Begin preview
   delay = 5                # Delay between images
   print('Beginning Capture... ')

   camera.capture('/home/pi/Desktop/ImagesCaptured/'+ str(datetime.now()) + '.png') #To Archive Folder
   camera.capture('/home/pi/Desktop/Pulled_Item_Image/pulled_image.png')            #To Comparison Folder
   sleep(delay) # Delay in between pictures
 
   camera.stop_preview() 
   camera.close() 

# Function: Runs Theft Detection System in Demo Mode
def ImageDemo():
    init_Item = Image("/home/pi/Desktop/Initial_Item_Image/init_image.png")
    sleep(5)
    curr_Item = Image('/home/pi/Desktop/Pulled_Item_Image/pulled_image.png')
    print('\nImages ->')
    init_Item.show()
    sleep(5)
    curr_Item.show()
    sleep(5)
    
    threshold = 2.5                 # Threshold value to be compared with the image matrix mean
    prev_Item = init_Item           
    diff = curr_Item - prev_Item
    matrix = diff.getNumpy()        # Matricizing values into array  
    mean = matrix.mean()    
    print("Matrixval = ",mean)      # Prints mean for analysis
    heading = "Image Difference = Motion" 
    diff.drawText(heading)
    diff.show()
    sleep(5)
    flag = 0
    
    if mean >= threshold:
            print("Motion Detected!")
            flag = 1
            if(checkMode()=='1'):
               print("Buzz")
               Buzzloop(flag)
               
    else:
            print("No Change In Motion")
            flag = 0
    return MotionStatus(flag)       # returns string value indicating if Motion = T or F

# Function: Runs Theft Detection System in Engage Mode. Engage mode runs indefinitely till motion is detected
def ImageAnalysis():

    init_Item = Image("/home/pi/Desktop/Initial_Item_Image/init_image.png")
    prev_Item = init_Item
    flag = 0
    
    while True:

            camera = PiCamera() #starts the camera
            camera.capture('/home/pi/Desktop/ImagesCaptured/'+ str(datetime.now()) + '.png') #To Archive
            sleep(5)
            camera.capture('/home/pi/Desktop/Pulled_Item_Image/pulled_image.png')            #To Comparison Folder
            camera.close()
            
            curr_Item = Image('/home/pi/Desktop/Pulled_Item_Image/pulled_image.png')
            print('\nImages ->')
            prev_Item.show()
            sleep(2)
            curr_Item.show()
            sleep(2)
            
            threshold = 2.5 # Threshold value 
            difference_Item = curr_Item - prev_Item
            matrix = difference_Item.getNumpy()
            mean = matrix.mean()
            print("Matrixval = ",mean) 
            difference_Item.show()
            sleep(5)
            if mean >= threshold:
                   print("Motion Detected!")
                   if(checkMode()=='1'):
                      flag = 1
                      Buzzloop(flag)
                   
            else:
                   print("No Change In Motion")

            prev_Item = curr_Item       # Decentralizes the initial image and loops with current and previous images

            if(flag == 1):
                break
    
    return MotionStatus(flag)

# Function: Returns value Security mode (Active or Standby) 
def checkMode():
    global MODE_VAL
    return MODE_VAL

# Function: Returns string Security mode (Active or Standby)
def displayMode():
    global MODE_VAL
    if(MODE_VAL=='0'):
        return "Standby Mode..."
    elif(MODE_VAL=='1'):
        return "Active  Mode..."


def MotionStatus(status):
    if(status == 0):
        return "No Motion Detected..."
    elif(status == 1):
        return "Motion Detected!"

# Function: Sets Security mode (Active or Standby)
def setMode(mv):
    global MODE_VAL
    MODE_VAL = mv
    print(MODE_VAL)
    if(MODE_VAL=='0'):
        print("MODE: STANDBY")
        GPIO.output(LEDPin, GPIO.LOW)       # LED indicates the mode
    elif(MODE_VAL == '1'):
        print("MODE: LOCK DOWN!")
        GPIO.output(LEDPin, GPIO.HIGH)
    return MODE_VAL

# Function: Runs the buzzer module 
def Buzzloop(num):  
    if(num==1):
        max_time = time.time() + 10                 
	while time.time()<max_time:             # Timer implemented to end loop after 10 seconds
		GPIO.output(BuzzerPin, GPIO.HIGH)
		time.sleep(0.01)
		GPIO.output(BuzzerPin, GPIO.LOW)
		time.sleep(0.01)


# CoAP RESOURCES #

# Resource class: Basic Hello World Resource 
class HelloWorld(Resource):
    def __init__(self, name="HelloWorld", coap_server=None):
        super(HelloWorld, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = str("Hello!")
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"
        
    def render_GET(self, request):
        #self.payload = "Hello"
        self.content_type = "text/plain"
        return self

  
    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = HelloWorld()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

# Resource class: GET runs takeinitialImage() 
class InitialImageSet(Resource):

    def __init__(self, name="InitialImageSet", coap_server=None):
        super(InitialImageSet, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = 'Initial Image Saved!'
        
    def render_GET(self, request):
        takeInitialImage()
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        print(self.payload)
        return self

    def render_POST(self, request):
        res = InitialImageSet()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

# Resource class: GET and PUT Security mode
class SetMode(Resource):
    def __init__(self, name="SetMode", coap_server=None):
        super(SetMode, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Enter Buzzer Mode? [0-OFF | 1-ON]: "

    def render_GET(self, request):
        self.payload = displayMode()
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        setMode(self.payload)
        print(self.payload)
        return self

    def render_POST(self, request):        
        res = SetMode()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

#Theft Detection Value
TDSval = 0

# Resource class: GET returns mode chosen, PUT allows to you to choose between Engage or Demo 
class BeginTDS(Resource):
    
    def __init__(self, name="BeginTDS", coap_server=None):       
        super(BeginTDS, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "ENGAGE / DEMO"

    def render_GET(self, request):
        global TDSval
        
        if(TDSval == 1):
            print("Engage!")
            takeImage()
            self.payload = ImageAnalysis()
            return self
        elif(TDSval == 2):
            print("Demo!")
            takeInitialImage()
            takeImage()
            self.payload = ImageDemo()
            return self
        elif(TDSval == 0):
            return self

        print("Here")
        return self

    def render_PUT(self, request):
        global TDSval

        if(request.payload in {"Engage","ENGAGE","E"}):
            TDSval = 1
        elif(request.payload in {"D","DEMO","Demo"}):
            TDSval = 2
        return self

    def render_POST(self, request):
        res = BeginTDS()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

# COAP SERVER #

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        
        self.add_resource('HelloWorld/', HelloWorld())
        self.add_resource('InitialImageSet/', InitialImageSet())
        self.add_resource('SetMode/', SetMode())
        self.add_resource('TheftDetectionSystem/',BeginTDS())

# MAIN FUNCTION #

def main():
    server = CoAPServer("0.0.0.0", 5683)    # Server IP
    print("CoAP Server Running...")
    try:
        server.listen(10)
        
    except KeyboardInterrupt:
        print ("Server Shutdown")
        server.close()
        GPIO.output(BuzzerPin, GPIO.LOW)
	    GPIO.cleanup()                      # Frees the GPIO so pins are not in use anymore
        print ("Exiting...")



if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(BuzzerPin, GPIO.OUT)
    GPIO.output(BuzzerPin, GPIO.LOW)
    GPIO.setup(LEDPin, GPIO.OUT, initial=GPIO.LOW)
    main()
