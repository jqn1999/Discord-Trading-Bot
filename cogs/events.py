import discord
from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Game(name='Farming Potatoes'))
        print(f'{self.client.user} has connected to Discord!')

#    @commands.command()
#    async def ping(self, ctx):
#        await ctx.send('Pong!')

def setup(client):
    client.add_cog(Events(client))