import discord
import discord.ext.commands.errors
import dotenv
import asyncio
from discord.ext import commands
import os
from pretty_help import PrettyHelp

Intents = discord.Intents.default()
Intents.members = True
Intents.messages = True
Intents.reactions = True
Intents.dm_messages = True

token = os.getenv('DISCORD_TOKEN')
description = "Commands for The Barkeeper"
bot = commands.Bot(command_prefix="^", intents=Intents, description=description, help_command=PrettyHelp())

modrole = 752158397255647252
ownerrole = 821756270826618910
processed = []

class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(brief="Average time it took to look up posts", description="Displays the average time it took the bot to look up and respond with the images it was tasked to search for")
    @commands.has_role(modrole)
    async def avgredditlookup(self, ctx):
        results = sum(processed) / len(processed)
        await ctx.send(f"The average time to look up reddit posts is **{results} seconds**")
        

    @bot.command(brief='Sends a message as the bot', description='Sends a message as the bot')
    @commands.has_role(ownerrole)
    async def sendmessage(self, ctx, channel: int, *, arg):
        cha = self.bot.get_channel(channel)
        print(f"User {ctx.message.author} sent {arg}")
        await cha.send(arg)

    @bot.command(brief="Bans the user", description="Bans the user")
    @commands.has_role(modrole)
    async def ban(self, ctx, user: discord.Member, *reason):
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

    @bot.command(brief="Unbans the user", description="Unbans the user")
    @commands.has_role(modrole)
    async def pardon(self, ctx, id: int):
        user = await self.bot.fetch_user(id)
        await ctx.guild.unban(user)
        await ctx.send(f"User <@!{id}> has been pardoned.")

    @bot.command(brief="Reacts with emotes to be used as votes", description="Thumbs up: Yes | Thumbs down: No | Fist: Abstain")
    @commands.has_role(modrole)
    async def modvote(self, ctx):
        await ctx.message.add_reaction("👍")
        await ctx.message.add_reaction("👎")
        await ctx.message.add_reaction("👊")

def setup(bot):
    bot.add_cog(Moderator(bot))