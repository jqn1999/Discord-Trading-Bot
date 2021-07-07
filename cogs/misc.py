import discord
from discord.ext import commands
import time
import math
import requests
import json
import random

class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def register(self, ctx):
        r = requests.get(f'http://localhost:3000/register/{ctx.author.id}/{ctx.author.display_name}')

        if (r.content):
            await ctx.channel.send("You already have an account. Use the stats command!")
        else:
            await ctx.channel.send('You have been added to the users database')
            print(f'{ctx.author} has been added to the users database')

    @commands.command()
    async def work(self, ctx):
        r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
        user = json.loads(r.text)

        for result in user:
            potatoes = result["potatoes"]
            workTimer = result["workTimer"]

        try:
            # 23 hours until user can work again
            if (workTimer+3600 < int(time.time())):
                # 10 x 8 x .85
                workGain = random.randint(500*.8, 500*1.2)
                potatoes += workGain
                requests.get(f'http://localhost:3000/workupdate/{ctx.author.id}/{potatoes}/{int(time.time())}')
                
                await ctx.channel.send(f'You work and gain {workGain} potatoes. You now have {potatoes} potatoes.')
                print(f'{ctx.author} has worked')
            else:
                remainingTime = workTimer+3600-int(time.time())
                if (remainingTime >= 3600):
                    remainingTime = math.ceil( (workTimer+3600-int(time.time()))/3600)
                    await ctx.channel.send(f'You have {remainingTime} hours until you can work again.')
                elif (remainingTime >= 60):
                    remainingTime = math.ceil( (workTimer+3600-int(time.time()))/60)
                    await ctx.channel.send(f'You have {remainingTime} minutes until you can work again.')
                else:
                    await ctx.channel.send(f'You have {remainingTime} seconds until you can work again.')
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

    @commands.command(aliases = ["stat"])
    async def stats(self, ctx, member: discord.Member = None):
        try:
            if member is None:
                r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
            else:
                r = requests.get(f'http://localhost:3000/find/UserData/{member.id}')

            user = json.loads(r.text)
            for result in user:
                potatoes = result["potatoes"]
                numTrades = result["numTrades"]
                openTrades = result["openTrades"]
                totalGain = result["totalGain"]
                totalLoss = result["totalLoss"]
                totalCost = result["totalCost"]
                winningTrades = result["winningTrades"]
                losingTrades = result["losingTrades"]
                rank = result["rank"]

                totalPL = totalGain - totalLoss
                if numTrades == 0:
                    avgPL = "N/A"
                    avgPLPercent = "N/A"
                    winrate = "N/A"
                else:
                    avgPL = round(totalPL/numTrades, 2)
                    avgPLPercent = round(((totalGain-totalLoss)/totalCost)*100, 2)
                    winrate = round(winningTrades/numTrades*100, 2)

            embed = discord.Embed(title=f'User Information\nRank: {rank}', description=(f"Potatoes: {potatoes}\nTotal Closed Trades: {numTrades}\nOpen Trades: {openTrades}\nAvg P/L: {avgPL}\nAvg P/L %: {avgPLPercent}%"), color=discord.Color.blue())
            if member is None:
                embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=ctx.author.avatar_url)
            else:
                embed.set_author(name=member.display_name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=member.avatar_url)
                embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text="Potato Hoarders")

            await ctx.channel.send(embed=embed)
        except:
            await ctx.channel.send("Format incorrect or someone has not registered.")

    # Returns a search of players on op.gg
    @commands.command()
    async def opgg(self, ctx, playerOne=None, playerTwo=None, playerThree=None, playerFour=None, playerFive=None):
        totalPlayers = [playerOne, playerTwo, playerThree, playerFour, playerFive]
        newTotalPlayers = []
        for player in totalPlayers:
            if player == None:
                pass
            else:
                player = ''.join(player.split()).lower()
                newTotalPlayers.append(player)
        multiplier = 1
        totalLink = ""
        for i in newTotalPlayers:
            if i == None:
                pass
            else:
                if multiplier == 1:
                    totalLink += i
                    multiplier -= 1
                else:
                    totalLink += "%2C" + i
        await ctx.send("https://na.op.gg/multi/query=" + totalLink)
        print("OP.GG request has been sent.")

    @commands.command()
    async def potatoes(self, ctx, member: discord.Member = None):
        if member is None:
            r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
        else:
            r = requests.get(f'http://localhost:3000/find/UserData/{member.id}')

        user = json.loads(r.text)
        if (user != []):
            for result in user:
                potatoes = result["potatoes"]
        else:
            await ctx.channel.send('You need to register before you can hunt')
            return

        if member is None:
            await ctx.channel.send(f"You currently have {potatoes} potatoes")
        else:
            await ctx.channel.send(f"{member.display_name} currently has {potatoes} potatoes")

def setup(client):
    client.add_cog(Misc(client))