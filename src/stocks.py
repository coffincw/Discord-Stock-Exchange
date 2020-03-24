import discord
import asyncio
import os
import time
import datetime
from finnhub import client as Finnhub # api docs: https://finnhub.io/docs/api
import requests

FINNHUB_API_TOKEN = os.environ.get('FINNHUB_API_TOKEN')
FINNHUB_RS_API_TOKEN = os.environ.get('FINNHUB_API_TOKEN_4')
finnhub_client = Finnhub.Client(api_key=FINNHUB_API_TOKEN)
finnhub_rs_client = Finnhub.Client(api_key=FINNHUB_RS_API_TOKEN)


async def rs(ctx, ticker):
    """Sends the stock_price_today() embedded 
    message and updates it every minute for 5
    minutes.

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        context of the command
    ticker : string
        stock ticker (ex. AAPL, MSFT, TSLA, ^DJI, BTCUSDT)

    """
    status, embed = await stock_price_today(ctx, ticker, True)
    message = await ctx.send(embed=embed)
    if status != 'ok': # if not okay then don't edit
            return
    
    iterations = 0
    while iterations < 5:
        await asyncio.sleep(60)
        if iterations == 4: # last iteration
            status, embed = await stock_price_today(ctx, ticker, False)
        else:
            status, embed = await stock_price_today(ctx, ticker, True)
        await message.edit(embed=embed)
        
        iterations += 1

async def stock_price_today(ctx, ticker, is_live):
    """Called by stocK_price() in bot.py, returns
    the current price, percent change, and price
    change for the specified ticker

    Parameters
    ----------
    ctx : discord.ext.commands.Context
        context of the command
    ticker : string
        stock ticker (ex. AAPL, MSFT, TSLA, ^DJI, BTCUSDT)

    """

    # for indexes 'stocks' needs to be 'index'
    quote, decimal_format = await get_finnhub_quote(ticker.upper(), finnhub_client)
    if quote['t'] == 0:
        embed=discord.Embed(description='Invalid Ticker!', color=discord.Color.dark_red())
        return 'not ok', embed
    current_price = quote["c"]
    price_change = current_price - quote["pc"]
    percent_change = ((current_price / quote["pc"])-1) * 100
    
    ccp, cpc, cpercentc, color = await get_string_change(current_price, price_change, percent_change, decimal_format)

    
    embedded_message = discord.Embed(
        # format with appropriate ','
        description=ticker.upper() + " Price: " + ccp + " USD\nPrice Change: " + cpc + " (" + cpercentc + ")", 
        color=color
        )
    live_addition = 'LIVE a' if is_live else 'A'
    embedded_message.set_footer(text=live_addition + 's of ' + str(time.ctime(time.time())) + ' EST')
    embed=embedded_message
    return 'ok', embed

async def movers(ctx, is_gainers):
    if is_gainers:
        title = 'Top Stock Gainers Today'
        color = discord.Color.green()
        movers_data = requests.get('https://financialmodelingprep.com/api/v3/stock/gainers').json()['mostGainerStock']
    else:
        title = 'Top Stock Losers Today'
        color = discord.Color.red()
        movers_data = requests.get('https://financialmodelingprep.com/api/v3/stock/losers').json()['mostLoserStock']

    embed = discord.Embed(title=title, color=color)

    num = 1
    for stock in movers_data:
        text = 'Price: ' + str(stock['price']) + '\nChange: ' + str(stock['changes'] + '\nPercent Change: ' + stock[''].strip(['(', ')']))
        embed.add_field(name = str(num) + '. ' + stock['companyName'] + ' (' + stock['ticker'] + ')', value=text, inline=True)
        num += 1
    
    await ctx.send(embed=embed)



async def get_string_change(current_price, price_change, percent_change, decimal_format):
    """Helper function to get the +/- sign of the
    price and percent change along with the color

    Parameters
    ----------
    current_price : float
        current share price of the ticker
    price_change : float
        difference between the previous close price and the current price
    percent_change : float
        percent difference between the previous close price nad the current price
    decimal_format : string
        string format for the numbers

    Returns
    -------
    ccp : string
        cleaner current price with formatted decimals and removal of trailing 0s and .'s
    cpc : string
        cleaner price change with formatted decimals and removal of trailing 0s and .'s
    cpercentc : string 
        cleaner percent change with formatted decimals
    color : discord.Color
        color for the embedded message
    """

    sign = '+'
    color = discord.Color.green()
    if price_change < 0: # price decrease
        price_change *= -1 # get rid of '-' sign
        percent_change *= -1 # get rid of '-' sign
        color = discord.Color.red()
        sign = '-'

    ccp = '$' + decimal_format.format(current_price).rstrip('0').rstrip('.') # cleaner current price format decimals and remove trailing 0s and .'s
    cpc = sign + "$" + decimal_format.format(price_change).rstrip('0').rstrip('.') # cleaner price change format decimals and remove trailing 0s and .'s
    cpercentc = sign + '{:,.2f}'.format(percent_change) + '%'
    return ccp, cpc, cpercentc, color

async def get_finnhub_quote(ticker, client):
    """Gets the quote for the specified ticker, 
    the quote includes the open price (o), 
    high price (h), low price (l), current price (c), 
    previous close price (pc), timestamp (t)

    Parameters
    ----------
    ticker : string
        stock ticker

    Returns
    -------
    quote : dictionary
        quote for the stock
    dec : string
        string format for the numbers

    """

    quote = client.quote(symbol=ticker)
    if quote['t'] != 0:
        return quote, '{:,.2f}'
    quote = client.quote(symbol='BINANCE:' + ticker)
    if quote['t'] != 0:
        return quote, '{:,.5f}'
    quote = client.quote(symbol='COINBASE:' + ticker)
    if quote['t'] != 0:
        return quote, '{:,.5f}'
    
    # Iterate through remaining exchanges
    crypto_exchanges = client.crypto_exchange()
    for exchange in [i for i in crypto_exchanges if i not in ['Binance', 'COINBASE']]:
        quote = client.quote(symbol=exchange + ':' + ticker)
        if quote['t'] != 0:
            return quote, '{:,.5f}'
    
    return quote, None
