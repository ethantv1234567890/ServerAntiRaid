# ServerAntiRaid
 
**Server Anti-Raid, developed by ACPlayGames! Small moderation bot made for fun.**

**NOTE: This is not recommended for beginners. Please learn the basics of Python before attempting to use this code!**

This is a basic moderation bot that you can add on to to suit your own needs. Feel free to contribute anything you want here. The best way to prevent raids is to enable *two-factor authentication* on your account and guild, adding a stricter verification level, enabling explicit content filter, and to give out administrative permissions with caution.

![AntiRaid Icon created by me!](AntiRaid.png)

A tutorial and explanation regarding how to use the bot is on my [YouTube](https://www.youtube.com/channel/UCDSHlAERINyHPbAkINm7OjQ)!

Join the official [Discord](https://discord.com/invite/ka35JqY) server!

---

## Installation
To get started, a few things must be installed.

1. Download [Python](https://www.python.org/downloads/). **Please make sure to check the "*Add Python to PATH*" option!**

2. We will be installing [discord.py](https://pypi.org/project/discord.py/) for this project. Open *Command Prompt* on your computer and type in `pip install discord`.

3. Clone the GitHub repository (either using the web URL, GitHub Desktop, or downloading the zipped file).

## Creating and Inviting the Bot

1. To create a bot, go to the [Discord Developer Portal](https://discord.com/developers/applications) and press `New Application`.

2. Name your application whatever you want, then hit `Create`. You can also set an optional description here.

3. On the left side, press the `Bot` tab, then press `Add Bot`, then `Yes, do it!`. This will transform your application into a bot.

4. Scroll down, and under `Privileged Gateway Intents`, check the `Server Members Intents` option.

5. Once your bot has appeared, copy your bot token by pressing `Copy`. You will use this later. This is how your program will login to your bot. **It is very important to keep this token safe, as it is your bot account credentials!**

6. Now, go to the left side and go to the `OAuth2` tab. Under the `Scopes` options, check `bot`. A section titled `Bot Permissions` will appear below. You will select your bot permissions here. We will using the `Administrator` permission, so please check that option. Now, under Scopes, you will see a link which you can invite your bot with. Copy this link and open it to invite your bot.

---

With those steps done, you are almost ready to go! However, please note that in `main.py`, the second to last line is shown below.

> bot.run('TOKEN HERE')

Please replace the `TOKEN HERE` text with your bot token from earlier, as shown below.

> bot.run('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')