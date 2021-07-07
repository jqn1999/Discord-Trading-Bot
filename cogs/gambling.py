import discord
from discord.ext import commands
from pymongo import MongoClient
import requests
import time
import json
import random

client = discord.Client()

class Gambling(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['cf', 'CF', 'Cf', 'cF'])
    async def coinflip(self, ctx, bet, guess=None):
        r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
        user = json.loads(r.text)

        if (user != []):
            for result in user:
                potatoes = result["potatoes"]
                coinTimer = result["coinTimer"]
        else:
            await ctx.channel.send('You need to register before you can gamble')
            return

        if potatoes <= 0:
            await ctx.channel.send(f"You do not have enough potatoes to bet")
            return
        elif bet == "all":
            bet = int(potatoes)
        elif bet == "half":
            bet = int(potatoes/2)
        elif (potatoes < int(bet)):
            await ctx.channel.send(f"You only have {potatoes} potatoes to bet")
            return

        if int(bet) <= 0:
            await ctx.channel.send(f"Invalid bet")
            return

        if guess is None:
            guess  = "heads"
        elif (guess.lower() == 'heads' or guess.lower() == 'h'):
            guess = 'heads'
        elif (guess.lower() == 'tails' or guess.lower() == 't'):
            guess = 'tails'
        else:
            await ctx.channel.send(f'Cannot read guess')
            return

        if (int(time.time()) > coinTimer+5):
            r = requests.get(f'http://localhost:3000/find/UserData/103243257240121344')
            user = json.loads(r.text)

            if (user != []):
                for result in user:
                    housePotatoes = result["potatoes"]
            else:
                await ctx.channel.send("shouldn't send, if it did something broke")

            # 0 == heads; 1 == tails
            coin = random.randint(0, 1)
            if coin == 0:
                coinResult = 'heads'
            elif coin == 1:
                coinResult = 'tails'

            betPrize = round(int(bet)*.9)
            if (coin == 0 and guess == "heads") or (coin == 1 and guess == "tails"):
                newPotatoes = round(potatoes + betPrize, 2)
                newHousePotatoes = round(housePotatoes-betPrize, 2)
                await ctx.channel.send(f"Congratulations! The coin landed on {coinResult} and you won {betPrize}. You now have {newPotatoes}")
            else:

                newPotatoes = round(potatoes - round(int(bet)), 2)
                newHousePotatoes = round(housePotatoes + round(int(bet)), 2)
                await ctx.channel.send(f"Unfortunately! The coin landed on {coinResult} and you lost {bet}. You now have {newPotatoes}")
            requests.get(f'http://localhost:3000/flipupdate/{ctx.author.id}/{newPotatoes}/{int(time.time())}')
            if int(ctx.author.id) != 103243257240121344:
                requests.get(f'http://localhost:3000/updatepotatoes/103243257240121344/{newHousePotatoes}')
            print(f'{ctx.author} has flipped')
        else:
            remainingTime = coinTimer+5 - int(time.time())
            await ctx.channel.send(f"You must wait {remainingTime} more seconds")


def setup(client):
    client.add_cog(Gambling(client))