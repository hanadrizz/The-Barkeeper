import os
import apraw
import discord
import discord.ext.commands.errors
from discord.ext import commands
from mediawiki import MediaWiki
import configparser
from tinydb import TinyDB, Query
from tinydb.operations import set
from pretty_help import PrettyHelp

# DATABASE INITIALIZATION

database = TinyDB("database.json", sort_keys=True, indent=4, separators=(',', ': '))
data = Query()

config = configparser.ConfigParser()
config.read('db.ini')

#SETTING UP THE DISCORD AND REDDIT CLIENTS
clientid = config['reddit']['client_id']
clientsecret = config['reddit']['client_secret']
useragent = config['reddit']['user_agent']
username = config['reddit']['username']
password = config['reddit']['password']

guildid = config.getint("discord", "guildid")
guild = config['discord']['guild']
token = config['discord']['token']

# MAKING SURE ITS SET UP PROPERLY
print('Configuration:')

print(f'ID: {clientid}')
print(f'Client Secret: {clientsecret}')
print(f'Useragent: {useragent}')
print(f'Reddit username: {username}')

# REDDIT INITIALIZATION
reddit = apraw.Reddit(client_id = clientid, client_secret = clientsecret, user_agent=useragent, username = username, password=password)

# FILTERS
bannedsubs = config["filter"]["bannedsubs"].split()
wordfilter = config["filter"]["filter"].split()


# SETTING UP ALL THE VALUES AND VARIABLES
# SEE THE COMPILE GUIDE FOR MORE

general = config.getint("setup", "general")
logs = config.getint("setup", "logs")
pinboard = config.getint("setup", "pinboard")
verf = config.getint("setup", "verf")
moggers = config.getint("setup", "moggers")
memberrole = config.getint("setup", "memberrole")
reactionnumber = config.getint("setup", "reactionlimit")
rules = config.getint("setup", "rules")

# INTENTS

Intents = discord.Intents.default()
Intents.members = True
Intents.messages = True
Intents.reactions = True
Intents.dm_messages = True

output = ""
description = "Commands for the bot"
bot = commands.Bot(command_prefix="?", intents=Intents, description=description, help_command=PrettyHelp())


# RELOADING THE COGS SO YOU CAN EDIT WITHOUT HAVING TO SHUT OFF THE BOT

@bot.command(brief="Reloads the bot", description="Reloads the bot", hidden=True)
@commands.is_owner()
async def reload(ctx):
    await ctx.send("Reloading...")
    bot.unload_extension("cogs.usercommands")
    bot.unload_extension("cogs.fun")
    bot.unload_extension("cogs.economy")
    bot.unload_extension("cogs.mod")

    bot.load_extension("cogs.usercommands")
    bot.load_extension("cogs.fun")
    bot.load_extension("cogs.economy")
    bot.load_extension("cogs.mod")
    await ctx.send("Reloaded.")
    print("#"*30)

# EVENTS

#SLUR FILTER DETECITION
@bot.event
async def on_message(message):
    ctx = message.channel
    if message.author != bot.user:
        if any(word in message.content for word in wordfilter):
            await message.delete()
            await ctx.send("Hey! You can't say that!", delete_after=5)
        else:
            pass
    else:
        pass

    await bot.process_commands(message)
    
#WELCOME MESSAGE AND ADDING THE MEMBER ROLE + GIVING THEM A PROFILE IN THE DATABASE
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(general)
    await channel.send(f"Welcome {member.mention} to the server! You can get roles by pinging Roleypoly! Be sure to read the rules over at <#{rules}> aswell! Have a nice day!")
    role = discord.utils.get(member.guild.roles, id=memberrole)
    await member.add_roles(role)
    print(f"{member} joined.")
    check = database.search(data.userid == member.id)
    if check == []:
        database.insert({"userid": member.id, "money": 0, "pickaxetier": 0})

#PINBOARD SET UP
@bot.event
async def on_reaction_add(reaction, user):
    if hasattr(reaction.emoji, "id"):
        if reaction.emoji.id == moggers:
            if reaction.count >= reactionnumber: # HOW MANY IS NEEDED TO PIN
                if reaction.message.pinned == False:
                    try:
                        await reaction.message.pin()
                    except:
                        await reaction.message.channel.send("Maximum number of pins reached (50)")

                    ctx = reaction.message.channel # PINBOARD MESSAGE 
                    message = reaction.message
                    user = message.author
                    avatar = user.avatar_url
                    pin = discord.Embed(color=0x9e85cc)
                    pin.set_author(name=message.author.name, icon_url=avatar)
                    pin.add_field(name="Channel:",value=message.channel.name, inline=False)
                    if message.content:
                        pin.add_field(name="Contents:", value=message.content, inline=False)
                    if not message.attachments:
                        pass
                    else:
                        image = message.attachments[0]
                        img = image.url
                        print(img)
                        pin.set_image(url=img)
                    board = bot.get_channel(pinboard)
                    await board.send(f"Message pinned from <#{ctx.id}>", embed=pin)

# ADDING ALL EMPTY USERS TO THE DATABASE WHEN IT STARTS
@bot.event
async def on_ready():
    print(f'Bot has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for rulebreakers, beware!")) # STATUS MESSAGE
    if os.stat("database.json").st_size == 0:
        server = bot.get_guild(guildid)
        servermembers = server.members
        for member in servermembers:
            database.insert({"userid": member.id, "money": 0, "pickaxetier": 0})
    
# LOGS
@bot.event
async def on_message_delete(message):
    if not message.author.bot:
        verify = bot.get_channel(verf)
        if message.channel != verify:
            channel = bot.get_channel(logs)
            deletedmessage = discord.Embed(title=f"Message deleted.", color=0x9e85cc)
            author = message.author.name
            content = message.content
            user = message.author
            avatar = user.avatar_url
            deletedmessage.set_author(name=message.author.name, icon_url=avatar)
            deletedmessage.add_field(name="Author:", value=author, inline=False)
            deletedmessage.add_field(name="Channel:", value=message.channel.name, inline=False)
            deletedmessage.add_field(name="Contents:", value=content, inline=False)
            await channel.send(embed=deletedmessage)
            print(f"{message.author.name} deleted a message")

# ERROR HANDLING

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(error)


bot.load_extension('cogs.usercommands')
bot.load_extension('cogs.economy')
bot.load_extension('cogs.fun')
bot.load_extension('cogs.mod')

bot.run(token)
