import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import requests
import json

td_token = open("td_token.txt", "r").read()
db_token = open("db_token.txt", "r").read()
cluster = MongoClient(db_token)

db = cluster["PotatoTrading"]
collection = db["UserData"]

headers = {'Authorization': ''}

class Trading(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def getStock(self, ctx, stock):
        try:
            stock = stock.upper()
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/quotes?apikey={td_token}&symbol={stock}", headers = headers)
            mark = userRequest.json()[stock]["mark"]
            mark = "{:.2f}".format(mark)
            await ctx.channel.send(f"The current price of {stock} is ${mark}.")
            print(f"{ctx.author} requested {stock} information")
        except:
            await ctx.channel.send("That stock ticker does not exist!")

def setup(client):
    client.add_cog(Trading(client))