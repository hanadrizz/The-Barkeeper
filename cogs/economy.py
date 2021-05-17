import discord
import discord.ext.commands.errors
import asyncio
from discord.ext import commands
from tinydb import TinyDB, Query
import os, random
from pretty_help import PrettyHelp
import json

Intents = discord.Intents.default()
Intents.members = True
Intents.messages = True
Intents.reactions = True
Intents.dm_messages = True

# EMOTES USED IN THE SLOTS, NOT REALLY MADE TO BE ADDED ANY MORE
slotsrow = [":lock:", ":heart:", ":purple_heart:", ":dolphin:", ":pig:", ":transgender_flag:", ":diamonds:", ":hearts:", ":flushed:", ":face_with_symbols_over_mouth:", ":blue_circle:"]

token = os.getenv('DISCORD_TOKEN')
description = "Commands for The Barkeeper"
bot = commands.Bot(command_prefix="?", intents=Intents, description=description, help_command=PrettyHelp())

database = TinyDB("database.json", sort_keys=True, indent=4, separators=(',', ': '))
data = Query()

# FETCHING THE USERS' LEVEL
def getPickaxeLevel(self, userid):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    pickaxelevel = record["pickaxetier"]
    return pickaxelevel
# CHANGING A USERS' LEVEL
def changePickaxeLevel(self, userid, level):
    database.upsert({"pickaxetier": level}, data.userid == userid)
# FETCHING A USERS' BALANCE
def getUserMoney(self, userid):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    return money
# REMOVING MONEY
def subtractMoney(self, userid, amount: int):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    money = money - amount
    database.upsert({"money":money}, data.userid == userid)
# ADDING MONEY
def addMoney(self, userid, amount):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    money = money + amount
    database.upsert({"money":money}, data.userid == userid)
# IF YOU DO NOT HAVE ENOUGH MONEY TO BUY A PICKAXE
async def denied(self, ctx, avatar):
    x = discord.Embed(title="Shop", color=0xff0000, description = f"Sorry {ctx.author.mention}, I can't give credit! Come back when you're a little... mmm... richer")
    x.set_author(name=ctx.author.name, icon_url=avatar)
    x.set_image(url="https://cdn.discordapp.com/attachments/821123717223415809/823315107261055006/morshu.gif")
    await ctx.send(embed=x)

# MINING COMMAND, GIVES A CHANCE DEPENDING ON THE TIER
async def mining(self, ctx, num1, userid):
    memb = self.bot.get_user(userid)
    x = random.randint(1, 100)
    num2 = 100 - num1
    if x <= num2:
        await ctx.send(f"Too bad, you only found rocks and scraps! {memb.mention}")
    else:
        y = random.randint(25, 200)
        await ctx.send(f"Woah, you found a gold ore! It's worth {y} :coin:! Lucky you! {memb.mention}")
        addMoney(self, userid, y)
        
#TIER SETUP, THIS IS WHERE I APPLY THE TIER NAMES, COSTS AND CHANCE OF MINING SOMETHING GOOD
pickaxetiers = ["wood","stone","copper","iron","steel","gold","diamond","platinum"]
pickaxecost = {"wood":           0,
                "stone":     10000,
                "copper":    20000,
                "iron":      50000,
                "steel":    100000,
                "gold":     150000,
                "diamond":  300000,
                "platinum": 500000}
miningchances = {1 : 30, 2 : 40, 3 : 50, 4 : 60, 5 : 70, 6 : 80, 7 : 90, 8 : 95}


class Economy(commands.Cog):
    """Capitalism in a nutshell. Use money, I guess"""

    def __init__(self, bot):
        self.bot = bot
    # BALANCE COMMAND
    # ALLOWS YOU TO SEE OTHERS ASWELL
    @bot.command(brief="Displays the user's balance", description="Displays the user's balance", aliases=["bal","bank","money"])
    async def balance(self, ctx, user:discord.Member=None):
        if user == None:
            userid = ctx.author.id
            balance = getUserMoney(self, userid)
            await ctx.send(f"{ctx.author.mention} Your balance is {balance} :coin:")
        else:
            userid = user.id
            balance = getUserMoney(self, userid)
            await ctx.send(f"{ctx.author.mention}, {user.display_name}'s balance is {balance} :coin:")
    #SHOPPING
    @bot.command(brief="Access the shop", description="Main command to access, buy and find items in the shop.")
    async def shop(self, ctx, arg="help", *, item=""):
        user = ctx.author
        userid = user.id
        avatar = user.avatar_url
        # DISPLAY ITEMS IN A LIST
        if "list" in arg:
            shop=discord.Embed(title="Shop", description="The one destination for all your needs!", color=0xff0000)
            shop.set_author(name=ctx.author.name, icon_url=avatar)
            pickaxelevel = getPickaxeLevel(self, userid)
            output = ""
            for i in range(len(pickaxetiers)): # USING THIS INSTEAD OF MANUALLY PUTTING IT ALL OUT
                if i+1 <= pickaxelevel:
                    output = output + f"{pickaxetiers[i]} pickaxe: You already own this item \n"
                else:
                    output = output + f"{pickaxetiers[i]} pickaxe: {pickaxecost[pickaxetiers[i]]} :coin:\n"
            shop.add_field(name="Pickaxes", value=output, inline=True)
            shop.set_footer(text = "^shop buy [item]")
            
            await ctx.send(embed=shop)
        # POINTING USERS TO THE RIGHT COMMANDS
        elif "help" in arg:
            await ctx.send("``shop buy [item]`` to buy things and ``shop list`` to see list.")
        # BUYING PICKAXES
        elif "buy" in arg:
            pickaxelevel = getPickaxeLevel(self, userid)
            money = getUserMoney(self, userid)
            items = ['wood', 'stone', 'copper', 'iron', "steel", 'gold', 'diamond', 'platinum']
            for i in item.lower().split():
                if i in items: # CHECKING THE PRICE
                    Newpickaxelevel = items.index(i) + 1
                    cost = dict.get(pickaxecost, i)
                    if money < cost:
                        await denied(self, ctx, avatar) # IF YOU DONT HAVE ENOUGH MONEY
                    elif pickaxelevel >= Newpickaxelevel: # DOESNT REALLY MAKE SENSE TO BUY SOMETHING YOU HAVE
                        await ctx.send("You already own this pickaxe, sorry!") 
                    else: # IF YOU BOTH HAVE ENOUGH MONEY AND DONT OWN IT, YOU GET IT, WOAH!
                        changePickaxeLevel(self, userid, Newpickaxelevel)
                        subtractMoney(self, userid, cost)
                        await ctx.send(f"You have successfully gotten a {i} pickaxe! Happy mining!") 
        else:
            await ctx.send("Invalid command. ``shop buy [item]`` to buy things and ``shop list`` to see list.")  
        
    # MINING COMMAND    
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    @bot.command(brief="Mines for money", description="Randomized chance to find ores or scraps. Better pickaxes give out more often rewards")
    async def mine(self, ctx):
        user = ctx.message.author
        userid = user.id
        pickaxelevel = getPickaxeLevel(self, userid)
        if pickaxelevel == 0:
            await ctx.send(f"You don't own a pickaxe yet! You need to buy it from the shop! Check our collection at ```^shop list```")

        elif pickaxelevel > 0:
            await mining(self, ctx, miningchances[pickaxelevel], userid)

    # LEADERBOARD SYSTEM
    @bot.command(brief="Leaderboard of the richest users.", description="This is a leaderboard of the richest users on the server.")
    async def leaderboard(self, ctx):
        leaderboard = {}
        with open("database.json") as f:
            leaderboard = json.load(f)
        f.close()
        leaderboard = leaderboard["_default"]
        richest = sorted(leaderboard, key=lambda k: -leaderboard[k]["money"])
        embed=discord.Embed(title="Leaderboard - Top 5", description="Richest users in the server", color=0x8080ff)
        embed.set_author(name="Top users", icon_url="https://cdn.discordapp.com/avatars/820839140111155200/9453547c9ae893eb3a3833ff7734a4ac.webp?size=1024")
        for k in richest[:5]:  # <-- change to 10 if you want top 10
            user = self.bot.get_user(leaderboard[k]["userid"])
            money = leaderboard[k]["money"]
            embed.add_field(name=user.display_name, value=f"{money} :coin:", inline=False)
        await ctx.send(embed=embed)
    # WELL SOMETIMES YOU JUST HAVE TO GIVE USERS A GAMBLING ADDICTION
    # WITH FICTIOUS MONEY, OF COURSE
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @bot.command(brief="The house always wins, you know.", description="Slot machine.")
    async def slots(self, ctx, amount: int):
        userid = ctx.message.author.id
        datasearch = database.search(data.userid == userid)
        record = datasearch[0]
        money = record["money"]
        if amount > money:
            await ctx.send("You can't gamble, you don't have enough money!")
        else:
            if amount <= 0:
                await ctx.send("You need to actually bet, you know?")
            else:
                subtractMoney(self, userid, amount)
                rand = random.randint(0,100) # CHANCE TO WIN
                y = random.sample(range(11), 9)
                ran = len(y)
                gamble = await ctx.send(content=f"**[S L O T S]**\n[----------------]\n| {slotsrow[y[0]]} | {slotsrow[y[1]]} | {slotsrow[y[2]]} |\n| {slotsrow[y[3]]} | {slotsrow[y[4]]} | {slotsrow[y[5]]} |\n| {slotsrow[y[6]]} | {slotsrow[y[7]]} | {slotsrow[y[8]]} |\n[----------------]")
                if rand > 80:
                    for x in range(5):
                        await asyncio.sleep(0.2)
                        count = 0
                        for a in range(ran):
                            y[count] = y[count] + 1
                            if y[count] >= 10:
                                y[count] = 0
                            count += 1 # I KNOW, KINDA CLUNKY BUT IT WORKS
                        await gamble.edit(content=f"**[S L O T S]**\n[----------------]\n| {slotsrow[y[0]]} | {slotsrow[y[1]]} | {slotsrow[y[2]]} |\n| {slotsrow[y[3]]} | {slotsrow[y[4]]} | {slotsrow[y[5]]} |\n| {slotsrow[y[6]]} | {slotsrow[y[7]]} | {slotsrow[y[8]]} |\n[----------------]")
                    await asyncio.sleep(0.2)
                    await gamble.edit(content=f"**[S L O T S]**\n[----------------]\n| {slotsrow[y[1]]} | {slotsrow[y[1]]} | {slotsrow[y[2]]} |\n| {slotsrow[8]} | {slotsrow[y[4]]} | {slotsrow[y[5]]} |\n| {slotsrow[y[7]]} | {slotsrow[y[7]]} | {slotsrow[y[8]]} |\n[----------------]")
                    await asyncio.sleep(0.5)
                    await gamble.edit(content=f"**[S L O T S]**\n[----------------]\n| {slotsrow[y[1]]} | {slotsrow[y[2]]} | {slotsrow[y[2]]} |\n| {slotsrow[8]} | {slotsrow[8]} | {slotsrow[y[5]]} |\n| {slotsrow[y[7]]} | {slotsrow[y[8]]} | {slotsrow[y[8]]} |\n[----------------]")
                    await asyncio.sleep(0.5)
                    await gamble.edit(content=f"**[S L O T S]**\n[----------------]\n| {slotsrow[y[1]]} | {slotsrow[y[2]]} | {slotsrow[y[3]]} |\n| {slotsrow[8]} | {slotsrow[8]} | {slotsrow[8]} |\n| {slotsrow[y[7]]} | {slotsrow[y[8]]} | {slotsrow[y[0]]} |\n[----------------]")
                    pot = amount * 3 
                    await ctx.send(f"{ctx.message.author} has won {pot} coins!!! Hurrah!")
                    addMoney(self, userid, pot)
                    
                elif rand <= 80:
                    for x in range(5):
                        count = 0
                        for a in range(ran):
                            y[count] = y[count] + 1
                            if y[count] == 11:
                                y[count] = 0
                            count += 1

                        await gamble.edit(content=f"**[S L O T S]**\n[----------------]\n| {slotsrow[y[0]]} | {slotsrow[y[1]]} | {slotsrow[y[2]]} |\n| {slotsrow[y[3]]} | {slotsrow[y[4]]} | {slotsrow[y[5]]} |\n| {slotsrow[y[6]]} | {slotsrow[y[7]]} | {slotsrow[y[8]]} |\n[----------------]")
                    await ctx.send(f"{ctx.message.author} lost {amount} :coin:")



def setup(bot):
    bot.add_cog(Economy(bot))
