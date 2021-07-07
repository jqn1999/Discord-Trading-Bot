import discord
from discord.ext import commands
import requests
import json
import asyncio
import datetime

# Gathers the needed token
td_token = open("./tokens/td_token.txt", "r").read()

headers = {'Authorization': ''}

class Trading(commands.Cog):

    def __init__(self, client):
        self.client = client

    ### Provides stock and options information
    @commands.command(aliases=['getstock', 'stock', 'Stock'])
    async def getStock(self, ctx, stock):
        try:
            # Grabs stock info using TDA API, returns as embed
            stock = stock.upper()
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/quotes?apikey={td_token}&symbol={stock}", headers = headers)
            netChange = userRequest.json()[stock]["regularMarketNetChange"]
            netChange = "{:.2f}".format(netChange)
            mark = userRequest.json()[stock]["mark"]
            mark = "{:.2f}".format(mark)
            netChangePercent = round(float(netChange) / (float(mark) - float(netChange) )*100, 2)

            embed = discord.Embed(title='Stock Price', description=(f"Ticker: {stock}\nPrice: {mark}\nDaily Change: {netChange}\n Daily Change %: {netChangePercent}%"), color=discord.Color.blue())
            embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")

            await ctx.channel.send(embed=embed)
            print(f"{ctx.author} requested {stock} information")
        except:
            await ctx.channel.send("That stock ticker does not exist!")

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
            if len(day) == 1:
                day = "0" + day
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
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={td_token}&symbol={stock}&contractType={optionType}&includeQuotes=FALSE&strike={strike}&fromDate={year}-{month}-{day}&toDate={year}-{month}-{day}", headers = headers)
            strike = "{:.1f}".format(float(strike))
            key = list(userRequest.json()[f"{optionType.lower()}ExpDateMap"].keys())[0]

            netChange = userRequest.json()[f"{optionType.lower()}ExpDateMap"][key][strike][0]["markChange"]
            netChange = "{:.2f}".format(netChange)
            mark = userRequest.json()[f"{optionType.lower()}ExpDateMap"][key][strike][0]["mark"]
            mark = "{:.2f}".format(mark)
            netChangePercent = round(float(netChange) / (float(mark) + abs(float(netChange)) )*100, 2)

            embed = discord.Embed(title='Option Details', description=(f"Ticker: {stock} {optionType}\nStrike: {strike}\nExpiration: {month}/{day}/{year}\nPrice: {mark}\nDaily Change: {netChange}\nDaily Change %: {netChangePercent}"),color=discord.Color.blue())
            embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")

            await ctx.channel.send(embed=embed)
            print(f"{ctx.author} requested {stock} option information")
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

    ### Allows users to buy (and eventually sell) stock and options positions
    @commands.command(aliases = ["buystock", "bs"])
    async def buyStock(self, ctx, stock, quantity=None):
        try:
            r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
            user = json.loads(r.text)

            if (user != []):
                for result in user:
                    potatoes = result["potatoes"]
                    openTrades = result["openTrades"]
            else:
                await ctx.channel.send('You need to register before you can trade')
                return

            if quantity == None:
                quantity = 1.0
            elif (int(quantity) <= 0):
                await ctx.channel.send("Enter a valid quantity")
                return
            else:
                quantity = float(quantity)

            # Grabs stock info using TDA API, returns as embed
            stock = stock.upper()
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/quotes?apikey={td_token}&symbol={stock}", headers = headers)
            mark = userRequest.json()[stock]["mark"]
            mark = "{:.2f}".format(mark)
            totalCost = float(mark)*quantity
            totalCost = round(totalCost, 2)

            # Returns stock information to user
            #await ctx.message.delete()
            embed = discord.Embed(title=(f'Buy Stock\nTotal Cost: {totalCost}'), description=(f"Ticker: {stock}\nPrice: {mark}\nQuantity: {quantity}"), color=discord.Color.green())
            embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
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
                    requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{remainingPotatoes}')

                    # Add a check later on for if the option is already opened
                    # Check if there is already an existing options position
                    r = requests.get(f'http://localhost:3000/findstockopen/{ctx.author.id}/{stock}')
                    user = json.loads(r.text)

                    for result in user:
                        try:
                            if (result["openStocks"][0]["ticker"] == stock):
                                # Existing position, get info and add onto it
                                newQuantity = result["openStocks"][0]["quantity"] + quantity
                                newTotalCost = result["openStocks"][0]["totalCost"] + totalCost
                                newTotalCost = round(newTotalCost, 2)
                                requests.get(f'http://localhost:3000/removestockopen/{ctx.author.id}/{stock}')
                                requests.get(f'http://localhost:3000/openstockopen/{ctx.author.id}/{stock}/{newQuantity}/{newTotalCost}')
                        except:
                            # Not an existing position
                            openTrades += 1
                            requests.get(f'http://localhost:3000/updateopentrades/{ctx.author.id}/{openTrades}')
                            requests.get(f'http://localhost:3000/openstockopen/{ctx.author.id}/{stock}/{quantity}/{totalCost}')

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

    @commands.command(aliases = ["sellstock", "ss"])
    async def sellStock(self, ctx, stock, quantity=None):
        try:
            r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
            user = json.loads(r.text)

            if (user != []):
                for result in user:
                    potatoes = result["potatoes"]
                    openTrades = result["openTrades"]
                    numTrades = result["numTrades"]
                    winningTrades = result["winningTrades"]
                    losingTrades = result["losingTrades"]
                    userTotalCost = result["totalCost"]
                    totalGain = result["totalGain"]
                    totalLoss = result["totalLoss"]
            else:
                await ctx.channel.send('You need to register before you can trade')
                return

            stock = stock.upper()
            if quantity == None:
                quantity = 1.0
            elif (int(quantity) <= 0):
                await ctx.channel.send("Enter a valid quantity")
                return
            else:
                quantity = float(quantity)

            # Grabs stock info of user
            r = requests.get(f'http://localhost:3000/findstockopen/{ctx.author.id}/{stock}')
            user = json.loads(r.text)

            fullPositionClose = False
            for result in user:
                try:
                    if (result["openStocks"][0]["ticker"] == stock):
                        # Existing position, get info and add onto it
                        prevOpenQuantity = result["openStocks"][0]["quantity"]
                        prevOpenTotalCost = result["openStocks"][0]["totalCost"]
                        prevOpenTotalCost = round(prevOpenTotalCost, 2)

                        newOpenQuantity = prevOpenQuantity - quantity
                        costPer = round(prevOpenTotalCost/prevOpenQuantity, 2)
                    if (prevOpenQuantity == quantity):
                        fullPositionClose = True
                    if (prevOpenQuantity < quantity):
                        # Cannot sell more than you  own
                        await ctx.channel.send(f'You cannot sell more than you currently own. You have {prevOpenQuantity}!')
                        return
                except:
                    # Nonexisting position
                    await ctx.channel.send('You do not have any of this stock to close')
                    return


            # Grabs stock info using TDA API, returns as embed
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/quotes?apikey={td_token}&symbol={stock}", headers = headers)
            mark = userRequest.json()[stock]["mark"]
            mark = "{:.2f}".format(mark)
            totalCredit = float(mark)*quantity
            totalCredit = round(totalCredit, 2)
            totalCost = costPer*quantity
            profitLoss = round(totalCredit - totalCost, 2)
            profitLossPercent = round(profitLoss/totalCost*100.0)

            embed = discord.Embed(title=(f'Sell Stock\nTotal Credit: {totalCredit}\nP/L: {profitLoss}'), description=(f"Ticker: {stock}\nOpen Price: {costPer}\nClosing Price: {mark}\nQuantity: {quantity}\nP/L: {profitLossPercent}%"), color=discord.Color.red())
            embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")
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
                    if (profitLoss > 0):
                        totalGain += round(totalCredit - totalCost, 2)
                        requests.get(f'http://localhost:3000/updatetotalgain/{ctx.author.id}/{totalGain}')
                    elif (profitLoss < 0):
                        totalLoss -= round(totalCredit - totalCost, 2)
                        requests.get(f'http://localhost:3000/updatetotalloss/{ctx.author.id}/{totalLoss}')

                    userPotatoes = round(potatoes+totalCredit, 2)
                    userTotalCost += round(totalCost, 2)
                    requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{userPotatoes}')
                    requests.get(f'http://localhost:3000/updatetotalcost/{ctx.author.id}/{userTotalCost}')

                    r = requests.get(f'http://localhost:3000/findstockclosed/{ctx.author.id}/{stock}')
                    user = json.loads(r.text)

                    closedArrayExist = False
                    for result in user:
                        try:
                            if (result["closedStocks"][0]["ticker"] == stock):
                                # Existing position, get info and add onto it
                                prevClosedQuantity = result["closedStocks"][0]["quantity"]
                                prevClosedTotalCost = result["closedStocks"][0]["totalCost"]
                                prevClosedTotalCost = round(prevClosedTotalCost, 2)
                                prevClosedTotalCredit = result["closedStocks"][0]["totalCredit"]

                                newClosedQuantity = quantity + prevClosedQuantity
                                newClosedTotalCost = round(totalCost + prevClosedTotalCost, 2)
                                newClosedTotalCredit = round(totalCredit + prevClosedTotalCredit, 2)
                                closedArrayExist = True
                        except:
                            # Nonexisting position
                            newClosedQuantity = quantity
                            newClosedTotalCost = round(totalCost, 2)
                            newClosedTotalCredit = round(totalCredit, 2)
                            pass

                    # Add a check later on for if the option is already opened
                    # Check if there is already an existing options position
                    if (fullPositionClose):
                        print('fullstockclose')
                        if (newClosedTotalCredit-newClosedTotalCost > 0):
                            winningTrades += 1
                            requests.get(f'http://localhost:3000/updatewinningtrades/{ctx.author.id}/{winningTrades}')
                        elif (newClosedTotalCredit-newClosedTotalCost < 0):
                            losingTrades += 1
                            requests.get(f'http://localhost:3000/updatelosingtrades/{ctx.author.id}/{losingTrades}')

                        openTrades -= 1
                        numTrades += 1
                        requests.get(f'http://localhost:3000/updateopentrades/{ctx.author.id}/{openTrades}')
                        requests.get(f'http://localhost:3000/updatenumtrades/{ctx.author.id}/{numTrades}')

                        print('removed stock open')
                        requests.get(f'http://localhost:3000/removestockopen/{ctx.author.id}/{stock}')
                        if (closedArrayExist):
                            print('closed exists, removing open')
                            requests.get(f'http://localhost:3000/removestockclosed/{ctx.author.id}/{stock}')
                        print(f'http://localhost:3000/openstockclosed/{ctx.author.id}/{stock}/{newClosedQuantity}/{newClosedTotalCost}/{newClosedTotalCredit}')
                        print('opening closed with new vars')
                        requests.get(f'http://localhost:3000/openstockclosed/{ctx.author.id}/{stock}/{newClosedQuantity}/{newClosedTotalCost}/{newClosedTotalCredit}')
                    else:  
                        print('not full close')
                        requests.get(f'http://localhost:3000/removestockopen/{ctx.author.id}/{stock}')
                        newOpenTotalCost = round(prevOpenTotalCost - totalCost, 2)
                        requests.get(f'http://localhost:3000/openstockopen/{ctx.author.id}/{stock}/{newOpenQuantity}/{newOpenTotalCost}')
                        if (closedArrayExist):
                            print('closed exists in not full close, removing')
                            requests.get(f'http://localhost:3000/removestockclosed/{ctx.author.id}/{stock}')
                        print('added new close with new vars')
                        requests.get(f'http://localhost:3000/openstockclosed/{ctx.author.id}/{stock}/{newClosedQuantity}/{newClosedTotalCost}/{newClosedTotalCredit}')

                    embed.set_field_at(0, name="Order Confirmed", value=(f'You have: {userPotatoes} potatoes'),inline=False)
                    print(f"{ctx.author} has sold {stock} stocks")
                elif str(reaction) == '❌':
                    embed.set_field_at(0, name="Order Rejected", value='\u200b',inline=False)
            except asyncio.TimeoutError:
                embed.set_field_at(0, name="Order Timed Out", value='\u200b',inline=False)

            await message.clear_reactions()
            await message.edit(embed=embed)
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

    @commands.command(aliases = ["buyoption", "BTO", "bto", "bo"])
    async def buyOption(self, ctx, stock, option, date, quantity=None):
        try:
            # Queries database for user info
            r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
            user = json.loads(r.text)

            if (user != []):
                for result in user:
                    potatoes = result["potatoes"]
                    openTrades = result["openTrades"]
            else:
                await ctx.channel.send('You need to register before you can trade')
                return

            # Formats given variables
            stock = stock.upper()
            strike = option[:-1]
            optionType = option[-1]
            month,day,year = date.split('/')

            if quantity == None:
                quantity = 1.0
            elif (int(quantity) <= 0):
                await ctx.channel.send("Enter a valid quantity")
                return
            else:
                quantity = float(quantity)

            if len(month) == 1:
                month = "0" + month
            if len(day) == 1:
                day = "0" + day
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
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={td_token}&symbol={stock}&contractType={optionType}&includeQuotes=FALSE&strike={strike}&fromDate={year}-{month}-{day}&toDate={year}-{month}-{day}", headers = headers)
            strike = "{:.1f}".format(float(strike))
            key = list(userRequest.json()[f"{optionType.lower()}ExpDateMap"].keys())[0]

            mark = userRequest.json()[f"{optionType.lower()}ExpDateMap"][key][strike][0]["mark"]
            mark = "{:.2f}".format(mark)
            totalCost = float(mark)*quantity*100
            totalCost = round(totalCost, 2)

            # Returns option information to user
            #await ctx.message.delete()
            embed = discord.Embed(title=(f"BTO\nTotal Cost: {totalCost}"), description=(f"Ticker: {stock} {optionType}\nStrike: {strike}\nExpiration: {month}/{day}/{year}\nPrice: {mark}\nQuantity: {quantity}"),color=discord.Color.green())
            embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
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
                    requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{remainingPotatoes}')

                    # Add a check later on for if the option is already opened
                    # Check if there is already an existing options position
                    r = requests.get(f'http://localhost:3000/findoptionopen/{ctx.author.id}/{stock}_{strike}_{optionType}_/{month}/{day}/{year}')
                    user = json.loads(r.text)

                    tickerMatch = f"{stock}_{strike}_{optionType}_{month}/{day}/{year}"
                    fullTicker = f"{stock}_{strike}_{optionType}_/{month}/{day}/{year}"
                    for result in user:
                        try:
                            if (result["openOptions"][0]['ticker'] == tickerMatch):
                                newQuantity = result["openOptions"][0]["quantity"] + quantity
                                newTotalCost = result["openOptions"][0]["totalCost"] + totalCost
                                newTotalCost = round(newTotalCost, 2)

                                requests.get(f'http://localhost:3000/removeoptionopen/{ctx.author.id}/{fullTicker}')
                                requests.get(f'http://localhost:3000/openoptionopen/{ctx.author.id}/{fullTicker}/{newQuantity}/{newTotalCost}')
                        except:
                            # Not an existing position
                            openTrades += 1
                            requests.get(f'http://localhost:3000/updateopentrades/{ctx.author.id}/{openTrades}')
                            requests.get(f'http://localhost:3000/openoptionopen/{ctx.author.id}/{fullTicker}/{quantity}/{totalCost}')
                    
                    
                    embed.set_field_at(0, name="Order Confirmed", value=(f'You have: {remainingPotatoes} potatoes'),inline=False)
                    print(f"{ctx.author} has bought an options contract")
                elif str(reaction) == '❌':
                    embed.set_field_at(0, name="Order Rejected", value='\u200b',inline=False)

            except asyncio.TimeoutError:
                embed.set_field_at(0, name="Order Timed Out", value='\u200b',inline=False)

            await message.clear_reactions()
            await message.edit(embed=embed)
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")
    
    @commands.command(aliases = ["selloption", "STC", "stc", "so"])
    async def sellOption(self, ctx, stock, option, date, quantity=None):
        try:
            # Queries database for user info
            r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
            user = json.loads(r.text)

            if (user != []):
                for result in user:
                    potatoes = result["potatoes"]
                    openTrades = result["openTrades"]
                    numTrades = result["numTrades"]
                    winningTrades = result["winningTrades"]
                    losingTrades = result["losingTrades"]
                    userTotalCost = result["totalCost"]
                    totalGain = result["totalGain"]
                    totalLoss = result["totalLoss"]
            else:
                await ctx.channel.send('You need to register before you can trade')
                return

            # Formats given variables
            stock = stock.upper()
            strike = option[:-1]
            optionType = option[-1]
            month,day,year = date.split('/')

            if quantity == None:
                quantity = 1.0
            elif (int(quantity) <= 0):
                await ctx.channel.send("Enter a valid quantity")
                return
            else:
                quantity = float(quantity)

            if len(month) == 1:
                month = "0" + month
            if len(day) == 1:
                day = "0" + day
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
            userRequest = requests.get(f"https://api.tdameritrade.com/v1/marketdata/chains?apikey={td_token}&symbol={stock}&contractType={optionType}&includeQuotes=FALSE&strike={strike}&fromDate={year}-{month}-{day}&toDate={year}-{month}-{day}", headers = headers)
            strike = "{:.1f}".format(float(strike))

            tickerMatch = f"{stock}_{strike}_{optionType}_{month}/{day}/{year}"
            fullTicker = f"{stock}_{strike}_{optionType}_/{month}/{day}/{year}"
            # Grabs option info of user
            r = requests.get(f'http://localhost:3000/findoptionopen/{ctx.author.id}/{fullTicker}')
            user = json.loads(r.text)

            fullPositionClose = False
            for result in user:
                try:
                    key = list(userRequest.json()[f"{optionType.lower()}ExpDateMap"].keys())[0]
                except:
                    # Option is expired
                    if (result["openOptions"][0]['ticker'] == tickerMatch):
                        prevOpenQuantity = result["openOptions"][0]["quantity"]
                        prevOpenTotalCost = result["openOptions"][0]["totalCost"]
                        prevOpenTotalCost = round(prevOpenTotalCost, 2)
                        costPer = round((prevOpenTotalCost/prevOpenQuantity)/100, 2)

                        totalCredit = 0
                        totalCredit = round(totalCredit, 2)
                        totalCost = costPer*quantity*100
                        totalCost = round(totalCost, 2)
                        profitLoss = round(totalCredit - totalCost, 2)

                        losingTrades += 1
                        totalLoss -= round(totalCredit - totalCost, 2)
                        requests.get(f'http://localhost:3000/updatelosingtrades/{ctx.author.id}/{losingTrades}')
                        requests.get(f'http://localhost:3000/updatetotalloss/{ctx.author.id}/{totalLoss}')

                        userPotatoes = round(potatoes+totalCredit, 2)
                        userTotalCost += totalCost
                        openTrades -= 1
                        numTrades += 1

                        requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{userPotatoes}')
                        requests.get(f'http://localhost:3000/updatetotalcost/{ctx.author.id}/{userTotalCost}')
                        requests.get(f'http://localhost:3000/updateopentrades/{ctx.author.id}/{openTrades}')
                        requests.get(f'http://localhost:3000/updatenumtrades/{ctx.author.id}/{numTrades}')

                        r = requests.get(f'http://localhost:3000/findoptionclosed/{ctx.author.id}/{fullTicker}')
                        user = json.loads(r.text)

                        closedArrayExist = False
                        for result in user:
                            try:
                                if (result["closedOptions"][0]['ticker'] == tickerMatch):
                                    # Existing position, get info and add onto it
                                    prevClosedQuantity = result["closedOptions"][0]["quantity"]
                                    prevClosedTotalCost = result["closedOptions"][0]["totalCost"]
                                    prevClosedTotalCost = round(prevClosedTotalCost, 2)
                                    prevClosedTotalCredit = result["closedOptions"][0]["totalCredit"]

                                    newClosedQuantity = quantity + prevClosedQuantity
                                    newClosedTotalCost = round(totalCost + prevClosedTotalCost, 2)
                                    newClosedTotalCredit = round(totalCredit + prevClosedTotalCredit, 2)
                                    closedArrayExist = True
                            except:
                                # Nonexisting position
                                newClosedQuantity = quantity
                                newClosedTotalCost = round(totalCost, 2)
                                newClosedTotalCredit = round(totalCredit, 2)
                                pass

                        requests.get(f'http://localhost:3000/removeoptionopen/{ctx.author.id}/{fullTicker}')
                        if (closedArrayExist):
                            requests.get(f'http://localhost:3000/removeoptionclosed/{ctx.author.id}/{fullTicker}')
                        requests.get(f'http://localhost:3000/openoptionclosed/{ctx.author.id}/{fullTicker}/{newClosedQuantity}/{newClosedTotalCost}/{newClosedTotalCredit}')
                        await ctx.channel.send("Position has expired, option has been closed for 0 credit.")
                        return
                    else:
                        # Nonexisting position
                        await ctx.channel.send('You do not have any of this option to close')
                        return

                try:
                    if (result["openOptions"][0]['ticker'] == tickerMatch):
                        # Existing position, get info and add onto it
                        prevOpenQuantity = result["openOptions"][0]["quantity"]
                        prevOpenTotalCost = result["openOptions"][0]["totalCost"]
                        prevOpenTotalCost = round(prevOpenTotalCost, 2)

                        newOpenQuantity = prevOpenQuantity - quantity
                        costPer = round((prevOpenTotalCost/prevOpenQuantity)/100, 2)
                    if (prevOpenQuantity == quantity):
                        fullPositionClose = True
                    if (prevOpenQuantity < quantity):
                        # Cannot sell more than you  own
                        await ctx.channel.send(f'You cannot sell more than you currently own. You have {prevOpenQuantity}!')
                        return
                except:
                    # Nonexisting position
                    await ctx.channel.send('You do not have any of this option to close')
                    return

            mark = userRequest.json()[f"{optionType.lower()}ExpDateMap"][key][strike][0]["mark"]
            mark = "{:.2f}".format(mark)
            totalCredit = float(mark)*quantity*100
            totalCredit = round(totalCredit, 2)
            totalCost = costPer*quantity*100
            totalCost = round(totalCost, 2)
            profitLoss = round(totalCredit - totalCost, 2)
            profitLossPercent = round(profitLoss/totalCost*100.0)

            # Returns option information to user
            #await ctx.message.delete()
            embed = discord.Embed(title=(f"STC\nTotal Credit: {totalCredit}\nP/L: {profitLoss}"), description=(f"Ticker: {stock} {optionType}\nStrike: {strike}\nExpiration: {month}/{day}/{year}\nOpen Price: {costPer}\nClosing Price: {mark}\nQuantity: {quantity}\nP/L: {profitLossPercent}%"),color=discord.Color.red())
            embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")
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
                    if (profitLoss > 0):
                        totalGain += round(totalCredit - totalCost, 2)
                        requests.get(f'http://localhost:3000/updatetotalgain/{ctx.author.id}/{totalGain}')
                    elif (profitLoss < 0):
                        totalLoss -= round(totalCredit - totalCost, 2)
                        requests.get(f'http://localhost:3000/updatetotalloss/{ctx.author.id}/{totalLoss}')

                    userPotatoes = round(potatoes+totalCredit, 2)
                    userTotalCost += totalCost
                    requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{userPotatoes}')
                    requests.get(f'http://localhost:3000/updatetotalcost/{ctx.author.id}/{userTotalCost}')

                    r = requests.get(f'http://localhost:3000/findoptionclosed/{ctx.author.id}/{fullTicker}')
                    user = json.loads(r.text)

                    closedArrayExist = False
                    for result in user:
                        try:
                            if (result["closedOptions"][0]['ticker'] == tickerMatch):
                                # Existing position, get info and add onto it
                                prevClosedQuantity = result["closedOptions"][0]["quantity"]
                                prevClosedTotalCost = result["closedOptions"][0]["totalCost"]
                                prevClosedTotalCost = round(prevClosedTotalCost, 2)
                                prevClosedTotalCredit = result["closedOptions"][0]["totalCredit"]

                                newClosedQuantity = quantity + prevClosedQuantity
                                newClosedTotalCost = round(totalCost + prevClosedTotalCost, 2)
                                newClosedTotalCredit = round(totalCredit + prevClosedTotalCredit, 2)
                                closedArrayExist = True
                        except:
                            # Nonexisting position
                            newClosedQuantity = quantity
                            newClosedTotalCost = round(totalCost, 2)
                            newClosedTotalCredit = round(totalCredit, 2)
                            pass

                    # Add a check later on for if the option is already opened
                    # Check if there is already an existing options position
                    if (fullPositionClose):
                        print('full close')
                        if (newClosedTotalCredit-newClosedTotalCost > 0):
                            winningTrades += 1
                            requests.get(f'http://localhost:3000/updatewinningtrades/{ctx.author.id}/{winningTrades}')
                        elif (newClosedTotalCredit-newClosedTotalCost < 0):
                            losingTrades += 1
                            requests.get(f'http://localhost:3000/updatelosingtrades/{ctx.author.id}/{losingTrades}')

                        openTrades -= 1
                        numTrades += 1
                        requests.get(f'http://localhost:3000/updateopentrades/{ctx.author.id}/{openTrades}')
                        requests.get(f'http://localhost:3000/updatenumtrades/{ctx.author.id}/{numTrades}')

                        requests.get(f'http://localhost:3000/removeoptionopen/{ctx.author.id}/{fullTicker}')
                        if (closedArrayExist):
                            requests.get(f'http://localhost:3000/removeoptionclosed/{ctx.author.id}/{fullTicker}')
                        requests.get(f'http://localhost:3000/openoptionclosed/{ctx.author.id}/{fullTicker}/{newClosedQuantity}/{newClosedTotalCost}/{newClosedTotalCredit}')
                    else:  
                        print('not full close')
                        requests.get(f'http://localhost:3000/removeoptionopen/{ctx.author.id}/{fullTicker}')
                        newOpenTotalCost = round(prevOpenTotalCost - totalCost, 2)
                        requests.get(f'http://localhost:3000/openoptionopen/{ctx.author.id}/{fullTicker}/{newOpenQuantity}/{newOpenTotalCost}')
                        if (closedArrayExist):
                            requests.get(f'http://localhost:3000/removeoptionclosed/{ctx.author.id}/{fullTicker}')
                        requests.get(f'http://localhost:3000/openoptionclosed/{ctx.author.id}/{fullTicker}/{newClosedQuantity}/{newClosedTotalCost}/{newClosedTotalCredit}')

                    embed.set_field_at(0, name="Order Confirmed", value=(f'You have: {userPotatoes} potatoes'),inline=False)
                    print(f"{ctx.author} has bought an options contract")
                elif str(reaction) == '❌':
                    embed.set_field_at(0, name="Order Rejected", value='\u200b',inline=False)

            except asyncio.TimeoutError:
                embed.set_field_at(0, name="Order Timed Out", value='\u200b',inline=False)

            await message.clear_reactions()
            await message.edit(embed=embed)
        except:
            await ctx.channel.send("Format incorrect or you have not registered.")

    ### Allows users to see their open (and eventually closed) stock and options positions
    @commands.command(aliases = ['openstocks', 'stocks'])
    async def openStocks(self, ctx):
        r = requests.get(f'http://localhost:3000/find/UserTrades/{ctx.author.id}')
        user = json.loads(r.text)

        string = ''
        for result in user:
            for i in range(len(result["openStocks"])):
                stock = result["openStocks"][i]["ticker"]
                quantity = result["openStocks"][i]["quantity"]
                totalCost = result["openStocks"][i]["totalCost"]
                totalCost = round(totalCost, 2)
                price = round(totalCost/quantity, 2)
                string = string + (f"Ticker: {stock} | Avg Cost: {price} | Quantity: {quantity} | Total Cost: {totalCost}\n")
        try:
            await ctx.channel.send(string)
        except:
            await ctx.channel.send("You have no open stock positions")

    @commands.command(aliases = ['closedstocks'])
    async def closedStocks(self, ctx):
        r = requests.get(f'http://localhost:3000/find/UserTrades/{ctx.author.id}')
        user = json.loads(r.text)

        string = ''
        for result in user:
            for i in range(len(result["closedStocks"])):
                stock = result["closedStocks"][i]["ticker"]
                quantity = result["closedStocks"][i]["quantity"]
                totalCost = result["closedStocks"][i]["totalCost"]
                totalCredit = result["closedStocks"][i]["totalCredit"]

                totalCost = round(totalCost, 2)
                totalCredit = round(totalCredit, 2)
                price = round(totalCost/quantity, 2)
                credit = round(totalCredit/quantity, 2)
                profitLoss = round(totalCredit - totalCost, 2)
                profitLossPercent = round(profitLoss/totalCost*100.0)
                string = string + (f"Ticker: {stock} | Avg Cost: {price} | Avg Credit: {credit} | Quantity: {quantity} | P/L: {profitLoss} or {profitLossPercent}%\n")
        try:
            await ctx.channel.send(string)
        except:
            await ctx.channel.send("You have no closed stock positions")

    @commands.command(aliases = ['openstock'])
    async def openStock(self, ctx, stock):
        # Formats given variables
        stock = stock.upper()

        #try:
        # Find specific position
        r = requests.get(f'http://localhost:3000/findstockopen/{ctx.author.id}/{stock}')
        user = json.loads(r.text)

        for result in user:
            for curStock in range(len(result["openStocks"])):
                if (result["openStocks"][curStock]['ticker'] == stock):
                    quantity = result["openStocks"][curStock]["quantity"]
                    totalCost = result["openStocks"][curStock]["totalCost"]
                    totalCost = round(totalCost, 2)
                    price = round(totalCost/quantity, 2)

        embed = discord.Embed(title=(f"Open Stock Info\nTotal Cost: {totalCost}"), description=(f"Ticker: {stock}\nPrice: {price}\nQuantity: {quantity}"),color=discord.Color.blue())
        embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")
        await ctx.channel.send(embed=embed)
        #except:
            #await ctx.channel.send(f"You do not own this position.")

    @commands.command(aliases = ['openoptions', 'options'])
    async def openOptions(self, ctx):
        r = requests.get(f'http://localhost:3000/find/UserTrades/{ctx.author.id}')
        user = json.loads(r.text)

        string = ''
        for result in user:
            for i in range(len(result["openOptions"])):
                stock, strike, optionType, date = result["openOptions"][i]["ticker"].split('_')
                quantity = result["openOptions"][i]["quantity"]
                totalCost = result["openOptions"][i]["totalCost"]
                totalCost = round(totalCost, 2)
                price = round(totalCost/quantity, 2)
                string = string + (f"Ticker: {stock} | Strike: {strike} {optionType} | Exp: {date} | Cost Per: {price} | Quantity: {quantity} | Total Cost: {totalCost}\n")
        try:
            await ctx.channel.send(string)
        except:
            await ctx.channel.send("You have no open option positions")

    @commands.command(aliases = ['closedoptions'])
    async def closedOptions(self, ctx):
        r = requests.get(f'http://localhost:3000/find/UserTrades/{ctx.author.id}')
        user = json.loads(r.text)

        string = ''
        for result in user:
            for i in range(len(result["closedOptions"])):
                stock, strike, optionType, date = result["closedOptions"][i]["ticker"].split('_')
                quantity = result["closedOptions"][i]["quantity"]
                totalCost = result["closedOptions"][i]["totalCost"]
                totalCredit = result["closedOptions"][i]["totalCredit"]

                totalCost = round(totalCost, 2)
                totalCredit = round(totalCredit, 2)
                price = round(totalCost/quantity, 2)
                credit = round(totalCredit/quantity, 2)
                profitLoss = round(totalCredit - totalCost, 2)
                profitLossPercent = round(profitLoss/totalCost*100.0)

                string = string + (f"Ticker: {stock} | Strike: {strike} {optionType} | Exp: {date} | Avg Cost: {price} | Avg Credit: {credit} | Quantity: {quantity} | P/L: {profitLoss} or {profitLossPercent}%\n")
        try:
            await ctx.channel.send(string)
        except:
            await ctx.channel.send("You have no closed option positions")

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
        if len(day) == 1:
            day = "0" + day
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
            r = requests.get(f'http://localhost:3000/findoptionopen/{ctx.author.id}/{stock}_{strike}_{optionType}_/{month}/{day}/{year}')
            user = json.loads(r.text)

            tickerMatch = f"{stock}_{strike}_{optionType}_{month}/{day}/{year}"
            for result in user:
                for option in range(len(result["openOptions"])):
                    if (result["openOptions"][option]['ticker'] == tickerMatch):
                        quantity = result["openOptions"][option]["quantity"]
                        totalCost = result["openOptions"][option]["totalCost"]
                        totalCost = round(totalCost, 2)
                        price = round(totalCost/quantity, 2)

            embed = discord.Embed(title=(f"Open Option Info\nTotal Cost: {totalCost}"), description=(f"Ticker: {stock} {optionType}\nStrike: {strike}\nExpiration: {month}/{day}/{year}\nPrice: {price}\nQuantity: {quantity}"),color=discord.Color.blue())
            embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")
            await ctx.channel.send(embed=embed)
        except:
            await ctx.channel.send(f"You do not own this position.")

def setup(client):
    client.add_cog(Trading(client))