# Potato-Bot
This is a Discord bot in development that will allow users to simulate stock and options trades in real-time through Discord commands as well as various fun ways to generate the money to do so.
# Getting Started
First, you will need to setup a Discord bot through the Discord Developer Portal.
Next, you will need to setup a Discord server where you can invite your bot.
Then, you will need to create a mongo database, which can be done at mongodb.com.
Finally, you can just pull this repository.

Next, you will need to run:
```
pip install discord.py
pip install requests

npm init --yes
npm install express
npm install cors
npm install dotenv
```

Now, make a folder named 'tokens' and place your bot_token.txt and td_token.txt inside along with the respective tokens needed.

Finally, you can run:
```
python main.py
```
and your bot should be up and running!
