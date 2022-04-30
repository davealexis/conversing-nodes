# Conversing Nodes

Use MQTT to orchestrate a conversation between multiple nodes that speak their part using text-to-speech.

This version of the code is universal, in that it works on both PC and Raspberry Pi.
The code detects what platform it is running on, and sets itself up accordingly
by importing the correct libraries for the platform.

Also, you now need to pass two command line arguments when you run the code
- This node's name
- The other node's name

The only requirement for the names now is that they must match the names of
the "speaker" values in conversation.json.

e.g. On one node you might run:
```
    python main.py izzy dave
```

Then on the other node you'll run:
```
    python main.py dave izzy
```

## Setup

Run the following command to make sure that the required libraries are installed:

## Windows

```
py -m pip install paho-mqtt pywin32
```

## Linux / Raspberry Pi
```
python -m pip install paho-mqtt
```


Open main.py in an editor and make sure that the MqttHost variable has the correct
IP address for the Raspberry Pi.

Edit the conversations.json file so it contains the full coversation you want, using the same
format as the included file:

```json
[
    {
        "speaker": "izzy",
        "text": "A long time ago, the world was ruled by 3 forces. Lig ma! Suh gun deez! And Up dog!"
    },
    {
        "speaker": "dave",
        "text": "Oh no! You are not getting me with that nonsense! But... What's Up dog?"
    },
    {
        "speaker": "izzy",
        "text": "Oh, nuffin much. Whats up with you? HAH HAH HAH"
    },
    {
        "speaker": "dave",
        "text": "you bastard"
    }
]
```

Then run the app:

```
py main.py
```

The app connects to MQTT and sends a Hello message to the "node/bust" topic
continuously, until the bust node responds to indicate that it is online.

Then the conversation starts. The conversation progresses from top to bottom,
pauses for 5 seconds, then starts again at the beginning.
