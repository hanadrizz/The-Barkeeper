import discord
import discord.ext.commands.errors
import dotenv
import asyncio
from discord.ext import commands
import os
from pretty_help import PrettyHelp
from tinydb import TinyDB, Query
from TextToOwO.owo import text_to_owo
from mediawiki import MediaWiki
import textwrap

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
imagefolder = "images\\"

class Fun(commands.Cog):
    """the stupidest commands can be found here"""
    def __init__(self, bot):
        self.bot = bot

    @bot.command(brief="Wooks up a summawy of a wikipedia page", description="Wooks up a summawy of a wikipedia page")
    async def wikowo(self, ctx, *, page):
        print(f"{ctx.message.author.name} requested {page}")
        wikipage = MediaWiki()
        try:
            site = wikipage.page(page, auto_suggest=False)
            summary = wikipage.summary(page, auto_suggest=False)
            owo = text_to_owo(summary)
            summary_list = textwrap.wrap(owo, 2000, break_long_words=False)
            for i in summary_list:
                await ctx.channel.send(i)
            await ctx.channel.send(f"<{site.url}>")
        except Exception as inst:
            site = wikipage.page(page)
            summary = wikipage.summary(page)
            owo = text_to_owo(summary)
            summary_list = textwrap.wrap(owo, 2000, break_long_words=False)
            for i in summary_list:
                await ctx.channel.send(i)
            await ctx.channel.send(f"<{site.url}>")
    
    @bot.command(brief="OwO, whats this? uwaaa >.<")
    async def owo(self, ctx, *, text):
        text = text_to_owo(text)
        await ctx.send(text)

    @bot.command(brief="Rock, paper, scissors", description="For some reason, people always lose.")
    async def rps(self, ctx, choice=""):
        if choice == "":
            await ctx.send("You need to pick between ``rock``, ``paper`` or ``scissor``")

        elif choice == "rock":
            await ctx.send("You lose!")
        elif choice == "paper":
            await ctx.send("You lose!")
        elif choice == "scissor":
            await ctx.send("You lose!")
        else:
            await ctx.send("Correct command usage is ``^rps [choice]")

    @bot.command(brief="Why don't you try me out?", description="we love some puns dont we")
    async def complementarybread(self, ctx):
        user = ctx.message.author
        await user.send("Hey!")
        await ctx.send("Psst... come with me down this alley!")
        await user.send("https://cdn.discordapp.com/attachments/821123717223415809/827637301953429514/complementarybread.png")
        print(f"Welcome to the bread bank, {user}")
        
    @bot.command(brief="thats a bit SUSSY", description="amogus")
    async def sus(self, ctx):
        await ctx.send("sus")
        print(f"{ctx.message.author.name} sus")

    @bot.command(brief="moo", description="moo")
    async def jamaal(self, ctx):
        await ctx.send("man\nhttps://cdn.discordapp.com/attachments/821123717223415809/821642340359733258/f4xz3iryogm61.jpg")
        print(f"{ctx.message.author.name} jamaal")

    @bot.command(brief="Hug a user!", description="Hug a user!")
    async def hug(self, ctx, arg : discord.Member=None):
        await ctx.send(f"<@{ctx.message.author.id}> is hugging <@{arg.id}>! :people_hugging:")
        
    @bot.command(brief="heehoo i have the mentality of a six year old", description="im still six years old")
    async def sex(self, ctx):
        await ctx.send("thats what i have with your mom lmao 🔥🔥🔥🔥")
        print(f"{ctx.message.author.name} sex")

def setup(bot):
    bot.add_cog(Fun(bot))