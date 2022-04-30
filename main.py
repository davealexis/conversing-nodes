import sys
import paho.mqtt.client as mqtt
import json
from time import sleep
import platform

MyPlatform = platform.system()

if MyPlatform == 'Windows':
    import win32com.client

if MyPlatform == 'Linux':
    import subprocess


# Set the MQTT server to connect to.
'''
    Set to the IP address of your Pi that has mosquitto running.
    If mosquitto is running on your own computer, you can use "localhost".

    Free public cloud MQTT brokers:
    - broker.emqx.io
    - mqtt.eclipse.org
    - test.mosquitto.org
    - broker.hivemq.com
    - broker.mqttdashboard.com
    - mqtt.fluux.io

    Private cloud MQTT brokers:
    - AWS IoT: https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html
    - Azure IoT: https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-mqtt-support
    - Google Cloud IoT: https://cloud.google.com/iot/docs/mqtt

    **For the private cloud, you'll need to create an account with the cloud provider, 
      then set up the MQTT broker.
'''
MqttHost = 'localhost'
MqttPort = 1883

# These variables will get set later (see bottom of this file)
Me = ''
MyTopic = ''
OtherNodeTopic = ''


# -----------------------------------------------------------------------------
class SpeakingNode():

    # -------------------------------------------------------------------------
    def __init__(self):
        """
        Initialize our SpeakingNode class.
        - Read the conversation file into memory
        - Connect to the MQTT broker and wait for the other node to come online.
        - Determine if we're the first to speak, and if so, start the conversation.
        """

        print(f"Starting {Me}. Plaform: {MyPlatform}")
        print("Reading conversation file...")

        with open('./conversation.json') as json_file:
            self.conversation = json.load(json_file)

        self.conversation_length = len(self.conversation)

        if MyPlatform == 'Windows':
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")

        print(f"Connecting to MQTT at {MqttHost}...")

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MqttHost, MqttPort)

    # -------------------------------------------------------------------------
    def start(self):
        self.is_partner_online = False

        print(f"Waiting for {OtherNodeTopic} to come online...")

        def isConnected():
            if self.mqtt_client.is_connected():
                return True
            
            yield False

        while not isConnected():
            ...

        while not self.is_partner_online:
            print(".", end="", flush=True)
            self.mqtt_client.publish(OtherNodeTopic, payload="::hello::")
            self.mqtt_client.loop(timeout=5.0)
            sleep(2)

        print()
        print("Let's go!")

        # If we got here, it means that the other node came online and we're
        # ready to rock!
        # Are we the 1st speaker?
        if self.conversation[0]['speaker'] == Me:
            self.speak(0)

        # This tells the MQTT client to start listening for messages.
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
        print(f"Subscribing to {MyTopic}")
        client.subscribe(MyTopic)

        # Send "are you there" message continuously to the other node
        # until we get a response. Then the conversation can start.

    # -------------------------------------------------------------------------
    def on_message(self, client, userdata, msg):
        """
        We're only subscribing to out topic, so we don't need to see
        which topic the message is from. We'll just look at the message payload,
        which will be a number indicating where the other node was in the
        conversation.
        """

        payload = msg.payload.decode()

        if payload == "::hello::":
            if not self.is_partner_online:
                print()
                print("Partner is online!")

            payload = None
            self.is_partner_online = True

            # Say hi back to the other node. This will ensure that they know we're
            # online also.
            self.mqtt_client.publish(OtherNodeTopic, payload="::hello::")

        # Ignore the hello message as well as empty/invalid messages
        if not payload or payload == '\x00' or len(payload.strip()) == 0 or payload == '::hello::':
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
        print(f"Saying: {text}")
        
        if MyPlatform == 'Windows':
            self.speaker.Speak(text)
        else:
            subprocess.call(
                [f'espeak -v en-us+f3 -k 20 -s 150 -a 100 -g 5 "{text}" 2>/dev/null'], shell=True)

        self.mqtt_client.publish(OtherNodeTopic, payload=conversation_index)


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Our name - "pc" or "bust" - is passed as an argument to the script.
    if len(sys.argv) < 3:
        print('Usage: python main.py <my node name> <other node name> [<mqtt host>]')
        print('     Example: python main.py izzy dave')
        print('     Example: python main.py izzy dave test.mosquitto.org')
        sys.exit(1)

    Me = sys.argv[1].lower()
    other = sys.argv[2].lower()
    MyTopic = f"mcartface/nodes/{Me}"
    OtherNodeTopic = f"mcartface/nodes/{other}"

    # Did we also get a specific MQTT server to connect to?
    if len(sys.argv) > 3:   
        MqttHost = sys.argv[3]

    speaker = SpeakingNode()
    speaker.start()
