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
# Usage
1. Check stock and options data
![image](https://user-images.githubusercontent.com/46391291/125893998-9ff2a1cf-ed5f-496e-b668-eeac83ba574b.png)
2. Buy stocks and options
![image](https://user-images.githubusercontent.com/46391291/125894006-04fc4d0b-ba31-4476-a652-7d2009286102.png)
3. Sell stocks and options (P/L would change and not be 0% as this was just an example)
![image](https://user-images.githubusercontent.com/46391291/125894011-9419fbbe-e984-4bba-baa4-417df6c9e55e.png)
4. Check on your open and closed positions
![image](https://user-images.githubusercontent.com/46391291/125888696-11174178-3f3d-4edd-838f-585a94d79e64.png)

There are many more commands, but these are the primary commands for trading.

