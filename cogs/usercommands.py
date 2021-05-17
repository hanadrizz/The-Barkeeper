import discord
import discord.ext.commands.errors
from discord.ext import commands
import apraw
import configparser
import os, random
from pretty_help import PrettyHelp
from mediawiki import MediaWiki
import textwrap
import time
import requests

config = configparser.ConfigParser()
config.read('db.ini')

# CONFIGURATION
verf = config.getint("setup", "verf")
verfrole = config.getint("setup", "verfrole")
minecraftip = config.getint("setup", "mcip")

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

reddit = apraw.Reddit(client_id = clientid, client_secret = clientsecret, user_agent=useragent, username = username, password=password)
# BANLIST FOR ?REDDITSEARCH
bannedsubs = config["filter"]["bannedsubs"].split()
description = "Commands for the bot"
bot = commands.Bot(command_prefix="?", intents=Intents, description=description, help_command=PrettyHelp())
processed = []

class User(commands.Cog):
    """General purpose commands"""
    def __init__(self, bot):
        self.bot = bot

    # VERY IMPORTANT LICENSE, PLEASE DO NOT VIOLATE IT
    @bot.command(brief="Bot license", description="Displays the GNU GPLv3 license for the bot's code, including its Github link")
    async def license(self, ctx):
        await ctx.send("""
        This bot isis licensed under the GNU VERSION 3 GENERAL PUBLIC LICENSE.

        The GNU General Public License is a free, copyleft license for software and other kinds of works.

        The licensed material and derivatives may be used for commercial purposes.
        The licensed material may be distributed.
        The licensed material may be modified.
        This license provides an express grant of patent rights from contributors.
        The licensed material may be used and modified in private.

        Source code must be made available when the licensed material is distributed.
        A copy of the license and copyright notice must be included with the licensed material.
        Modifications must be released under the same license when distributing the licensed material.
        Changes made to the licensed material must be documented.

        This license includes a limitation and/or no liability.
        This liceense explicitly states that it does NOT provide any warranty.

        The full license document may be read at <https://choosealicense.com/licenses/gpl-3.0/>
        The original repository may be found at  <https://github.com/hanadrizz/The-Barkeeper>
        """)

    # MAKES AN API CALL TO MCSRVSTAT FOR SERVER INFORMATION
    @bot.command(brief="Minecraft server status", description="Minecraft server status")
    async def minecraft(self, ctx):
        response = requests.get(f"https://api.mcsrvstat.us/2/{minecraftip}")
        embed=discord.Embed(title="Minecraft Server", color=0x2fab0f)
        response = response.json()
        if response["online"] == True:
            embed.add_field(name="Online?", value="True", inline=False)
            embed.add_field(name="Player count", value=f"{response['players']['online']}/{response['players']['max']}", inline=False)
            try:
                playerlist = ""
                for player in response["players"]["list"]:
                    playerlist += f"{player}\n"
                embed.add_field(name="Player list", value=playerlist, inline=False)
            except:
                pass
            embed.set_footer(text=f"Server IP: {response['ip']}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Server offline.")  

    # THIS IS USEFUL FOR CHECKING IF THE BOT IS ONLINE
    # OR NOT, DISCORD PRESENCE TENDS TO BE SLOW WHEN IT
    # COMES TO THAT, AND THIS ONE IS A NONDESTRUCTIVE METHOD
    # FOR THAT KIND OF TESTING
    @bot.command(brief="Sends back the latency for the bot", description="Sends back how long it takes for the bot to respond. Good for checking if the bot is online.")
    async def ping(self, ctx):
        await ctx.send(f"Pong! **{self.bot.latency}ms**")
        print(f"{ctx.message.author.name} pinged")

    # LOOKS UP A SUMMARY OF A WIKIPEDIA PAGE AND POSTS IT TO THE CHANNEL
    @bot.command(brief="Looks up a summary of a wikipedia page", description="Looks up a summary of a wikipedia page")
    async def wiki(self, ctx, *, page):
        print(f"{ctx.message.author.name} requested {page}")
        wikipage = MediaWiki()
        try:
            site = wikipage.page(page, auto_suggest=False)
            summary = wikipage.summary(page, auto_suggest=False)
            summary_list = textwrap.wrap(summary, 2000, break_long_words=False) # BREAKS UP A MESSAGE IF ITS OVER 2000 CHARACTERS (DISCORD LIMIT)
            for i in summary_list:
                await ctx.channel.send(i)
            await ctx.channel.send(f"<{site.url}>")
        except Exception as inst: # IF IT FAILS TO FIND THE SPECIFIC PAGE, THIS ONE ATTEMPTS TO FIND THE RIGHT ONE
            site = wikipage.page(page)
            summary = wikipage.summary(page)
            summary_list = textwrap.wrap(summary, 2000, break_long_words=False)
            for i in summary_list:
                await ctx.channel.send(i)
            await ctx.channel.send(f"<{site.url}>")
    # FINDS A RANDOM IMAGE IN ANY SUBREDDIT
    @bot.command(brief="Searches for a random image in a specified subreddit", description="Searchees for a random image in a specified subreddit")
    async def redditsearch(self, ctx, sub):
        try:
            print(f"{ctx.message.author.name} searched for an image in r/{sub}")
            start_time = time.time()
            if sub == "traa": # JUST MAKING IT EASIER TO FIND IMAGES IN TRAA AND OBKR
                sub = "traaaaaaannnnnnnnnns"
            if sub == "okbr":
                sub = "okbuddyretard" # SLUR FILTER LOL
            listing = []
            subreddit = await reddit.subreddit(sub)
            if sub.lower() in bannedsubs:
                await ctx.send("Subreddit is blocked in the server filter.") # FILTER
                return
            elif subreddit.over18 == True:
                await ctx.send("No NSFW subreddits.") # NO HORNY
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
        except AttributeError: # ERROR HANDLING, SOMETIMES THERE ARE NO IMAGES TO BE FOUND
            await ctx.send(f"Fetching image failed. This is probably due to `{sub}` not existing or being restricted.")
        except IndexError:
            await ctx.send(f"Fetching image failed. This is probably due to `{sub}` not being a image heavy subreddit.")
        except:
            await ctx.send(f"Fetching image failed. This is most likely due to using non-standard search term. Correct usage is ``^redditsearch [subreddit name]``. Without the r/")
    # GRABS THE USERS' PROFILE IMAGE AND POSTS IT
    @bot.command(brief="Returns the specified users' avatar", description="Displays the specified user's avatar")
    async def avatar(self, ctx, avamember: discord.Member = ""):
        if avamember == "":
            print("a")
            avamember = self.bot.get_user(ctx.author.id)
        userAvatarUrl = avamember.avatar_url
        await ctx.send(userAvatarUrl)
        print(f"{ctx.message.author.name} looked up {avamember}'s avatar.")
    
    # VERIFIES A USER FOR A SPECIFIC CHANNEL IN A SPECIFIC CHANNEL
    @bot.command(brief="Verifies the user for the NSFW channel.", hidden=True)
    async def verify(self, ctx):
        verify = self.bot.get_channel(verf)
        mes = ctx.message
        if ctx.message.channel == verify:
            member = ctx.message.author
            role = discord.utils.get(member.guild.roles, id=verfrole)
            await member.add_roles(role)
            await mes.delete()
            await ctx.send("Verified", delete_after=5)
        else:
            await ctx.send(f"Hey, you need to check <#{verf}> to get in! It's important to read the rules, you know?", delete_after=15)

def setup(bot):
    bot.add_cog(User(bot))
