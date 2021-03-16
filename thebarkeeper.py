import apraw
import os, random
import discord
from discord import file
from discord.enums import _is_descriptor
from discord.ext.commands.errors import BadInviteArgument
import dotenv
import asyncio
from discord.ext import commands
import wikipedia
import textwrap
import time

dotenv.load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = os.getenv("DISCORD_GUILD")

clientid = os.getenv("client_id")
clientsecret = os.getenv("client_secret")
useragent = os.getenv('user_agent')
user_name = os.getenv("username")
pass_word = os.getenv('password')

#ya aint getting my detaisl bruh
reddit = apraw.Reddit(client_id = "", client_secret = "", user_agent=useragent, username = "", password="")
memefolder = os.getenv("memefolder")

# Easy to use list, lol
bannedsubs = ["poo", "kropotkistan"]


# USERS AND CHANNELS

bottesting = 821087946941792258
general = 752157598232477789
memechannel = 752158323574308934
logs = 821333966173765643

modrole = 752158397255647252

Intents = discord.Intents.default()
Intents.members = True
Intents.messages = True

output = ""

bot = commands.Bot(command_prefix="^", intents=Intents)

# MODERATOR COMMANDS

# Sends a message as The Barkeeper
@bot.command(pass_context=True)
@commands.has_role(modrole)
async def sendmessage(ctx, channel: int, *, arg):
    print(ctx)
    print(channel)
    cha = bot.get_channel(channel)
    print(arg)
    await cha.send(arg)

# Bans user
@bot.command(pass_context=True)
@commands.has_role(modrole)
async def ban(ctx, user: discord.Member, *reason):
    if user == None or user == ctx.message.author:
        await ctx.send("You can't ban yourself.")
    else:
        if reason == None:
            await ctx.send("You need a reason.")
        else:
            role = discord.utils.get(ctx.guild.roles, name="Admins")
            if role in user.roles:
                print("b")
                await ctx.send("Hey, you can't do that!")
            if role not in user.roles:
                print("a")
                reason = " ".join(reason[:])
                banmessage = f"You have been banned from {ctx.guild.name} for \n{reason}"
                await user.send(banmessage)
                await ctx.guild.ban(user, reason=reason)
                await ctx.channel.send(f"Banned {user}")

# Unbans user
@bot.command(pass_context=True)
@commands.has_role(modrole)
async def pardon(ctx, id: int):
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.send(f"User <@!{id}> has been pardoned.")


# USER COMMANDS    

# Grabs the summary of any wikipedia page sent
@bot.command()
async def wiki(ctx, *, page):
    try:
        summary = wikipedia.summary(page,  auto_suggest=False)
        summary_list = textwrap.wrap(summary, 2000, break_long_words=False)
        for i in summary_list:
            await ctx.channel.send(i)
    except Exception as inst:
        output = "Error raised."
        await ctx.send(f"{output}\n{inst}")



# @bot.command()
# async def meme(ctx):
#     meme = random.choice(os.listdir(memefolder))
#     memelocation = f"{memefolder}\\{meme}"
#     print(memelocation)
#     filestats = os.stat(memelocation)
#     filesize = filestats.st_size
#     print(filesize)
#     if filesize > 8388608:
#         ctx.send("The meme randomly selected was too large.")
#     else:
#         area=ctx.message.channel
#         await ctx.send(file=discord.File(memelocation))

# Posts a random image or GIF in chat, with any subreddit as a parameter. 18+ is banned
@bot.command()
async def redditsearch(ctx, sub):
    start_time = time.time()
    listing = []
    subreddit = await reddit.subreddit(sub)
    print(subreddit.subreddit_type)
    try:
        if sub.lower() in bannedsubs:
            await ctx.send("Banned subreddit.")
            return
        else:
            if subreddit.over18 == True:
                await ctx.send("No NSFW subreddits.")
                return
            else:
                async for submission in subreddit.hot(limit=100):
                    if submission.spoiler == True:
                        pass
                    else:
                        if submission.over_18 == True:
                            pass
                        else:
                            if submission.url.endswith("jpg") or submission.url.endswith("jpeg") or submission.url.endswith("png") or submission.url.endswith("gifv"):
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
            await ctx.send(f"---- Took %s seconds to lookup ----" % (end_time - start_time))
    except AttributeError:
        await ctx.send("Subreddit is most likely banned or restricted.")

@bot.command()
async def avatar(ctx, *,  avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    await ctx.send(userAvatarUrl)
    
    #dont know about you but that crewman lookin sus
@bot.command()
async def sus(ctx):
    await ctx.send("sus")
    
    # Just as a "I'm ready"
@bot.event
async def on_ready():
    print(f'Bot has connected to Discord!')
    
    #lmaoooo
@bot.command()
async def sex(ctx):
    await ctx.send("thats what i have with your mom lmao 🔥🔥🔥🔥")

# Welcome message and gives member role
@bot.event
async def on_member_join(member):
    print(member)
    channel = bot.get_channel(general)
    await channel.send(f"Welcome {member.mention} to The Bar! You can get roles by pinging Roleypoly! Be sure to read the rules over at <#755155329502675066> aswell! Have a nice day!")
    role = discord.utils.get(member.guild.roles, id=752163420962422795)
    await member.add_roles(role)

# Logs deleted messages to logging channel
@bot.event
async def on_message_delete(message):
    channel = bot.get_channel(logs)
    deletedmessage = discord.Embed(title=f"Message deleted.")
    author = message.author.name
    content = message.content
    user = message.author
    avatar = user.avatar_url
    deletedmessage.set_author(name=message.author.name, icon_url=avatar)
    deletedmessage.add_field(name="Author:", value=author, inline=False)
    deletedmessage.add_field(name="Contents:", value=content, inline=False)
    await channel.send(embed=deletedmessage)

# ERROR HANDLING

@avatar.error
async def avatar_error(ctx, error):
    await ctx.send(f"^{ctx.command.name} was invoked incorrectly. Format is ``^avatar [user]``.")

@wiki.error
async def wiki_error(ctx, inst):
    await ctx.send(f'^{ctx.command.name} was invoked incorrectly. Error: {inst} Correct formatting of this command is ^wiki "[page]".')

@redditsearch.error
async def redditsearch_error(ctx, inst):
    await ctx.send(f"Exception raised. \n\n{inst}")

bot.run(token)

