import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import time
import math

db_token = open("db_token.txt", "r").read()
cluster = MongoClient(db_token)

PotatoTrading = cluster["PotatoTrading"]

UserData = PotatoTrading["UserData"]
UserTrades = PotatoTrading["UserTrades"]

class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def register(self, ctx):
        query = { '_id': ctx.author.id}
        if (UserData.count_documents(query) == 0):
            post = {'_id': ctx.author.id, 'potatoes': 1000, 'workTimer': int(time.time())}
            UserData.insert_one(post)

            post = {'_id': ctx.author.id}
            UserTrades.insert_one(post)

            await ctx.channel.send('You have been added to the database')
            print(f'{ctx.author} has been added to the database')
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
        UserData.update_many({}, {'$set': {'potatoes': 1000 }})
        await ctx.channel.send('All users have been updated.')
        print('Users have been updated.')
    
    @commands.command()
    async def work(self, ctx):
        query = { '_id': ctx.author.id}
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
            



def setup(client):
    client.add_cog(Misc(client))