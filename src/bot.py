import random
import shelve
from io import BytesIO
from pathlib import Path
import discord
from discord import Game
from discord.ext.commands import Bot
import asyncio
import stocks
import charts
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
async def stock_candle(ctx, *args):
    if len(args) < 2:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.\nDo: %stockcandle ticker timeframe", color=discord.Color.red()))
        return
    await charts.chart(ctx, args[0], args[1], 'candle')

@client.command(name='stockline')
async def stock_line(ctx, *args):
    if len(args) < 2:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.\nDo: %stockline ticker timeframe", color=discord.Color.red()))
        return

    await charts.chart(ctx, args[0], args[1], 'line')

@client.command(name='stockrenko')
async def stock_renko(ctx, *args):
    if len(args) < 2:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.\nDo: %stockrenko ticker timeframe", color=discord.Color.red()))
        return

    await charts.chart(ctx, args[0], args[1], 'renko')

@client.command(name='stockpf')
async def stock_pf(ctx, *args):
    if len(args) < 2:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.\nDo: %stockpf ticker timeframe", color=discord.Color.red()))
        return

    await charts.chart(ctx, args[0], args[1], 'pf')

@client.command(name='stock')
async def stock_price(ctx, *args):
    if len(args) < 1:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.\nDo: %stock ticker", color=discord.Color.red()))
        return
    status, embed = await stocks.stock_price_today(ctx, args[0], False)
    await ctx.send(embed=embed)


@client.command(name='rs', aliases=['realtimestock', 'rstock'])
async def realtimestock(ctx, *args):
    if len(args) < 1:
        await ctx.channel.send(embed=discord.Embed(description="Invalid command format.\nDo: %rs ticker", color=discord.Color.red()))
        return
    await stocks.rs(ctx, args[0])

@client.command(name='losers')
async def losers(ctx):
    await stocks.movers(ctx, False)

@client.command(name='gainers')
async def gainers(ctx):
    await stocks.movers(ctx, True)

@client.command(name='secp')
async def sector_performance(ctx):
    await stocks.secp(ctx)




client.run(BOT_TOKEN)
