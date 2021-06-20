import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import asyncio

client = discord.Client()
db_token = open("db_token.txt", "r").read()
cluster = MongoClient(db_token)

db = cluster["PotatoTrading"]
UserData = db["UserData"]
UserTrades = db["UserTrades"]

class Test(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def test(self, ctx):
        try:
            optionData = UserTrades.find({"_id": ctx.author.id}, {"openOptions": {'$elemMatch': {"ticker": "AAPL_132.0_PUT_06/25/2021"}}})
            for result in optionData:
                ticker = result["openOptions"][0]["ticker"]
                price = result["openOptions"][0]["price"]
                quantity = result["openOptions"][0]["quantity"]

            await ctx.channel.send(f"{ticker} / {price} / {quantity}")
        except:
            await ctx.channel.send(f"You do not own this position.")

def setup(client):
    client.add_cog(Test(client))