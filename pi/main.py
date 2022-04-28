#!/bin/env python

import paho.mqtt.client as mqtt
import subprocess
import json
from time import sleep

# -----------------------------------------------------------------------------
MqttHost = '192.168.4.2'
Me = 'bust'

class SpeakingNode():

    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Initialize our SpeakingNode class.
        - Read the conversation file into memory
        - Connect to the MQTT broker and wait for the other node to come online.
        - Determine if we're the first to speak, and if so, start the conversation.
        """

        print("Reading conversation file...")

        with open('./conversation.json') as json_file:
            self.conversation = json.load(json_file)

        self.conversation_length = len(self.conversation)

        print("Connecting to MQTT...")

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MqttHost)

    # -------------------------------------------------------------------------
    def start(self):
        self.is_partner_online = False

        print("Waiting for PC to come online...")

        while not self.is_partner_online:
            self.mqtt_client.publish('nodes/pc', payload="::hello::")
            self.mqtt_client.loop(timeout=5.0)
            sleep(2)

        # If we got here, it means that the other node came online and we're
        # ready to rock!
        # Are we the 1st speaker?
        if self.conversation[0]['speaker'] == Me:
            self.speak(0)

        self.mqtt_client.loop_forever()

    # -------------------------------------------------------------------------
    def on_connect(self, client, userdata, flags, result_code):
        """
        This function gets executed when we are successfully connected to the
        MQTT server.
        Once we get connected, we can subscribe to the topics we're interested in.
        """

        print("Connected to MQTT")

        # Subscribe to whatever topics we're interested in
        client.subscribe("nodes/bust")

        # Send "are you there" message continuously to the bust node
        # until we get a response. Then the conversation can start.

    # -------------------------------------------------------------------------
    def on_message(self, client, userdata, msg):
        """
        We're only subscribing to the "nodes/pc" topic, so we don't need to see
        which topic the message is from. We'll just look at the message payload,
        which will be a number indicating where the other node was in the
        conversation.
        """

        payload = msg.payload.decode()

        if payload == "::hello::":
            if not self.is_partner_online:
                print("Partner is online!  Let's go!")
                self.is_partner_online = True
                subprocess.call([ 'espeak -v en+f5 -k 20 -s 150 -a 100 -g 5 "Hello!" 2>/dev/null'], shell=True)

            return

        # Get the current conversation index from the message,
        # Add 1 to it, and look up our reply in the conversation list.
        conversation_index = int(payload) + 1

        if conversation_index >= self.conversation_length:
            # Got to the end of the conversation. Wait a bit, then start over
            # from the beginning.
            sleep(5)
            conversation_index = 0

        self.speak(conversation_index)

    # -------------------------------------------------------------------------
    def speak(self, conversation_index):
        my_part = self.conversation[conversation_index]
        text = my_part['text'].replace("'", "''")
        subprocess.call([ f'espeak -v en+f5 -k 20 -s 150 -a 100 -g 5 "{text}" 2>/dev/null'], shell=True)
        self.mqtt_client.publish("nodes/pc", payload=conversation_index)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    speaker = SpeakingNode()
    speaker.start()
