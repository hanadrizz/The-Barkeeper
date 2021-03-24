import discord
import discord.ext.commands.errors
import dotenv
import asyncio
from discord.ext import commands
import apraw
import configparser
import os, random
from pretty_help import PrettyHelp
from mediawiki import MediaWiki
import textwrap
import time



config = configparser.ConfigParser()
config.read('db.ini')

clientid = config['reddit']['client_id']
clientsecret = config['reddit']['client_secret']
useragent = config['reddit']['user_agent']
username = config['reddit']['username']
password = config['reddit']['password']

Intents = discord.Intents.default()
Intents.members = True
Intents.messages = True
Intents.reactions = True
Intents.dm_messages = True

token = os.getenv('DISCORD_TOKEN')

reddit = apraw.Reddit(client_id = clientid, client_secret = clientsecret, user_agent=useragent, username = username, password=password)
bannedsubs = ["urinalpics", "urinalshitters", "urinalpoop", "poo", "kropotkistan", "femboy", "trans", "feemagers"]
description = "Commands for The Barkeeper"
bot = commands.Bot(command_prefix="^", intents=Intents, description=description, help_command=PrettyHelp())
processed = []

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(brief="Bot license", description="Displays the MIT license for the bot's code, including its Github link")
    async def license(self, ctx):
        with open("LICENSE", "r") as license:
            notice = license.read()
            notice = notice + "\n\nRepository can be found at <https://github.com/hanadrizz/The-Barkeeper>"
            await ctx.send(notice)

    @bot.command(brief="Sends back the latency for the bot", description="Sends back how long it takes for the bot to respond. Good for checking if the bot is online.")
    async def ping(self, ctx):
        await ctx.send(f"Pong! **{self.bot.latency}ms**")
        print(f"{ctx.message.author.name} pinged")

    
    @bot.command(brief="Looks up a summary of a wikipedia page", description="Looks up a summary of a wikipedia page")
    async def wiki(self, ctx, *, page):
        print(f"{ctx.message.author.name} requested {page}")
        wikipage = MediaWiki()
        try:
            site = wikipage.page(page, auto_suggest=False)
            summary = wikipage.summary(page, auto_suggest=False)
            summary_list = textwrap.wrap(summary, 2000, break_long_words=False)
            for i in summary_list:
                await ctx.channel.send(i)
            await ctx.channel.send(f"<{site.url}>")
        except Exception as inst:
            site = wikipage.page(page)
            summary = wikipage.summary(page)
            summary_list = textwrap.wrap(summary, 2000, break_long_words=False)
            for i in summary_list:
                await ctx.channel.send(i)
            await ctx.channel.send(f"<{site.url}>")

    @bot.command(brief="Searches for a random image in a specified subreddit", description="Searchees for a random image in a specified subreddit")
    async def redditsearch(self, ctx, sub):
        try:
            print(f"{ctx.message.author.name} searched for an image in r/{sub}")
            start_time = time.time()
            if sub == "traa":
                sub = "traaaaaaannnnnnnnnns"
            if sub == "okbr":
                sub = "okbuddyretard"
            listing = []
            subreddit = await reddit.subreddit(sub)
            if sub.lower() in bannedsubs:
                await ctx.send("Subreddit is blocked in the server filter.")
                return
            elif subreddit.over18 == True:
                await ctx.send("No NSFW subreddits.")
                return
            else:
                async for submission in subreddit.hot(limit=100):
                    if submission.url.endswith(("jpg", "jpeg", "png", "gifv")) and not submission.spoiler and not submission.over_18:
                        listing.append(submission)
                    else:
                        pass
            
                random.shuffle(listing)
                post = listing[0]
                if submission.link_flair_text == None:
                    await ctx.send(f"{post.title}\n{post.url}")
                else:
                    await ctx.send(f"[{submission.link_flair_text}] \n{post.title}\n{post.url}")
                end_time = time.time()
                endresult = end_time - start_time
                await ctx.send(f"---- Took %s seconds to lookup ----" % (endresult))
                processed.append(endresult)
        except AttributeError:
            await ctx.send(f"Fetching image failed. This is probably due to `{sub}` not existing or being restricted.")
        except IndexError:
            await ctx.send(f"Fetching image failed. This is probably due to `{sub}` not being a image heavy subreddit.")
        except:
            await ctx.send(f"Fetching image failed. This is most likely due to using non-standard search term. Correct usage is ``^redditsearch [subreddit name]``. Without the r/")

    @bot.command(brief="Returns the specified users' avatar", description="Displays the specified user's avatar")
    async def avatar(self, ctx, avamember: discord.Member = ""):
        if avamember == "":
            print("a")
            avamember = self.bot.get_user(ctx.author.id)
        userAvatarUrl = avamember.avatar_url
        await ctx.send(userAvatarUrl)
        print(f"{ctx.message.author.name} looked up {avamember}'s avatar.")

def setup(bot):
    bot.add_cog(User(bot))
