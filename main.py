# Guild install URL:
# https://discord.com/oauth2/authorize?client_id=1270128415831359621&permissions=2150829568&integration_type=0&scope=bot


import sys
import torch
import os
import random
import discord
import datetime
import re

from typing import Final
from dotenv import load_dotenv
from discord import Intents, Client, Message

# from gtts import gTTS
from TTS.api import TTS

import io
import db

print("Starting SonicBlaster...")
print("Loading environment variables...")
load_dotenv()

# if our database doesn't exist, create it
if not os.path.exists(db.PATH):
    print("CRITICAL ERROR: Database does not exist.")
    if input("Do you want to create it? (y/n): ").lower() != "y":
        print("Exiting...")
        sys.exit(1)
    db.create_db()

# setup our constants
URL_INSTALL: Final[str] = os.getenv("URL_INSTALL")
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
DEVICE: Final[str] = "cuda" if torch.cuda.is_available() else "cpu"
tts: Final[TTS] = TTS(os.getenv("TTS_MODEL")).to(DEVICE)
DEFAULT_VOICE: Final[str] = "deckard-cain.wav"
BOT_ADMINS: Final[list[str]] = os.getenv("BOT_ADMINS").split(":")
# advertise our install URL
print(f"Install URL: {URL_INSTALL}")

# setup our intents
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

# active voice connections
voice_connections = {}
nicknames = db.load_nicknames()
voices = db.load_voices()
voice_queues = {}


# add our message parsing functionality
async def send_message(message: Message, user_message: str) -> None:

    if not user_message:
        print("Message is empty, intents were not enabled")
        return

    # if the message is prefixed with a ? then it is private
    if is_private := user_message[0] == "?":
        print(f"Is private: {is_private}")

        # remove the ? from the message
        user_message = user_message[1:]

    try:
        response: str = process_user_commands(message, user_message)

        if response:

            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)
        else:
            print("No response")

    # general exception handling
    except Exception as e:
        print(f"Error: {e}")
        response = "An error occurred"


@client.event
async def on_ready() -> None:
    print(f"Connected to Discord as {client.user}")


@client.event
async def on_message(message: Message) -> None:
    # don't process our own messages
    if message.author == client.user:
        return

    username: str = message.author.name
    user_message: str = message.content
    channel: str = message.channel.name
    guild_name = message.guild.name
    print(f"[{guild_name}:{channel}] {username}: {user_message}")

    # check if the message is a "!join" command
    if user_message == "!join":
        # join the voice channel of the user
        if message.author.voice:
            # check if the bot is already in a voice channel in this guild
            if message.guild in voice_connections:
                await message.channel.send(
                    "Dropping existing connection...Leaving voice channel..."
                )
                await voice_connections[message.guild].disconnect()
                del voice_connections[message.guild]

            await message.channel.send("Joining voice channel...")
            voice_connections[message.guild] = (
                await message.author.voice.channel.connect()
            )
        else:
            await message.channel.send("You are not in a voice channel")

    # check if the message is a "!leave" command
    elif user_message == "!leave":
        # leave the voice channel
        if message.guild in voice_connections:
            await message.channel.send("Leaving voice channel...")
            await voice_connections[message.guild].disconnect()
            del voice_connections[message.guild]
        else:
            await message.channel.send("I am not in a voice channel")

    if user_message.startswith("!"):

        await send_message(message, user_message)

    else:

        # check if the user message is in a guild we have an active voice connection
        if message.guild in voice_connections:
            # get the voice connection
            voice = voice_connections[message.guild]
            filtered_message = re.sub(r"<.*?>", "", user_message)
            tts_name = username

            if username in voices:
                voice_to_use = f"voices/{voices[username]}"
            else:
                voice_to_use = f"voices/{DEFAULT_VOICE}"

            if username in nicknames:
                tts_name = nicknames[username]
            else:
                print(f"Username not found in nicknames: `{username}`")

            tts_text = f"{tts_name} says {filtered_message}"

            # check if the tts text contains a link
            if "http" in tts_text.lower():
                tts_text = f"{tts_name} sent a link"

            # create a TTS object
            audio_data = io.BytesIO()
            tts.tts_to_file(
                text=tts_text,
                speaker_wav=voice_to_use,
                language="en",
                file_path=audio_data,
            )

            # rewind to the start of the file
            audio_data.seek(0)

            if message.guild not in voice_queues:
                voice_queues[message.guild] = []

            # if already playing, add to the queue
            if voice.is_playing():
                voice_queues[message.guild].append(audio_data)
            else:
                # play the mp3 file from memory
                voice.play(
                    discord.FFmpegPCMAudio(audio_data, pipe=True),
                    after=lambda e: play_queue(message.guild),
                )


def play_queue(guild):
    print(f"Playing queue for {guild}")
    if guild in voice_queues:
        voice = voice_connections[guild]
        if len(voice_queues[guild]) > 0:
            audio_data = voice_queues[guild].pop(0)
            voice.play(
                discord.FFmpegPCMAudio(audio_data, pipe=True),
                after=lambda e: play_queue(guild),
            )


def process_user_commands(message: Message, user_message: str) -> str:
    lowered = user_message.lower()

    response = ""

    if lowered == "!help" or lowered == "!commands":
        response = "Available commands:  !join, !voice, !nick, !dice, !coin, !8ball, !help, !commands, !url, !source"

    elif lowered == "!source":
        response = "The source code for Sonic Blaster is available on GitHub: https://github.com/SiliconSorcerers/SonicBlaster"

    elif lowered == "!url":
        response = f"To install Sonic Blaster in your discord server visit our install URL: {URL_INSTALL}"

    elif lowered == "!dice":
        response = f"Rolling a dice... you got {random.randint(1, 6)}"

    elif lowered == "!coin":
        flip = random.choice(["Heads", "Tails"])
        response = f"Flipping a coin... you got {flip}"

    elif lowered == "!connlist":
        response = f"Active voice connections: {voice_connections}"

    elif lowered.startswith("!voice"):
        parts = user_message.split(" ")

        if len(parts) >= 2:

            # remove the !voice command
            parts.pop(0)

            # join the rest of the parts into a single string
            parts = " ".join(parts)

            username = message.author.name
            voice = parts

            # verify the voice exists in the voices folder
            if not os.path.exists(f"voices/{voice}"):
                response = f"Voice {voice} not found. The following are valid voices: "

                # list each file in the voices directory
                for file in os.listdir("voices"):
                    response += f"{file}, "

                # remove the last comma
                response = response[:-2]

            else:

                voices[username] = voice

                db.register_voice(username, voice)

                response = f"Registered voice: {username} -> {voice}"
        else:
            response = "Invalid syntax. Please use !voice <voice>. The following are valid voices: "

            # list each file in the voices directory
            for file in os.listdir("voices"):
                if not file.lower().endswith(".md"):
                    response += f"{file}, "

            # remove the last comma
            response = response[:-2]

            if message.author.name in voices:
                response += f".\n\nYour current voice is {voices[message.author.name]}."

    elif lowered.startswith("!nick"):
        parts = user_message.split(" ")

        if len(parts) >= 2:

            # remove the !nick command
            parts.pop(0)

            # join the rest of the parts into a single string
            parts = " ".join(parts)

            username = message.author.name
            nickname = parts

            nicknames[username] = nickname
            db.register_nickname(username, nickname)

            response = f"Registered nickname: {username} -> {nickname}"
        else:
            response = "Invalid syntax. Please use !nick <nickname>"

    elif lowered.startswith("!8ball "):
        response = random.choice(
            [
                # yes's
                "Yes",
                "Unequivocally yes",
                "Yes, without the shadow of a doubt",
                "Count on it",
                "Does a bear shit in the woods?",
                # no's
                "No",
                "Not a snowball's chance in hell",
                "Don't hold your breath",
                "When pigs fly",
                "Dream on",
                # neutral
                "The dark side clouds everything. Impossible to see the future is.",
                "Ask again later",
                "The answer is hidden in the tea leaves",
                "The universe is still deciding",
                "The path ahead is unclear",
            ]
        )

    if message.author.name in BOT_ADMINS:
        if lowered == "!quit":
            sys.exit(0)

    return response


def main() -> None:
    print("Running SonicBlaster...")
    client.run(TOKEN)


if __name__ == "__main__":
    main()
