# Raspberry Pi Node

## Setup

Run the following command to make sure that the required libraries are installed:

```
python -m pip install -r requirements.txt
```

Open main.py in an editor and make sure that the MqttHost variable has the correct
IP address for the Raspberry Pi.

Edit the conversations.json file so it contains the full coversation you want, using the same
format as the included file:

```json
[
    {
        "speaker": "bust",
        "text": "A long time ago, the world was ruled by 3 forces. Lig ma! Suh gun deez! And Up dog!"
    },
    {
        "speaker": "pc",
        "text": "Oh no! You are not getting me with that nonsense! But... What's Up dog?"
    },
    {
        "speaker": "bust",
        "text": "Oh, nuffin much. Whats up with you? HAH HAH HAH"
    },
    {
        "speaker": "pc",
        "text": "you bastard"
    }
]
```

Then run the app:

```
python main.py
```

The app connects to MQTT and sends a Hello message to the "node/pc" topic
continuously, until the bust node responds to indicate that it is online.

Then the conversation starts. The conversation progresses from top to bottom,
pauses for 5 seconds, then starts again at the beginning.
