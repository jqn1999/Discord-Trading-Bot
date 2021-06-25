import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import requests
import json
import asyncio
import datetime

# Gathers the needed tokens
td_token = open("./tokens/td_token.txt", "r").read()
db_token = open("./tokens/db_token.txt", "r").read()

# Connects to the mongodb and sets variables up
cluster = MongoClient(db_token)
db = cluster["PotatoTrading"]
UserData = db["UserData"]
UserTrades = db["UserTrades"]

headers = {'Authorization': ''}

class Trading(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Allows users to get stock information
    @commands.command(aliases=['getstock', 'stock', 'Stock'])
    async def getStock(self, ctx, stock):
        try:
            # Grabs stock info using TDA API, returns as embed
            stock = stock.upper()
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/quotes?apikey={td_token}&symbol={stock}", headers = headers)
            mark = userRequest.json()[stock]["mark"]
            mark = "{:.2f}".format(mark)

            embed = discord.Embed(title='Stock Price', description=(f"Ticker: {stock}\nPrice: {mark}"), color=discord.Color.blue())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")

            await ctx.channel.send(embed=embed)
            print(f"{ctx.author} requested {stock} information")
        except:
            await ctx.channel.send("That stock ticker does not exist!")

    @commands.command(aliases = ["buystock", "bs"])
    async def buyStock(self, ctx, stock, quantity=None):
        try:
            r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
            user = json.loads(r.text)

            if (user != []):
                for result in user:
                    potatoes = result["potatoes"]
            else:
                await ctx.channel.send('You need to register before you can trade')
                return

            if quantity == None:
                quantity = 1.0
            else:
                quantity = float(quantity)

            # Grabs stock info using TDA API, returns as embed
            stock = stock.upper()
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/quotes?apikey={td_token}&symbol={stock}", headers = headers)
            mark = userRequest.json()[stock]["mark"]
            mark = "{:.2f}".format(mark)
            totalCost = float(mark)*quantity
            totalCost = round(totalCost, 2)

            embed = discord.Embed(title=(f'Buy Stock\nTotal Cost: {totalCost}'), description=(f"Ticker: {stock}\nPrice: {mark}\nQuantity: {quantity}"), color=discord.Color.green())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")

            # Checks if user has enough money
            if potatoes < totalCost:
                embed.add_field(name=(f"You do not have enough\nto purchase this stock."),value=(f"You have: {potatoes} potatoes"),inline=False)
                message = await ctx.channel.send(embed=embed)
                return

            embed.add_field(name="Confirm or reject\nyour order by reacting\nwith a ✅ or a ❌\nin the next 10 seconds.",value='\u200b',inline=False)
            message = await ctx.channel.send(embed=embed)
            await message.add_reaction('✅')
            await message.add_reaction('❌')

            def check(reaction, user):
                return reaction.message == message and str(reaction) in ['✅','❌'] and user == ctx.author
            
            # Checks if user accepts or rejects the given price
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout = 10.0, check=check)

                if str(reaction) == '✅':
                    remainingPotatoes = round(potatoes-totalCost, 2)
                    UserData.update_one({'_id': ctx.author.id}, {'$set': {'potatoes': remainingPotatoes} })

                    # Add a check later on for if the stock is already opened
                    UserTrades.update_one({'_id': ctx.author.id}, {'$push': {'openStocks': {'ticker': (f"{stock}"), "quantity": quantity, "totalCost": totalCost}} })

                    embed.set_field_at(0, name="Order Confirmed", value=(f'You have: {remainingPotatoes} potatoes'),inline=False)
                    print(f"{ctx.author} has bought {stock} stocks")
                elif str(reaction) == '❌':
                    embed.set_field_at(0, name="Order Rejected", value='\u200b',inline=False)
            except asyncio.TimeoutError:
                embed.set_field_at(0, name="Order Timed Out", value='\u200b',inline=False)

            await message.clear_reactions()
            await message.edit(embed=embed)
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

    # Used to get information on a given option contract
    @commands.command(aliases=['getoption', 'option', 'Option'])
    async def getOption(self, ctx, stock, option, date):
        try:
            # Formats given variables
            stock = stock.upper()
            strike = option[:-1]
            optionType = option[-1]
            month,day,year = date.split('/')
            if len(month) == 1:
                month = "0" + month
            if len(year) == 2:
                year = "20" + year

            if optionType.lower() == 'c':
                optionType = 'CALL'
            elif optionType.lower() == 'p':
                optionType = 'PUT'
            else:
                await ctx.channel.send("Format incorrect, please recheck.")
                return

            # Uses TDA API to get info on given option
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={td_token}&symbol={stock}&contractType={optionType}&includeQuotes=FALSE&strike={strike}&fromDate=20{year}-{month}-{day}&toDate=20{year}-{month}-{day}", headers = headers)
            strike = "{:.1f}".format(float(strike))
            key = list(userRequest.json()[f"{optionType.lower()}ExpDateMap"].keys())[0]

            mark = userRequest.json()[f"{optionType.lower()}ExpDateMap"][key][strike][0]["mark"]
            mark = "{:.2f}".format(mark)

            embed = discord.Embed(title='Option Details', description=(f"Ticker: {stock} {optionType}\nStrike: {strike}\nExpiration: {month}/{day}/{year}\nPrice: {mark}"),color=discord.Color.blue())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")

            await ctx.channel.send(embed=embed)
            print(f"{ctx.author} requested {stock} option information")
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

    @commands.command(aliases = ["buyoption", "BTO", "bto", "bo"])
    async def buyOption(self, ctx, stock, option, date, quantity=None):
        #try:
            # Formats given variables
            stock = stock.upper()
            strike = option[:-1]
            optionType = option[-1]
            month,day,year = date.split('/')
            if quantity == None:
                quantity = 1.0
            else:
                quantity = float(quantity)
            if len(month) == 1:
                month = "0" + month
            if len(year) == 2:
                year = "20" + year

            if optionType.lower() == 'c':
                optionType = 'CALL'
            elif optionType.lower() == 'p':
                optionType = 'PUT'
            else:
                await ctx.channel.send("Format incorrect or you have not registered.")
                return

            # Uses TDA API to get info on given option
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={td_token}&symbol={stock}&contractType={optionType}&includeQuotes=FALSE&strike={strike}&fromDate={year}-{month}-{day}&toDate=20{year}-{month}-{day}", headers = headers)
            strike = "{:.1f}".format(float(strike))
            key = list(userRequest.json()[f"{optionType.lower()}ExpDateMap"].keys())[0]

            mark = userRequest.json()[f"{optionType.lower()}ExpDateMap"][key][strike][0]["mark"]
            mark = "{:.2f}".format(mark)
            totalCost = float(mark)*quantity*100
            totalCost = round(totalCost, 2)

            # Queries database for user info
            query = {'_id': ctx.author.id}
            if (UserData.count_documents(query) == 0):
                await ctx.channel.send('You need to register before you can trade')
                return
            else:
                user = UserData.find(query)
                for result in user:
                    potatoes = result["potatoes"]
                    openTrades = result["openTrades"]

            # Returns option information to user
            await ctx.message.delete()
            embed = discord.Embed(title=(f"BTO\nTotal Cost: {totalCost}"), description=(f"Ticker: {stock} {optionType}\nStrike: {strike}\nExpiration: {month}/{day}/{year}\nPrice: {mark}\nQuantity: {quantity}"),color=discord.Color.green())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")

            # Checks if user has enough money
            if potatoes < totalCost:
                embed.add_field(name=(f"You do not have enough\nto purchase this contract."),value=(f"You have: {potatoes} potatoes"),inline=False)
                message = await ctx.channel.send(embed=embed)
                return

            embed.add_field(name="Confirm or reject\nyour order by reacting\nwith a ✅ or a ❌\nin the next 10 seconds.",value='\u200b',inline=False)
            message = await ctx.channel.send(embed=embed)
            await message.add_reaction('✅')
            await message.add_reaction('❌')

            def check(reaction, user):
                return reaction.message == message and str(reaction) in ['✅','❌'] and user == ctx.author

            # Checks if user accepts or rejects the given price
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout = 10.0, check=check)

                if str(reaction) == '✅':
                    remainingPotatoes = round(potatoes-totalCost, 2)
                    openTrades += 1
                    UserData.update_one({'_id': ctx.author.id}, {'$set': {'potatoes': remainingPotatoes}, '$set': {'openTrades': openTrades}})

                    # Add a check later on for if the option is already opened
                    UserTrades.update_one({'_id': ctx.author.id}, {'$push': {'openOptions': {'ticker': (f"{stock}_{strike}_{optionType}_{month}/{day}/{year}"), "quantity": quantity, "totalCost": totalCost}} })

                    embed.set_field_at(0, name="Order Confirmed", value=(f'You have: {remainingPotatoes} potatoes'),inline=False)
                    print(f"{ctx.author} has bought an options contract")
                elif str(reaction) == '❌':
                    embed.set_field_at(0, name="Order Rejected", value='\u200b',inline=False)

            except asyncio.TimeoutError:
                embed.set_field_at(0, name="Order Timed Out", value='\u200b',inline=False)

            await message.clear_reactions()
            await message.edit(embed=embed)
        #except:
            #await ctx.channel.send("Format incorrect or you have not registered.")
    
    @commands.command(aliases = ['openoptions'])
    async def openOptions(self, ctx):
        optionData = UserTrades.find({"_id": ctx.author.id})
        string = ''
        for result in optionData:
            for i in range(len(result["openOptions"])):
                stock, strike, optionType, date = result["openOptions"][i]["ticker"].split('_')
                quantity = result["openOptions"][i]["quantity"]
                totalCost = result["openOptions"][i]["totalCost"]
                price = round(totalCost/quantity, 2)
                string = string + (f"Ticker: {stock}, Strike: {strike} {optionType}, Exp: {date}, Cost Per: {price}, Quantity: {quantity}, Total Cost: {totalCost}\n")
        await ctx.channel.send(string)

    @commands.command(aliases = ['openoption'])
    async def openOption(self, ctx, stock, option, date):
        # Formats given variables
        stock = stock.upper()
        strike = option[:-1]
        strike = round(float(strike), 1)
        optionType = option[-1]
        month,day,year = date.split('/')
        if len(month) == 1:
            month = "0" + month
        if len(year) == 2:
            year = "20" + year

        if optionType.lower() == 'c':
            optionType = 'CALL'
        elif optionType.lower() == 'p':
            optionType = 'PUT'
        else:
            await ctx.channel.send("Format incorrect or you have not registered.")
            return

        try:
            # Find specific position
            optionData = UserTrades.find({"_id": ctx.author.id}, {"openOptions": {'$elemMatch': {"ticker": f"{stock}_{strike}_{optionType}_{month}/{day}/{year}"}}})
            for result in optionData:
                quantity = result["openOptions"][0]["quantity"]
                totalCost = result["openOptions"][0]["totalCost"]
                price = round(totalCost/quantity, 2)

            embed = discord.Embed(title=(f"Open Option Info\nTotal Cost: {totalCost}"), description=(f"Ticker: {stock} {optionType}\nStrike: {strike}\nExpiration: {month}/{day}/{year}\nPrice: {price}\nQuantity: {quantity}"),color=discord.Color.blue())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")
            await ctx.channel.send(embed=embed)
        except:
            await ctx.channel.send(f"You do not own this position.")

    #@commands.command(aliases = ['closedoptions'])
    #async def closedOptions(self, ctx):
        #optionData = UserTrades.find({"_id": ctx.author.id})
        #string = ''
        #for result in optionData:
            #for i in range(len(result["closedOptions"])):
                #stock, strike, optionType, date = result["closedOptions"][i]["ticker"].split('_')
                #quantity = result["closedOptions"][i]["quantity"]
                #totalCost = result["closedOptions"][i]["totalCost"]
                #price = round(totalCost/quantity,2)

                #string = string + (f"Ticker: {stock}, Strike: {strike} {optionType}, Exp: {date}, Cost: {price}, Quantity: {quantity}\n")
        #await ctx.channel.send(string)

def setup(client):
    client.add_cog(Trading(client))