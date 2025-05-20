> [!IMPORTANT]  
> This repo is still under active development and doesnt have a stable release yet.

# LM + Discord
A simple discord bot for the LM Studio REST API.

## Features
- Channel based memory
- Long term user based memory
- Web search functionality
- Built in commands to interact with the LLMs
- Very customizable

## Setup
1. Create a new [discord bot](https://discord.com/developers/applications) and add it to a server or as a user app
2. Clone or download the repo
3. Go to the src folder and create a .env file with a `BOT_TOKEN` variable
4. Copy your bot token and add it to the `BOT_TOKEN` value
5. Download LM Studio and install a model of your choice (recrommend below or equal to 7B)
6. Navigate to and start the LM Studio server/rest api

### If using Docker:
1. Build the image using the provided Docker file
2. Run the image

### If not using Docker:
1. Navigate to the project root folder
2. Run this script to download dependencies: `pip install dotenv discord.py asyncio requests`
3. Then navigate to the src file and start the bot `cd src; python3 __main__.py`

## Using the bot:
By default replies to @'s but can be configured to respond to other things.

### Commands:
`/model`: Lists all downloaded models and provides a dropdown to switch out current running model

...and more to come
