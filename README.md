# The-Barkeeper

![GNU GPLv3](https://img.shields.io/badge/license-GNU%20GPLv3-green)
![Python Version](https://img.shields.io/badge/python-v3.9-blue)
![Discord](https://img.shields.io/discord/752157598232477786)

Fun exercise in making a bot. Personalized for my own server at: https://discord.gg/XGRzEhXAug
This bot is not adjusted for simple download and use.

todo:
comment it all, im bad at that :sunglasses:

# COMPILE GUIDE

This bot isn't really meant for easy distribution, but its not too hard to make it work for your server.
You just need some python knowledge, access to the discord API and own the server
You have to have Python, Pip and Python virtual environments instaled before this.

First, download all the files and put them in a folder.
Then create a file called db.ini
In this file, paste this in:

    [reddit]
    
    client_id=
    client_secret=
    user_agent=
    username=
    password=
    
    [discord]
    guildid =
    guild = 
    token =
    
    [filter]
    filter = 
    bannedsubs =
    
    [setup]
    
    general =
    logs =
    pinboard =
    verf =
    verfrole = 
    memberrole =
    modrole =
    ownerrole =
    moggers =
    reactionlimit =
    minecraftip =
    rules =

On the reddit part of this file, get a Reddit API application and paste in, as well as logging in on an account
Its safe to use your own, but it doesn't matter. It only looks for images and stuff, nothing else
In ths discord part, paste the ID for your server (use developer mode), in guildid, the name of your server in guild, and most importantly, your bot's Bot Token you have gotten from the Discord Developer API

On filter, you have to just seperate the words with spaces, but in filter, add all the words you want filtered,
and on banned subs, all the subs you dont want users to check

Setup is a lot more trickier, all of these values is an ID, so be sure to use devmode
general is for your general channel, the bot will announce new entrants here
logs is for the logging channel, here the bot will put all deleted messages
pinboard is the channel the bot will post the messages it pins in here
verf is the channel you want users to post the ?verify command in
verfrole is the role you want to assign users when they are verified
memberrole is the members role, ID, not name
ownerrole and modrole is the owners and moderators roles, get the IDs, not name
moggers is the *emote* you want users to use when they are trying to get a message pinned
reactionlimit is a number, how many reactions you want users to reach before a message is pinned
minecraftip is the numerical ip to a minecraft server
rules is for the rules channel, this is to point users to that channel when they're welcomed.

And then when you have filled all of these in, just open a console, and then type

    python3 -m venv venv
When that has finished, it depends on which operating system you use
If you're on Linux, do 

    source ./venv/bin/activate
If you're on Windows, do

    venv/Scripts/activate

Then you have to do

    pip install -r requirements.txt

Now, you're ready to run the bot, do 
python3 thebarkeeper.py

If you've done everything right, it should run just fine.
If you have any questions, tips, help, or any of the sort, just open a ticket and I'll come to your assistance.




# Prefix
Prefix is ?

# Commands
Moderator commands | Output
------------ | -------------
ban [user] [reason] | Bans the specified user, and dms the user
kick [user] [reason] | Kicks the user with the specified reason
pardon [user] | Unbans the specified user
sendmessage [channel id] [message] | Sends a message in the specified channel as the bot. Message is anything after the ID
modvote | The bot reacts with three emotes to the command message, a thumbs up, a thumbs down, and a fist. These represents "Yay", "Nay", "Abstain"
avgredditlookup | After a couple redditsearch commands has been performed, this command outputs the average amount of time it took to find and post images.

Economy commands | Output
------------ | -------------
balance | Displays the user's balance
bal | See ?balance
leaderboard | Displays the top 5 richest users on the server
mine | Roll for a chance to get money or nothing. Chances depend on which pickaxe you own
shop list | Shows a list of items you can buy in the shop
shop buy [item] | Buys the item if you have enough
slots [amount] | Gamble for the set amount

User commands | Output
------------ | -------------
  avatar [user] | Responds with the specified users' avatar        
  help | Displays a help message
  wiki [page] | Responds with the specified pages' summary and a link
  license | Outputs the license and a link to this repository
  hug [user] | Responds with "[author] is hugging [user]! :people_hugging:"
  redditsearch [subreddit] | Looks for images in the specified subreddit, shuffles and picks one image, and posts it in the channel
  ping | Responds with the latency of the bot vs receiving commands
  minecraft | Shows you if the server is online and how many players are on
  
  Fun commands | Output
------------ | -------------
  wikowo [page] | same as wiki, but owofied
  owo [text] | Owofies a text, nyaaa
  jamaal | Responds with a picture of a cow stuck in a fence with subtitle "jamaal"    
  sex | Responds with "thats what i have with your mom lmao :fire::fire::fire::fire:"
  sus | Responds with "sus"
  rps [move] | You can't win at "Rock Paper Scissors"
  complementarybread | Pun on the word "compliment" and the complementary bread you receive at resturants. The bot sends you a private message with an image of a bread with the caption "You're cute."


  
