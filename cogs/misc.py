import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import time
import math

db_token = open("./tokens/db_token.txt", "r").read()
cluster = MongoClient(db_token)

PotatoTrading = cluster["PotatoTrading"]

UserData = PotatoTrading["UserData"]
UserTrades = PotatoTrading["UserTrades"]

class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def register(self, ctx):
        query = {'_id': ctx.author.id}
        if (UserData.count_documents(query) == 0):
            post = {'_id': ctx.author.id, 'potatoes': 1000.00, 'workTimer': int(time.time()), 'coinTimer': int(time.time()), 'numTrades': 0, 'openTrades': 0,'winningTrades': 0, 'losingTrades': 0, 'totalGain': 0.0, 'totalLoss': 0.0 }
            UserData.insert_one(post)

            post = {'_id': ctx.author.id, 'openStocks': [], 'closedStocks': [], 'openOptions': [], 'closedOptions': []}
            UserTrades.insert_one(post)

            await ctx.channel.send('You have been added to the users database')
            print(f'{ctx.author} has been added to the users database')
        else:
            #user = UserData.find(query)
            #for result in user:
                #potatoes = result["potatoes"]
            #potatoes += 1
            #UserData.update_one({'_id': ctx.author.id}, {'$set': {'potatoes': potatoes} })
            await ctx.channel.send('You are already registered.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update(self, ctx):
        #UserData.update_many({}, {'$set': {'guild': 'None' }})
        await ctx.channel.send('All users have been updated.')
        print('Users have been updated.')
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearCollections(self, ctx):
        UserData.remove({})
        UserTrades.remove({})
        await ctx.channel.send('Collections have been cleared')
        print('Collections have been cleared')
    
    @commands.command()
    async def work(self, ctx):
        query = {'_id': ctx.author.id}
        user = UserData.find(query)
        for result in user:
            workTimer = result["workTimer"]
            potatoes = result["potatoes"]

        # 23 hours until user can work again
        if (workTimer+82800 < int(time.time())):
            # 10 x 8 x .85
            potatoes += 68
            UserData.update_one({'_id': ctx.author.id}, {'$set': {'potatoes': potatoes} })
            UserData.update_one({'_id': ctx.author.id}, {'$set': {'workTimer': int(time.time())} })
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
            
    @commands.command(aliases = ["stat"])
    async def stats(self, ctx):
        try:
            query = {'_id': ctx.author.id}
            user = UserData.find(query)
            for result in user:
                potatoes = result["potatoes"]
                numTrades = result["numTrades"]
                openTrades = result["openTrades"]
                totalPL = result["totalGain"] - result["totalLoss"]
                if numTrades == 0:
                    avgPL = "N/A"
                else:
                    avgPL = round(totalPL/numTrades, 2)

            embed = discord.Embed(title='User Information', description=(f"Potatoes: {potatoes}\nTotal Trades: {numTrades}\nOpen Trades: {openTrades}\nTotal P/L: {totalPL}\nAvg P/L: {avgPL}"), color=discord.Color.blue())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text="Potato Hoarders")

            await ctx.channel.send(embed=embed)
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

def setup(client):
    client.add_cog(Misc(client))