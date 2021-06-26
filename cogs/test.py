import discord
from discord.ext import commands
from pymongo import MongoClient
import asyncio

client = discord.Client()

class Test(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def test(self, ctx):
        print('hi')

def setup(client):
    client.add_cog(Test(client))