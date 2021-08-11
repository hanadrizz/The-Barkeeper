import configparser
import discord
import discord.ext.commands.errors
from discord.ext import commands
import os
from pretty_help import PrettyHelp
import configparser

Intents = discord.Intents.default()
Intents.members = True
Intents.messages = True
Intents.reactions = True
Intents.dm_messages = True

config = configparser.ConfigParser()
config.read("db.ini")

modrole = config.getint("setup", "modrole")
ownerrole = config.getint("setup", "ownerrole")
processed = []


class Moderator(commands.Cog):
    """Commands for moderating purposes"""

    def __init__(self, bot):
        self.bot = bot

    # ITS JUST SOME INTERESTING STATISTICS
    # OF THE AVERAGE TIME IT TAKES FOR THE BOT
    # TO PROCESS AND SEND IMAGES THROUGH THE
    # ?REDDITSEARCH COMMAND
    @commands.command(
        brief="Average time it took to look up posts",
        description="Displays the average time it took the bot to look up and respond with the images it was tasked to search for",
    )
    @commands.has_role(modrole)
    async def avgredditlookup(self, ctx):
        results = sum(processed) / len(processed)
        await ctx.send(
            f"The average time to look up reddit posts is **{results} seconds**"
        )

    # THIS ONE IS FOR SENDING A MESSAGE AS THE BOT
    # CHANNEL IS THE ID FOR THE CHANNEL TO SEND IN
    # NO " " NEEDED
    @commands.command(
        brief="Sends a message as the bot", description="Sends a message as the bot"
    )
    @commands.has_role(ownerrole)
    async def sendmessage(self, ctx, channel: int, *, arg):
        cha = self.bot.get_channel(channel)
        print(f"User {ctx.message.author} sent {arg}")
        await cha.send(arg)

    # ANY MOD WITH THE BAN MEMBERS PERMISSION
    # USES THIS TO BAN THE USER
    # THE USER IS DM'D THE BAN REASON
    @commands.command(brief="Bans the user", description="Bans the user")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *reason):
        try:
            if user == None or user == ctx.message.author:
                await ctx.send("You can't ban yourself.")
            elif reason == None:
                await ctx.send("You need a reason.")
            else:
                reason = " ".join(reason[:])
                banmessage = (
                    f"You have been banned from {ctx.guild.name} for: \n\n{reason}"
                )
                await ctx.guild.ban(user, reason=reason)
                await user.send(banmessage)
                await ctx.channel.send(f"Banned {user}")
                print(f"{user} banned")
        except Exception as exc:
            if exc.code == 50013:
                await ctx.send("You don't have the permission to ban this user.")
            else:
                await ctx.send(f"An exception occured.\n\n{exc}")

    # REVERSES A BAN ON A USER
    # REQUIRES AN ID
    @commands.command(brief="Unbans the user", description="Unbans the user")
    @commands.has_permissions(ban_members=True)
    async def pardon(self, ctx, id: int):
        try:
            user = await self.bot.fetch_user(id)
            await ctx.guild.unban(user)
            await ctx.send(f"User <@!{id}> has been pardoned.")
        except Exception as exc:
            if exc.code == 50013:
                await ctx.send("You don't have the permission to unban this user.")
            else:
                await ctx.send(
                    "An error occured. Remember to input the *id* of the target."
                )

    # KICKS A USER INSTEAD OF BANNING
    # EVERYTHING ELSE IS THE SAME
    # WITH THE BAN COMMAND
    @commands.command(brief="Kicks the user", description="Kicks the user")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *reason):
        try:
            if user == None or user == ctx.message.author:
                await ctx.send("You can't kick yourself.")
            elif reason == None:
                await ctx.send("You need a reason.")
            else:
                reason = " ".join(reason[:])
                banmessage = (
                    f"You have been kicked from {ctx.guild.name} for: \n\n{reason}"
                )
                await ctx.guild.ban(user, reason=reason)
                await user.send(banmessage)
                await ctx.channel.send(f"Banned {user}")
                print(f"{user} banned")
        except Exception as exc:
            if exc.code == 50013:
                await ctx.send("You don't have the permission to kick this user.")

    # USEFUL FOR MOD VOTE STUFF
    @commands.command(
        brief="Reacts with emotes to be used as votes",
        description="Thumbs up: Yes | Thumbs down: No | Fist: Abstain",
    )
    @commands.has_permissions(manage_messages=True)
    async def modvote(self, ctx):
        await ctx.message.add_reaction("👍")
        await ctx.message.add_reaction("👎")
        await ctx.message.add_reaction("👊")


def setup(bot):
    bot.add_cog(Moderator(bot))
