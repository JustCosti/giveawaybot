token = '' # Input your token here.

# Imports
import discord
import asyncio
import random
import logging
import json
import os
import string




# From imports
from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime, timedelta




# Put the channel you would like to log, when somone creates a giveaway ^^^
intents = discord.Intents.default()
client = commands.Bot(command_prefix = 'gw!' , case_insensitive = True , intents = intents)
client.remove_command('help')

# Commands

@client.command()
async def test(ctx):
    await ctx.send("Hello")
    
    
    
    
# Giveaway Command
@client.command(aliases = ['start , g'])
@commands.has_permissions(manage_guild = True)
async def giveaway(ctx):
    await ctx.send(embed=discord.Embed(color=discord.Color.green(), title = "Select the channel, you would like the giveaway to be in"))
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg1 = await client.wait_for('message', check = check, timeout=30.0)

        channel_converter = discord.ext.commands.TextChannelConverter()
        try:
            giveawaychannel = await channel_converter.convert(ctx, msg1.content)
        except commands.BadArgument:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "This channel doesn't exist, please try again"))

    except asyncio.TimeoutError:
        await ctx.send("You took to long, please try again!")
    if not giveawaychannel.permissions_for(ctx.guild.me).send_messages or  not giveawaychannel.permissions_for(ctx.guild.me).add_reactions:
        return await ctx.send(embed=discord.Embed(color=discord.Color.red(), description = f"Bot does not have correct permissions to send in: {giveawaychannel}\n **Permissions needed:** ``Add reactions | Send messages``"))

    await ctx.send(embed=discord.Embed(color=discord.Color.green(), title = "How many winners to the giveaway would you like?"))
    try:
        msg2 = await client.wait_for('message', check = check, timeout=30.0)
        try:
            winerscount = int(msg2.content)
        except ValueError:
            return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "You didn't specify a number of winners, please try again."))

    except asyncio.TimeoutError:
        await ctx.send("You took to long, please try again!")

    await ctx.send(embed=discord.Embed(color=discord.Color.green(), title = "Select an amount of time for the giveaway."))
    try:
        since = await client.wait_for('message', check = check, timeout=30.0)

    except asyncio.TimeoutError:
        await ctx.send("You took to long, please try again!")


    seconds = ("s", "sec", "secs", 'second', "seconds")
    minutes= ("m", "min", "mins", "minute", "minutes")
    hours= ("h", "hour", "hours")
    days = ("d", "day", "days")
    rawsince = since.content
    try:
        time = int(since.content.split(" ")[0])
    except ValueError:
        return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "You did not specify a unit of time, please try again."))
    since = since.content.split(" ")[1]
    if since.lower() in seconds:
        timewait = time
    elif since.lower() in minutes:
        timewait = time*60
    elif since.lower() in hours:
        timewait = time*3600
    elif since.lower() in days:
        timewait = time*86400
    elif since.lower() in weeks:
        timewait = time*604800
    else:
        return await ctx.send(embed=discord.Embed(color=discord.Color.red(), title = "You did not specify a unit of time, please try again."))
        
    prizeembed = discord.Embed(title = "What would you like the prize to be?" , color = discord.Color.green())
    await ctx.send(embed = prizeembed)
    try:
        msg4 = await client.wait_for('message', check = check, timeout=30.0)


    except asyncio.TimeoutError:
        await ctx.send("You took to long, please try again.")

    logembed = discord.Embed(title = "Giveaway Logged" , description = f"**Prize:** ``{msg4.content}``\n**Winners:** ``{winerscount}``\n**Channel:** {giveawaychannel.mention}\n**Host:** {ctx.author.mention}" , color = discord.Color.red())
    logembed.set_thumbnail(url = ctx.author.avatar_url)
    
    guild = client.get_guild() # Put your guild ID here!
    logchannel = guild.get_channel() # Put your channel, you would like to send giveaway logs to.
    await logchannel.send(embed = logembed)

    futuredate = datetime.utcnow() + timedelta(seconds=timewait)
    embed1 = discord.Embed(title=f"🎉GIVEAWAY🎉\n`{msg4.content}`", color = discord.Color.blue(), timestamp = futuredate, description=f'React with 🎉 to enter!\nEnd Date: {futuredate.strftime("%a, %b %d, %Y %I:%M %p")}\nHosted by: {ctx.author.mention}')
    
    embed1.set_footer(text=f"Giveaway will end")
    msg = await giveawaychannel.send(embed=embed1)
    await msg.add_reaction("🎉")
    await asyncio.sleep(timewait)
    message = await giveawaychannel.fetch_message(msg.id)
    for reaction in message.reactions:
        if str(reaction.emoji) == "🎉":
            users = await reaction.users().flatten()
            if len(users) == 1:
                return await msg.edit(embed=discord.Embed(title="Nobody has won"))

    winners = random.sample([user for user in users if not user.bot], k=winerscount)
    
    #await message.clear_reactions()
    winnerstosend = "\n".join([winner.mention for winner in winners])

    win = await ctx.send(embed = discord.Embed(title = "WINNER" , description = f"Congratulations {winnerstosend}, you have won **{msg4.content}**!" , color = discord.Color.blue()))
    bmessage = await message.channel.send(winnerstosend)
    await bmessage.delete(delay=1)
    
    
# Reroll command, used for chosing a new random winner in the giveaway
@client.command()
@commands.has_permissions(manage_guild = True)
async def reroll(ctx):
    async for message in ctx.channel.history(limit=100 , oldest_first = False):
        if message.author.id == client.user.id and message.embeds:
            reroll = await ctx.fetch_message(message.id)
            users = await reroll.reactions[0].users().flatten()
            users.pop(users.index(client.user))
            winner = random.choice(users)
            await ctx.send(f"The new winner is {winner.mention}")
            break
    else:
        await ctx.send("No giveaways going on in this channel.")
    
@client.command()
async def ping(ctx):
    ping = client.latency
    await ctx.send(f"The bot's ping is: ``{round(ping * 1000)}ms``")
    
    
# Events
@client.event
async def on_ready():

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
client.run(token)
