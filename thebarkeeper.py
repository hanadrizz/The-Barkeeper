import apraw
import os, random
import discord
import discord.ext.commands.errors
from discord.guild import Guild
from discord.message import Attachment
import dotenv
import asyncio
from discord.ext import commands
from mediawiki import MediaWiki
import textwrap
import time
import datetime
import configparser
from tinydb import TinyDB, Query
from tinydb.operations import set
import typing

database = TinyDB("database.json", sort_keys=True, indent=4, separators=(',', ': '))
data = Query()

def getPickaxeLevel(userid):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    pickaxelevel = record["pickaxetier"]
    return pickaxelevel

def changePickaxeLevel(userid, level):
    database.upsert({"pickaxetier": level}, data.userid == userid)

def getUserMoney(userid):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    return money

def subtractMoney(userid, amount: int):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    money = money - amount
    database.upsert({"money":money}, data.userid == userid)

def addMoney(userid, amount):
    datasearch = database.search(data.userid == userid)
    record = datasearch[0]
    money = record["money"]
    money = money + amount
    database.upsert({"money":money}, data.userid == userid)

async def denied(ctx, avatar):
    x = discord.Embed(title="Shop", color=0xff0000, description = f"Sorry {ctx.author.mention}, I can't give credit! Come back when you're a little... mmm... richer")
    x.set_author(name=ctx.author.name, icon_url=avatar)
    x.set_image(url="https://cdn.discordapp.com/attachments/821123717223415809/823315107261055006/morshu.gif")
    await ctx.send(embed=x)

async def mining(ctx, num1, userid):
    x = random.randint(1, 100)
    num2 = 100 - num1
    if x <= num2:
        await ctx.send("Too bad, you only found rocks and scraps!")
    else:
        y = random.randint(25, 200)
        await ctx.send(f"Woah, you found a gold ore! It's worth {y} :coin:! Lucky you!")
        addMoney(userid, y)
        
    
pickaxetiers = ["wood","stone","copper","iron","steel","gold","diamond","platinum"]
pickaxecost = {"wood": 0,"stone": 50,"copper": 150,"iron": 500,"steel": 1500,"gold": 3000,"diamond": 5000,"platinum": 10000}
miningchances = {1 : 35, 2 : 45, 3 : 50, 4 : 60, 5 : 70, 6 : 80, 7 : 90, 8 : 95}


imagefolder = "images\\"
pximg = "i.pximg.net"

config = configparser.ConfigParser()
config.read('db.ini')

clientid = config['reddit']['client_id']
clientsecret = config['reddit']['client_secret']
useragent = config['reddit']['user_agent']
username = config['reddit']['username']
password = config['reddit']['password']

print('Configuration:')

print(f'ID: {clientid}')
print(f'Client Secret: {clientsecret}')
print(f'Useragent: {useragent}')
print(f'Reddit username: {username}')

dotenv.load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = os.getenv("DISCORD_GUILD")

reddit = apraw.Reddit(client_id = clientid, client_secret = clientsecret, user_agent=useragent, username = username, password=password)
memefolder = os.getenv("memefolder")

bannedsubs = ["urinalpics", "urinalshitters", "urinalpoop", "poo", "kropotkistan", "femboy", "trans", "feemagers"]
bannedtags = ["ribbon_bondage", "scat", "no_bra","panties", "pantsu", "pantyshot", "bikini", "swimsuit", "feet", "toes", "ass", "povfeet", "bikini_top", "licking", "saliva", "micro_bikini", "cameltoe"]
wordfilter = config["filter"]["filter"].split()

# USERS AND CHANNELS

bottesting = 821087946941792258
general = 752157598232477789
memechannel = 752158323574308934
logs = 821333966173765643
pinboard = 821796457711534120
boorulogs = 822132304050389083

modrole = 752158397255647252
ownerrole = 821756270826618910

# EMOJI

moggers = 821358739336593429

# INTENTS

Intents = discord.Intents.default()
Intents.members = True
Intents.messages = True
Intents.reactions = True
Intents.dm_messages = True

output = ""

bot = commands.Bot(command_prefix="^", intents=Intents)

# MODERATOR COMMANDS

processed = []

@bot.command()
@commands.has_role(modrole)
async def avgredditlookup(ctx):
    results = sum(processed) / len(processed)
    await ctx.send(f"The average time to look up reddit posts is **{results} seconds**")
    

@bot.command()
@commands.has_role(ownerrole)
async def sendmessage(ctx, channel: int, *, arg):
    cha = bot.get_channel(channel)
    print(f"User {ctx.message.author} sent {arg}")
    await cha.send(arg)

@bot.command()
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
                print(f"{user} banned")

@bot.command()
@commands.has_role(modrole)
async def pardon(ctx, id: int):
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.send(f"User <@!{id}> has been pardoned.")

@bot.command()
@commands.has_role(modrole)
async def modvote(ctx):
    await ctx.message.add_reaction("👍")
    await ctx.message.add_reaction("👎")
    await ctx.message.add_reaction("👊")

@bot.command()
@commands.has_role(ownerrole)
async def memberlist(ctx):
    if not ctx.author.bot:
        server_members = ctx.guild.members
        
            
# ECONOMY

@bot.command()
async def balance(ctx):
    userid = ctx.author.id
    balance = getUserMoney(userid)
    await ctx.send(f"Your balance is {balance} :coin:")


@bot.command()
async def shop(ctx, arg="help", *, item=""):
    user = ctx.author
    userid = user.id
    avatar = user.avatar_url
    image = imagefolder + "morshu.gif"

    if "list" in arg:
        shop=discord.Embed(title="Shop", description="The one destination for all your needs!", color=0xff0000)
        shop.set_author(name=ctx.author.name, icon_url=avatar)
        pickaxelevel = getPickaxeLevel(userid)
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
        pickaxelevel = getPickaxeLevel(userid)
        money = getUserMoney(userid)
        items = ['wood', 'stone', 'copper', 'iron', "steel", 'gold', 'diamond', 'platinum']
        for i in item.lower().split():
          if i in items:
            Newpickaxelevel = items.index(i) + 1
            cost = dict.get(pickaxecost, i)
            if money < cost:
              await denied(ctx, avatar)
            elif pickaxelevel >= Newpickaxelevel:
              await ctx.send("You already own this pickaxe, sorry!")
            else:
              changePickaxeLevel(userid, Newpickaxelevel)
              subtractMoney(userid, cost)
              await ctx.send(f"You have successfully gotten a {i} pickaxe! Happy mining!")
    else:
        await ctx.send("Invalid command. ``shop buy [item]`` to buy things and ``shop list`` to see list.")  
            
#@commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
@bot.command()
async def mine(ctx):
    user = ctx.author
    userid = user.id
    pickaxelevel = getPickaxeLevel(userid)
    
    if pickaxelevel == 0:
        await ctx.send(f"You don't own a pickaxe yet! You need to buy it from the shop! Check our collection at ```^shop list```")

    elif pickaxelevel > 0:
        await mining(ctx, miningchances[pickaxelevel], userid)

        
    
# USER COMMANDS    

@bot.command()
async def complementarybread(ctx):
    user = ctx.message.author
    image = imagefolder + "complementarybread.png"
    await user.send("Hey!", file=discord.File(image))
    await ctx.send("Psst... come with me down this alley!")
    print(f"Welcome to the bread bank, {user}")


@bot.command()
async def license(ctx):
    with open("LICENSE", "r") as license:
        notice = license.read()
        notice = notice + "\n\nRepository can be found at <https://github.com/hanadrizz/The-Barkeeper>"
        await ctx.send(notice)

@bot.command()
async def booru(ctx):
    await ctx.send("Undergoing maintenance. Bully Maria in the meantime.") 

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! **{bot.latency}ms**")
    print(f"{ctx.message.author.name} pinged")

wikipage = MediaWiki()
@bot.command()
async def wiki(ctx, *, page):
    print(f"{ctx.message.author.name} requested {page}")
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

@bot.command()
async def redditsearch(ctx, sub):
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

@bot.command()
async def avatar(ctx, *,  avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    await ctx.send(userAvatarUrl)
    print(f"{ctx.message.author.name} looked up {avamember}'s avatar.")
    
@bot.command()
async def sus(ctx):
    await ctx.send("sus")
    print(f"{ctx.message.author.name} sus")

@bot.command()
async def jamaal(ctx):
    await ctx.send("man\nhttps://cdn.discordapp.com/attachments/821123717223415809/821642340359733258/f4xz3iryogm61.jpg")
    print(f"{ctx.message.author.name} jamaal")

@bot.command()
async def hug(ctx, arg : discord.Member=None):
    await ctx.send(f"<@{ctx.message.author.id}> is hugging <@{arg.id}>! :people_hugging:")
    
@bot.command()
async def sex(ctx):
    await ctx.send("thats what i have with your mom lmao 🔥🔥🔥🔥")
    print(f"{ctx.message.author.name} sex")

# EVENTS

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
    

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(general)
    # await channel.send(f"Welcome {member.mention} to The Bar! You can get roles by pinging Roleypoly! Be sure to read the rules over at <#755155329502675066> aswell! Have a nice day!")
    role = discord.utils.get(member.guild.roles, id=752163420962422795)
    await member.add_roles(role)
    print(f"{member} joined.")
    check = database.search(data.userid == member.id)
    if check == []:
        database.insert({"userid": member.id, "money": 0})

@bot.event
async def on_reaction_add(reaction, user):
    if hasattr(reaction.emoji, "id"):
        if reaction.emoji.id == moggers:
            if reaction.count >= 3:
                if reaction.message.pinned == False:
                    try:
                        await reaction.message.pin()
                    except:
                        await reaction.message.channel.send("Maximum number of pins reached (50)")

                    ctx = reaction.message.channel
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

@bot.event
async def on_ready():
    print(f'Bot has connected to Discord!')
    

@bot.event
async def on_message_delete(message):
    if not message.author.bot:
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



