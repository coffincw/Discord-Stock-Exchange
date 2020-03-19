import random
import shelve
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
import stocks
import os
import time

BOT_PREFIX = "%"
BOT_TOKEN = os.environ.get('DSE_BOT_TOKEN')
BOT_ROLE = "bots"

client = Bot(command_prefix=BOT_PREFIX, case_insensitive=True)
client.remove_command('help')

@client.event
async def on_ready():
    """This function runs when the bot is started
    """
    game = discord.Game(name = 'the market')
    await client.change_presence(activity=game)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#101440
    
@client.event
async def on_message(message):
    author = message.author
    try:
        if message.guild.id == 387465995176116224:
            data = shelve.open('server-data/stem-discord-data')
            if (BOT_ROLE not in [role.name.lower() for role in author.roles]):
                if str(author) in data:
                    data[str(author)] += 1
                else:
                    data[str(author)] = 1
            data['Total Messages'] += 1
            data.close()
    except:
        pass
    await client.process_commands(message)

# vvv GENERAL COMMANDS vvv

def get_top_10(data):
    top_10 = ''
    number = 0
    # sort dictionary and only take top ten
    for user in sorted(data, key=data.get, reverse=True):
        if number == 0:
            number+= 1
            continue
        elif number < 11:
            top_10 += '**' + str(number) + '**. ' + user + ' - ' + str(data[user]) + '\n'
        else:
            break
        number += 1
    top_10 += '*Total Messages*: ' + str(data['Total Messages'])
    return top_10

## vvv STOCK COMMANDS vvv

@client.command(name='stockcandle')
async def stock_candle(ctx, ticker, timeframe):
    if len(ticker) == 0 or len(timeframe) == 0:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.  Do: $stockcandle ticker d|m|6m|y|ytd|5y|max", color=discord.Color.red()))
        return

    await stocks.chart(ctx, ticker, timeframe, 'candle')

@client.command(name='stockline')
async def stock_line(ctx, ticker, timeframe):
    if len(ticker) == 0 or len(timeframe) == 0:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.  Do: $stockline ticker d|m|6m|y|ytd|5y|max", color=discord.Color.red()))
        return

    await stocks.chart(ctx, ticker, timeframe, 'line')

@client.command(name='stock')
async def stock_price(ctx, ticker):
    await stocks.stock_price_today(ctx, ticker)


client.run(BOT_TOKEN)
