# Sonic Blaster
SonicBlaster is a Text-to-Speech Discord bot. It uses advanced AI
speech synthesis to deliver natural language sounding TTS.


## Windows Dependencies
### 1 PyTorch (Optionally with CUDA)

Reference the Pytorch docs to get the latest pip command:

https://pytorch.org/get-started/locally/

At the time of writing this amounts to:

`pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

You may need the latest C++ build tools installed from Microsoft.

### Coqui TTS

Reference the Coqui TTS documentation. At the time of writing this amounts to:

`pip install coqui-tts`


## Install
### 1. Setting up your .env file
Copy the .env.sample file to .env or establish environment variables as it defines.
BOT_ADMINS is colon delimited.

```
DISCORD_TOKEN=Your-Token-Here
URL_INSTALL=Your-Install-URL-Here
TTS_MODEL=tts_models/multilingual/multi-dataset/xtts_v2
BOT_ADMINS=YOUR:ADMIN:USERNAMES
```
Setup your app and get your tokens and URL on discord.com here:

https://discord.com/developers/applications

### 2. Creating your database
Create a SQLite3 database using the included db.py manager.

```
[user@device] python db.py -h

SonicBlaster DB Manager
usage: db.py [-h] [-c] [-n]

options:
  -h, --help       show this help message and exit
  -c, --create-db  create an empty database
  -n, --nicknames  list nicknames

```
