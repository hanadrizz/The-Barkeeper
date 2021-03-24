import discord
import discord.ext.commands.errors
import dotenv
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

token = os.getenv('DISCORD_TOKEN')
description = "Commands for The Barkeeper"
bot = commands.Bot(command_prefix="^", intents=Intents, description=description, help_command=PrettyHelp())

database = TinyDB("database.json", sort_keys=True, indent=4, separators=(',', ': '))
data = Query()

def getPickaxeLevel(self, userid):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    pickaxelevel = record["pickaxetier"]
    return pickaxelevel

def changePickaxeLevel(self, userid, level):
    database.upsert({"pickaxetier": level}, data.userid == userid)

def getUserMoney(self, userid):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    return money

def subtractMoney(self, userid, amount: int):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    money = money - amount
    database.upsert({"money":money}, data.userid == userid)

def addMoney(self, userid, amount):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    money = money + amount
    database.upsert({"money":money}, data.userid == userid)

async def denied(self, ctx, avatar):
    x = discord.Embed(title="Shop", color=0xff0000, description = f"Sorry {ctx.author.mention}, I can't give credit! Come back when you're a little... mmm... richer")
    x.set_author(name=ctx.author.name, icon_url=avatar)
    x.set_image(url="https://cdn.discordapp.com/attachments/821123717223415809/823315107261055006/morshu.gif")
    await ctx.send(embed=x)

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
        
    
pickaxetiers = ["wood","stone","copper","iron","steel","gold","diamond","platinum"]
pickaxecost = {"wood":           0,
                "stone":     10000,
                "copper":    20000,
                "iron":      50000,
                "steel":    100000,
                "gold":     150000,
                "diamond":  300000,
                "platinum": 500000}
miningchances = {1 : 35, 2 : 45, 3 : 50, 4 : 60, 5 : 70, 6 : 80, 7 : 90, 8 : 95}


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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

    @bot.command(brief="Access the shop", description="Main command to access, buy and find items in the shop.")
    async def shop(self, ctx, arg="help", *, item=""):
        user = ctx.author
        userid = user.id
        avatar = user.avatar_url

        if "list" in arg:
            shop=discord.Embed(title="Shop", description="The one destination for all your needs!", color=0xff0000)
            shop.set_author(name=ctx.author.name, icon_url=avatar)
            pickaxelevel = getPickaxeLevel(self, userid)
            output = ""
            for i in range(len(pickaxetiers)):
                if i+1 <= pickaxelevel:
                    output = output + f"{pickaxetiers[i]} pickaxe: You already own this item \n"
                else:
                    output = output + f"{pickaxetiers[i]} pickaxe: {pickaxecost[pickaxetiers[i]]} :coin:\n"
            shop.add_field(name="Pickaxes", value=output, inline=True)
            shop.set_footer(text = "^shop buy [item]")
            
            await ctx.send(embed=shop)

        elif "help" in arg:
            await ctx.send("``shop buy [item]`` to buy things and ``shop list`` to see list.")

        elif "buy" in arg:
            pickaxelevel = getPickaxeLevel(self, userid)
            money = getUserMoney(self, userid)
            items = ['wood', 'stone', 'copper', 'iron', "steel", 'gold', 'diamond', 'platinum']
            for i in item.lower().split():
                if i in items:
                    Newpickaxelevel = items.index(i) + 1
                    cost = dict.get(pickaxecost, i)
                    if money < cost:
                        await denied(self, ctx, avatar)
                    elif pickaxelevel >= Newpickaxelevel:
                        await ctx.send("You already own this pickaxe, sorry!")
                    else:
                        changePickaxeLevel(self, userid, Newpickaxelevel)
                        subtractMoney(self, userid, cost)
                        await ctx.send(f"You have successfully gotten a {i} pickaxe! Happy mining!")
        else:
            await ctx.send("Invalid command. ``shop buy [item]`` to buy things and ``shop list`` to see list.")  
            
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.user)
    @bot.command(brief="Mines for money", description="Randomized chance to find ores or scraps. Better pickaxes give out more often rewards")
    async def mine(self, ctx):
        user = ctx.message.author
        userid = user.id
        pickaxelevel = getPickaxeLevel(self, userid)
        if pickaxelevel == 0:
            await ctx.send(f"You don't own a pickaxe yet! You need to buy it from the shop! Check our collection at ```^shop list```")

        elif pickaxelevel > 0:
            await mining(self, ctx, miningchances[pickaxelevel], userid)

    @bot.command(brief="Leaderboard of the richest users.", description="This is a leaderboard of the richest users on the server.")
    async def leaderboard(self, ctx):
        leaderboard = {}
        with open("database.json") as f:
            leaderboard = json.load(f)
        f.close()
        leaderboard = leaderboard["_default"]
        richest = sorted(leaderboard, key=lambda k: -leaderboard[k]["money"])
        embed=discord.Embed(title="Leaderboard - Top 5", description="Richest users in the server", color=0x8080ff)
        embed.set_author(name="The Bar", icon_url="https://cdn.discordapp.com/avatars/820839140111155200/9453547c9ae893eb3a3833ff7734a4ac.webp?size=1024")
        for k in richest[:5]:  # <-- change to 10 if you want top 10
            user = self.bot.get_user(leaderboard[k]["userid"])
            money = leaderboard[k]["money"]
            embed.add_field(name=user.display_name, value=f"{money} :coin:", inline=False)
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Economy(bot))