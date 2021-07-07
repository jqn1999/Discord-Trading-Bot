import discord
from discord.ext import commands
from pymongo import MongoClient
import requests
import json

client = discord.Client()

class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

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
    
    # Can delete messages in bulk
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=1):
        # Has the + 1 to also remove the command message, plus amount
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} messages have been removed.")
        print(f"Purge has removed {amount} messages.")

    @commands.command(aliases = ['adminaddpotatoes'])
    @commands.has_permissions(administrator=True)
    async def adminAddPotatoes(self, ctx, member: discord.Member, potatoes):
        potatoes = int(potatoes)
        r = requests.get(f'http://localhost:3000/find/UserData/{member.id}')
        recipient = json.loads(r.text)

        if (recipient != []):
            for result in recipient:
                recipientPotatoes = result["potatoes"]
        else:
            await ctx.channel.send('Recipient needs to register')
            return
        newRecipientPotatoes = recipientPotatoes + potatoes
        requests.get(f'http://localhost:3000/updatepotatoes/{member.id}/{newRecipientPotatoes}')
        
        await ctx.channel.send(f"You have given {potatoes} potatoes to {member.display_name}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def startPoll(self, ctx):
        print('x')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def closePoll(self, ctx):
        print('x')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def finishPoll(self, ctx):
        print('x')

def setup(client):
    client.add_cog(Admin(client))