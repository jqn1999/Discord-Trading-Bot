import discord
from discord.ext import commands
import time
import math
import requests
import json

class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def register(self, ctx):
        print(ctx.author.id)
        r = requests.get(f'http://localhost:3000/register/{ctx.author.id}')

        if (r.content):
            await ctx.channel.send("You already have an account. Use the stats command!")
        else:
            await ctx.channel.send('You have been added to the users database')
            print(f'{ctx.author} has been added to the users database')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update(self, ctx):
        requests.get(f'http://localhost:3000/updatemany/(ENTER COLLECTION & CHANGE BACKEND)')
        await ctx.channel.send('All users have been updated.')
        print('Users have been updated.')
    
    @commands.command(aliases = ['clearcollections', 'clearall'])
    @commands.has_permissions(administrator=True)
    async def clearCollections(self, ctx):
        requests.get(f'http://localhost:3000/clearall')
        await ctx.channel.send('Collections have been cleared')
        print('Collections have been cleared')
    
    @commands.command()
    async def work(self, ctx):
        r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
        user = json.loads(r.text)

        for result in user:
            workTimer = result["workTimer"]
            potatoes = result["potatoes"]

        try:
            # 23 hours until user can work again
            if (workTimer+82800 < int(time.time())):
                # 10 x 8 x .85
                potatoes += 68
                requests.get(f'http://localhost:3000/workupdate/{ctx.author.id}/{potatoes}/{int(time.time())}')
                
                await ctx.channel.send(f'You work and now have {potatoes} potatoes.')
                print(f'{ctx.author} has worked')
            else:
                remainingTime = workTimer+82800-int(time.time())
                if (remainingTime >= 3600):
                    remainingTime = math.ceil( (workTimer+82800-int(time.time()))/3600)
                    await ctx.channel.send(f'You have {remainingTime} hours until you can work again.')
                elif (remainingTime >= 60):
                    remainingTime = math.ceil( (workTimer+82800-int(time.time()))/60)
                    await ctx.channel.send(f'You have {remainingTime} minutes until you can work again.')
                else:
                    await ctx.channel.send(f'You have {remainingTime} seconds until you can work again.')
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

    @commands.command(aliases = ["stat"])
    async def stats(self, ctx):
        #try:
            r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
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

                totalPL = totalGain - totalLoss
                if numTrades == 0:
                    avgPL = "N/A"
                    avgPLPercent = "N/A"
                    winrate = "N/A"
                else:
                    avgPL = round(totalPL/numTrades, 2)
                    avgPLPercent = round(((totalGain-totalLoss)/totalCost)/numTrades*100, 2)
                    winrate = round(winningTrades/numTrades*100, 2)

            embed = discord.Embed(title='User Information', description=(f"Potatoes: {potatoes}\nTotal Closed Trades: {numTrades}\nOpen Trades: {openTrades}\nAvg P/L: {avgPL}\nAvg P/L %: {avgPLPercent}%\nWinrate: {winrate}%"), color=discord.Color.blue())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text="Potato Hoarders")

            await ctx.channel.send(embed=embed)
        #except:
            #await ctx.channel.send("Format incorrect or you have not registered.")

def setup(client):
    client.add_cog(Misc(client))