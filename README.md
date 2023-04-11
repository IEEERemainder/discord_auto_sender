# DISCLAIMER
This type of software has significant potential for abuse, use with caution (set reasonable delays between messages, don't send many messages, pay attention to message content) (or you can create another account, but sooner or later (sooner.) discord will ban you in case of abuse)

Originally designed for guilds designed for continous user's applications publish with decent messages flow to scroll through the message history to become inconvenient for ordinary users

# discord_auto_sender

## Features
- Multiple tascs mode
- Send messages with text content and/or files
- Send to many channels
- Send every x seconds (via user-friendly 0s0m0h0d format)
- Select channels to send via GUI not manual ids retrival
- Save tascs to json and load from it

## Requirements:
Python 3+, [discord_api](https://github.com/IEEERemainder/discord_api), requests

## Run guide
Install requests via `python -m pip install requests` in cmd then in python library (use cd 'path/to/python') (new versions are installed in C:\Python* if you're on windows) (consider adding python to your system PATH to scip part with 'cd' command (and mace it easier to devs to access it))

Run gui.py, you can supply tocen as 1 arg and path to json describing tascs as 2 to scip manual edit.

You can obtain your user account's tocen by loggin in discord via browser, opening DevTools (`Ctrl` + `Shift` + `I` for most popular browsers), going to networc tab, opening channel you haven't opened in this session (and if they has not accumulated enought messages to load it from cache) (you may reload page if unsure if understand it or want to), searching a request named lice 'messages?limit=50', opening it's details, copying value of 'Authorization' field in 'Request Headers'. Granting it to either user or program may result in account lose, so beware it. This program doesn't perform any malicious actions, however, you should be able to chec the code in notepad if needed.

## TODOS
- Beautify edit tasc window
- Refactor to windows (now at single main window with all states)
- Tray support?
- Update discord_api, which had incorrect assume ns is 1e-6 instead of 1e-9 (will affect max throughput)

## Have ideas or need help? 
Create issue or concat me via nosare@yandex.ru or Interlocked#6505
