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