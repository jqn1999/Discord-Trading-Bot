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

            embed = discord.Embed(title='Stock Price', description=(f"Ticker: {stock}\nPrice: {mark}"), color=discord.Color.blue())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text="Potato Hoarders")

            await ctx.channel.send(embed=embed)
            print(f"{ctx.author} requested {stock} information")
        except:
            await ctx.channel.send("That stock ticker does not exist!")

    @commands.command()
    async def getOption(self, ctx, stock, option, date):
        #try:
            stock = stock.upper()
            strike = option[:-1]
            optionType = option[-1]
            month,day,year = date.split('/')

            if optionType.lower() == 'c':
                optionType = 'CALL'
            elif optionType.lower() == 'p':
                optionType = 'PUT'
            else:
                await ctx.channel.send("Format incorrect, please recheck.")
                return

            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={td_token}&symbol={stock}&contractType={optionType}&includeQuotes=FALSE&strike={strike}&fromDate=20{year}-{month}-{day}&toDate=20{year}-{month}-{day}", headers = headers)
            strike = "{:.1f}".format(float(strike))
            key = list(userRequest.json()[f"{optionType.lower()}ExpDateMap"].keys())[0]

            mark = userRequest.json()[f"{optionType.lower()}ExpDateMap"][key][strike][0]["mark"]
            mark = "{:.2f}".format(mark)

            embed = discord.Embed(title='Option Details', description=(f"Ticker: {stock}\nStrike: {strike}\nExpiration: {date}\nPrice: {mark}"),color=discord.Color.blue())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text="Potato Hoarders")

            await ctx.channel.send(embed=embed)
            #await ctx.channel.send(f"The current price of {stock} {strike} {optionType} {month}/{day}/{year} is ${mark}.")
            print(f"{ctx.author} requested {stock} option information")
        #except:
            #await ctx.channel.send("Format incorrect, please recheck.")

def setup(client):
    client.add_cog(Trading(client))