# LM + Discord

A simple Discord bot for the LM Studio REST API.

![Example Discord Bot (Bob)](/assets/bob.png)

## Features

- Streamed Replies
- Long term user based memory using `sentence-transformers`
- Web search functionality **(WIP)**
- Built in commands to interact with the LLMs
- Basic voicechat abilites
- Very customizable

## Setup

1. Create a new [Discord bot](https://discord.com/developers/applications)
2. Copy your bot token and keep it somewhere safe in the meantime
3. Clone or download the repo
4. Go to the src folder and create a .env file like seen below (you can also directly modify the docker file if using docker):

```py
BOT_TOKEN= #Your Bot Token Here
LM_STUDIO_URL= #http://host.docker.internal:1234 (default if running in docker)
DEFAULT_MODEL= #gemma-3-12b-it (defaults to first model found if none)
VOICE_TRIGGER_WORDS= #for voice chat, a list of words separated by commas (ex. hey bob,ok bob,hello bob)
```

5. Download LM Studio (headless or headed) and install a model of your choice
6. Start the LM Studio server

### If using Docker:

1. Build the image using the provided Docker file
2. Run the image

### If not using Docker:

1. Navigate to the project root folder
2. Recommended but optional: Create a virtual environment `python -m venv venv` for the deps, then activate it `\\venv\Scripts\Activate.ps1` (for Windows)
3. Run this script to download dependencies: `pip install -r requirements.txt`
4. Then start the bot `python src/__main__.py`

## Using the bot:

By default replies to @'s (both pings and replys) but can be configured to respond to other things.

### Commands:

`/model`: Lists all downloaded models and provides a dropdown to switch out current running model

![Model Command](/assets/model.png)

`/prompt`: Manually prompts the bot without context (mostly for use in direct messages, group chats, etc)

![Prompt Command](/assets/prompt.png)

...and more to come

## Todo

- [ ] Finish voice chat implimentation
- [ ] Create permissions
- [ ] More out of the box customizability (option to disable long term memory)
- [ ] Add a lighter weight long term memory option
- [ ] Finish web search tool (maybe)
- [ ] Add music player tool (maybe)

## Additional Notes

For models that support reasoning/thinking the thought process is truncated from the output (for now, i plan to address this in the future).

Depending on your use case sentence-transformers might be a little heavy, or you simply dont need the memory. In this case simply comment out the calls to the memory module in events.py (lines 35-37 and 49).

Voice chat is still very much a WIP but does infact work!

By default when using voice abilites comes with one tts model, you can find more at https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md

By default the bot CAN respond to other bots, I did this mostly because I thought it would be funny. I dont see a point in disabling it as most other bots already have done so on their end, so it probably shouldnt result in an infinite loop :)