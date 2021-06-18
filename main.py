import discord
from discord.ext import commands
import os

#client = discord.Client()
client = commands.Bot(command_prefix = '.')
bot_token = open("bot_token.txt", "r").read()

@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Cog has been reloaded.')
        print('Cog has been reloaded.')
    except:
        await ctx.send('Cog has not been loaded.')
        print('Cog has not been loaded.')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f'{filename} has been loaded.')

client.run(bot_token)