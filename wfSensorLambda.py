#
# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#

# greengrassHelloWorld.py
# Demonstrates a simple publish to a topic using Greengrass core sdk
# This lambda function will retrieve underlying platform information and send
# a hello world message along with the platform information to the topic
# 'hello/world'. The function will sleep for five seconds, then repeat.
# Since the function is long-lived it will run forever when deployed to a
# Greengrass core.  The handler will NOT be invoked in our example since
# the we are executing an infinite loop.

import greengrasssdk
import logging
import sys
from threading import Timer
import json
from datetime import datetime
from datetime import timezone
import random
import grovepi
from grove_rgb_lcd import *

# Setup logging to stdout
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
sensor_topic = 'waterflower/sensor/telemetry'

# Grovepi sensor connections
temp_sensor = 0             # Port A0
mois_sensor = 1             # Port A1
light_sensor = 2            # Port A2
relay = 6                   # Port D6

tooDry = 100
justRight = 300
tooWet = 500

# When deployed to a Greengrass core, this code will be executed immediately
# as a long-lived lambda function.  The code will enter the infinite while
# loop below.
# If you execute a 'test' on the Lambda Console, this test will fail by
# hitting the execution timeout of three seconds.  This is expected as
# this function never returns a result.

def calcColorAdj(variance):     # Calc the adjustment value of the background color
    "Because there is 200 mapping to 255 values, 1.275 is the factor for 400 spread"
    factor = 1.275;
    adj = abs(int(factor * variance));
    if adj > 255:
        adj = 255;
    return adj;

def calcBG(humidity):
    "This calculates the color value for the background"
    variance = humidity - justRight;   # Calculate the variance
    adj = calcColorAdj(variance);   # Scale it to 8 bit int
    bgList = [0,0,0]               # initialize the color array
    if(variance < 0):
        bgR = 0;                    # too dry, no red
        bgB = adj;                  # green and blue slide equally with adj
        bgG = 255 - adj;

    elif(variance == 0):             # perfect, all on green
        bgR = 0;
        bgB = 0;
        bgG = 255;

    elif(variance > 0):             #too wet - no blue
        bgB = 0;
        bgR = adj;                  # Red and Green slide equally with Adj
        bgG = 255 - adj;

    bgList = [bgR,bgG,bgB]          #build list of color values to return
    return bgList;

def greengrass_sensor_run():
    try:
        temp_value = 0.1
        mois_value = 0
        light_value = 0
        switch_status = 0
        lastTemp = 0.1
        lastMois = 0
        # Get value from temperature sensor
        temp_value = grovepi.temp(temp_sensor,"1.2")
        #temp_value = random.uniform(22.0, 23.9)
        # Get value from moisture sensor
        mois_value = grovepi.analogRead(mois_sensor)
        #mois_value = random.randint(150,350)
        # Get value from light sensor
        light_value = grovepi.analogRead(light_sensor)
        #light_value = random.randint(590,620)
        moment = "D" if light_value > 200 else "N"
        # Get status from relay
        switch_status = grovepi.digitalRead(relay)
        #switch_status = random.randint(0,1)
        # Set temperature and moisture to LCD
        if (abs(temp_value - lastTemp) >= 0.1) or (mois_value != lastMois):
            lastTemp = temp_value
            lastMois = mois_value
            bgList = calcBG(mois_value)
            setRGB(bgList[0],bgList[1],bgList[2])
            setText("Temp: %.1f C *%s\nMoisture: %d " %(temp_value,moment,mois_value))

        # build the message to be sent
        message = {"clientId": "sensor001",
                    "timestamp": int(datetime.now(timezone.utc).timestamp()*1000),
                    "temp": format(temp_value,'0.1f'),
                    "moisture": mois_value,
                    "light": light_value,
                    "switch":switch_status}
        logger.info('Triggering publish to topic ' + sensor_topic + ' with ' + json.dumps(message))

        client.publish(
                topic=sensor_topic,
                queueFullPolicy='AllOrException',
                payload=json.dumps(message))
    except IOError:
        logger.error('IO Error')
    except Exception as e:
        logger.error('Failed to publish message: ' + repr(e))

    # Asynchronously schedule this function to be run again in 5 seconds
    Timer(5, greengrass_sensor_run).start()


# Start executing the function above
greengrass_sensor_run()


# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    return
