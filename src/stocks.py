import discord
import os
import time
import re
import datetime
from calendar import monthrange
from PIL import Image, ImageFont, ImageDraw
from finnhub import client as Finnhub # api docs: https://finnhub.io/docs/api
import requests
import matplotlib
import mplfinance
import pandas as pd

FINNHUB_API_TOKEN = os.environ.get('FINNHUB_API_TOKEN')
finnhub_client = Finnhub.Client(api_key=FINNHUB_API_TOKEN)



def get_string_change(current_price, price_change, percent_change, decimal_format):
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


async def stock_price_today(ctx, ticker):
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
    quote, decimal_format = get_quote(ticker.upper())
    if quote['t'] == 0:
        await ctx.send(embed=discord.Embed(description='Invalid Ticker!', color=discord.Color.dark_red()))
        return
    current_price = quote["c"]
    price_change = current_price - quote["pc"]
    percent_change = ((current_price / quote["pc"])-1) * 100
    
    ccp, cpc, cpercentc, color = get_string_change(current_price, price_change, percent_change, decimal_format)

    
    embedded_message = discord.Embed(
        # format with appropriate ','
        description=ticker.upper() + " Price: " + ccp + " USD\nPrice Change: " + cpc + " (" + cpercentc + ")", 
        color=color
        )
    embedded_message.set_footer(text='As of ' + str(time.ctime(time.time())))
    await ctx.send(embed=embedded_message)

def get_quote(ticker):
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

    quote = finnhub_client.quote(symbol=ticker)
    if quote['t'] != 0:
        return quote, '{:,.2f}'
    quote = finnhub_client.quote(symbol='BINANCE:' + ticker)
    if quote['t'] != 0:
        return quote, '{:,.5f}'
    quote = finnhub_client.quote(symbol='COINBASE:' + ticker)
    if quote['t'] != 0:
        return quote, '{:,.5f}'
    
    # Iterate through remaining exchanges
    crypto_exchanges = finnhub_client.crypto_exchange()
    for exchange in crypto_exchanges:
        quote = finnhub_client.quote(symbol=exchange + ':' + ticker)
        if quote['t'] != 0:
            return quote, '{:,.5f}'
    
    return quote, None
