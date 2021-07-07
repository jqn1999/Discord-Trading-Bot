import discord
from discord.ext import commands
import requests
import json
import datetime
import asyncio
import random
import time
import math

client = discord.Client()

class Game(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['givepotatoes', 'give'])
    async def givePotatoes(self, ctx, member: discord.Member, potatoes):
        try:
            potatoes = int(potatoes)
        except:
            await ctx.channel.send("Cannot read potato amount")
            return

        if potatoes <= 0:
            await ctx.channel.send("Please enter a valid potato amount")
            return
        
        # Queries database for user info
        r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
        user = json.loads(r.text)

        if (user != []):
            for result in user:
                userPotatoes = result["potatoes"]
        else:
            await ctx.channel.send('You need to register')
            return

        if (userPotatoes < potatoes):
            await ctx.channel.send(f"You do not have that many potatoes to give, you have {userPotatoes} potatoes")
            return
        else:
            newUserPotatoes = userPotatoes - potatoes
            requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{newUserPotatoes}')

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

    @commands.command(alises = ['Hunt', 'HUNT'])
    async def hunt(self, ctx):
        r = requests.get(f'http://localhost:3000/find/UserData/{ctx.author.id}')
        user = json.loads(r.text)
        r = requests.get(f'http://localhost:3000/find/UserGameStats/{ctx.author.id}')
        userGameStats = json.loads(r.text)

        if (user != [] and userGameStats != []):
            for result in user:
                potatoes = result["potatoes"]
                huntTimer = result["huntTimer"]
            for stats in userGameStats:
                level = stats["level"]
                experience = stats["experience"]
                regularKills = stats["regularKills"]
                epicKills = stats["epicKills"]
                legendaryKills = stats["legendaryKills"]
                mythicKills = stats["mythicKills"]
                losses = stats["losses"]
                totalGain = stats["totalGain"]
        else:
            await ctx.channel.send('You need to register before you can hunt')
            return

        if (huntTimer+120 < int(time.time())):
            pass
        else:
            remainingTime = huntTimer+120-int(time.time())
            if (remainingTime >= 60):
                remainingTime = math.ceil( (huntTimer+120-int(time.time()))/60)
                await ctx.channel.send(f'You have {remainingTime} minutes until you can hunt again.')
                return
            else:
                await ctx.channel.send(f'You have {remainingTime} seconds until you can hunt again.')
                return

        monsterRNG = random.randint(1, 1000)
        if monsterRNG <= 950:
            regularKills += 1
            loseCost = 100
            reward = 100
            chanceToWin = random.randint(int((80 + 1.07**(level))*.95), int((80 + 1.07**(level))*1.05))
            chosenType = 'regular'
        elif monsterRNG <= 980:
            epicKills += 1
            loseCost = 200
            reward = 1000
            chanceToWin = random.randint(int((40 + 1.07**(level))*.95), int((40 + 1.07**(level))*1.05))
            chosenType = 'epic'
        elif monsterRNG <= 995:
            legendaryKills += 1
            loseCost = round(potatoes*.05)
            reward = 20000
            chanceToWin = random.randint(int((10 + 1.07**(level))*.95), int((10 + 1.07**(level))*1.05))
            chosenType = 'legendary'
        else:
            mythicKills += 1
            loseCost = round(potatoes*.10)
            reward = 800000
            chanceToWin = random.randint(int((5 + 1.07**(level))*.95), int((5 + 1.07**(level))*1.05))
            chosenType = 'mythic'

        r = requests.get(f'http://localhost:3000/findmonsters')
        monsters = json.loads(r.text)
        for result in monsters:
            numMonsters = len(result[chosenType])-1
            chosenMonsterIndex = random.randint(0, numMonsters)
            chosenMonsterName = result[chosenType][chosenMonsterIndex]["name"]
            chosenMonsterType = result[chosenType][chosenMonsterIndex]["type"]
            chosenMonsterExp = result[chosenType][chosenMonsterIndex]["experience"]
            chosenMonsterHP = result[chosenType][chosenMonsterIndex]["health"]
            chosenMonsterAttack = result[chosenType][chosenMonsterIndex]["attack"]
            chosenMonsterImg = result[chosenType][chosenMonsterIndex]["image"]

        embed = discord.Embed(title=(f"{chosenMonsterName}\nDifficulty: {chosenMonsterType}"), description=(f"HP: {chosenMonsterHP}\nATK: {chosenMonsterAttack}\nChance to Win: {chanceToWin}%"),color=discord.Color.dark_gold())
        embed.set_author(name=ctx.author.name, url="https://www.youtube.com/user/maniacbraniac115", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=chosenMonsterImg)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text="Potato Hoarders",icon_url="https://i.imgur.com/uZIlRnK.png")
        embed.add_field(name="Attack or run\nby reacting\nwith a ✅ or a ❌\nin the next 20 seconds.",value='\u200b',inline=False)
        message = await ctx.channel.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')

        def check(reaction, user):
            return reaction.message == message and str(reaction) in ['✅','❌'] and user == ctx.author
        
        # Checks if user accepts or rejects the given price
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout = 20.0, check=check)

            if str(reaction) == '✅':
                requests.get(f'http://localhost:3000/huntupdate/{ctx.author.id}/{int(time.time())}')
                playerWinRoll = random.randint(0, 100)
                if playerWinRoll <= chanceToWin:
                    # Win
                    reward = random.randint(int(reward*.8),int(reward*1.2))
                    newPotatoes = round(potatoes + reward, 2)
                    requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{newPotatoes}')

                    newExperience = experience + random.randint(int(chosenMonsterExp*.9), int(chosenMonsterExp*1.1))
                    newLevel = int(experience/500)+1
                    requests.get(f'http://localhost:3000/gameuserupdate/{ctx.author.id}/{newLevel}/{newExperience}/{regularKills}/{epicKills}/{legendaryKills}/{mythicKills}')

                    newTotalGain = round(totalGain + reward, 2)
                    requests.get(f'http://localhost:3000/updatehuntgain/{ctx.author.id}/{newTotalGain}')

                    embed.set_field_at(0, name=f"u merked the homie and\ngained {reward} potatoes", value=(f'You now have: {newPotatoes} potatoes'),inline=False)
                else:
                    # Lose
                    lostPotatoes = random.randint(int(loseCost*.2),int(loseCost*1.2))
                    newPotatoes = round(potatoes - lostPotatoes, 2)
                    requests.get(f'http://localhost:3000/updatepotatoes/{ctx.author.id}/{newPotatoes}')

                    newLosses = losses + 1
                    requests.get(f'http://localhost:3000/updatelosses/{ctx.author.id}/{newLosses}')

                    embed.set_field_at(0, name=f"u got merked n lost\n{lostPotatoes} potatoes", value=(f'You now have: {newPotatoes} potatoes'),inline=False)
                print(f"{ctx.author} has gone hunting")
            elif str(reaction) == '❌':
                embed.set_field_at(0, name="Player Ran Away", value='\u200b',inline=False)
        except asyncio.TimeoutError:
            embed.set_field_at(0, name="Player Ran Away", value='\u200b',inline=False)

        await message.clear_reactions()
        await message.edit(embed=embed)

    @commands.command()
    async def bet(self, ctx, option, potatoes):
        # check option validity
        # check potato amount validity
        # check open poll validity
        # insert or return error
        print('x')

def setup(client):
    client.add_cog(Game(client))