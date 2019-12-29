#
# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#

import sys
import logging
import greengrasssdk
import grovepi
import os.path
from datetime import datetime
from datetime import timezone
import time
import json

# Setup logging to stdout
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

client = greengrasssdk.client('iot-data')
control_topic = 'waterflower/relay'

# grovepi connections
relay = 6                   # Port D6

# default threshold
mois_threshold = 300
light_threshold = 200
temp_threshold = 10

file = "/tmp/threshold_setting"

def get_input_topic(context):
    try:
        topic = context.client_context.custom['subject']
    except Exception as e:
        logging.error('Topic could not be parsed. ' + repr(e))
    return topic

def status_process(event,threshold):
    state = "--"
    try:
        temp_value = float(event['temp'])
        mois_value = int(event['moisture'])
        light_value = int(event['light'])
        status = int(event['switch'])
        if mois_value < threshold:
            if ((light_value > light_threshold) and (temp_value > temp_threshold)):
                if status:
                    state = "off"
                else:
                    state = "on"
            else:
                state = "on-1"
        else:
            if status:
                state = "off"
    except Exception as e:
        logging.error('Sensor message could not be processed. ' + repr(e))
    return state

def switch_handler(event, context):
    mois_threshold = 300
    input_topic = get_input_topic(context)
    logger.info("Received message from %s!" % input_topic)
    if 'setting' in input_topic:
        try:
            mois_threshold = event['threshold']
            file_handler = open(file,"w")
            file_handler.write(str(mois_threshold))
            file_handler.close()
            logger.info("Save the threshold setting <%s>!" % mois_threshold)
        except Exception as e:
            logging.error('Setting failed. ' + repr(e))
    elif 'sensor' in input_topic:
        if os.path.isfile(file):
            try:
                file_handler = open(file)
                mois_threshold = int(file_handler.read())
                file_handler.close()
                logger.info("Get the new threshold: <%d>!" % mois_threshold)
            except Exception as e:
                logging.error('Setting failed. ' + repr(e))

        state = status_process(event,mois_threshold)
        grovepi.pinMode(relay,"OUTPUT")
        if state == "on":
            try:
                grovepi.digitalWrite(relay,1)
                logger.info("Triggering relay turned ON!")
                # build the message to be sent
                message = {"clientId": "relay001",
                            "timestamp": int(datetime.now(timezone.utc).timestamp()*1000),
                            "state": 1 }
                logger.info('Triggering publish to topic ' + control_topic + ' with ' + json.dumps(message))

                client.publish(
                        topic=control_topic,
                        queueFullPolicy='AllOrException',
                        payload=json.dumps(message))
            except Exception as e:
                logger.error("Failed to switch ON relay: " + repr(e))
        elif state == "on-1":
            try:
                grovepi.digitalWrite(relay,1)
                logger.info("Triggering relay turned ON - one time!")
                time.sleep(1)
                grovepi.digitalWrite(relay,0)
                # build the message to be sent
                message = {"clientId": "relay001",
                            "timestamp": int(datetime.now(timezone.utc).timestamp()*1000),
                            "state": 1 }
                logger.info('Triggering publish to topic ' + control_topic + ' with ' + json.dumps(message))

                client.publish(
                        topic=control_topic,
                        queueFullPolicy='AllOrException',
                        payload=json.dumps(message))
            except Exception as e:
                logger.error("Failed to switch ON relay[one time]: " + repr(e))
        elif state == "off":
            try:
                grovepi.digitalWrite(relay,0)
                logger.info("Triggering relay turned OFF!")
            except Exception as e:
                logger.error("Failed to switch OFF relay: " + repr(e))
        else:
            logger.info("No need to change!")
