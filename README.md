# Sonic Blaster
## Install
### 1. Setting up your .env file
Copy the .env.sample file to .env or establish environment variables as it defines.

```
DISCORD_TOKEN=Your-Token-Here
URL_INSTALL=Your-Install-URL-Here
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
