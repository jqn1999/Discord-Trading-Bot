import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import asyncio

client = discord.Client()
db_token = open("./tokens/db_token.txt", "r").read()
cluster = MongoClient(db_token)

db = cluster["PotatoTrading"]
UserData = db["UserData"]
UserTrades = db["UserTrades"]

class Test(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def test(self, ctx):
        print('hi')

def setup(client):
    client.add_cog(Test(client))