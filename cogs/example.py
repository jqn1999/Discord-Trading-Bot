import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient

#db_token = open("db_token.txt", "r").read()
#cluster = MongoClient(db_token)

#db = cluster["PotatoTrading"]
#collection = db["UserData"]

class Example(commands.Cog):

    def __init__(self, client):
        self.client = client

#    @commands.command()
#    async def addToDatabase(self, ctx):
#        post = {'_id': ctx.author.id, 'potatoes': 0}
#        collection.insert_one(post)
#        await ctx.channel.send('You have been added to the database')

def setup(client):
    client.add_cog(Example(client))