# Discord Stock Exchange (DSE)
Virtual stock exchange bot to use virtual currency in the real world market

**Bot Prefix**: Start a command with % to use the bot (ex. `%stock AAPL`)

## Add to your server
[Invite DSE to server](https://discordapp.com/api/oauth2/authorize?client_id=690279463648493578&permissions=117824&scope=bot)

## Commands
- stock [ticker]
    - Display stock price, price change, percent change
- rs [ticker]
    - Displays the stock price, price change, percent change in real time (updates every minute for 5 minutes)
- gainers
    - Displays the top 10 stock gainers of the day
- losers
    - Displays the top 10 stock losers of the day
- stockcandle [ticker timeframe]
    - Displays the stock's candle data over specified timeframe.  
      - Possible timeframes (multiples can be specified ex. 5D): D, W, M, Y, MAX
- stockline [ticker timeframe]
    - Displays the stock\'s data in a line graph over specified timeframe.
      - Possible timeframes (multiples can be specified ex. 5D): D, W, M, Y, MAX
- stockrenko [ticker timeframe]
    - Displays the stock\'s data in a renko chart over specified timeframe.
      - Possible timeframes (multiples can be specified ex. 5D): D, W, M, Y, MAX
- stockpf [ticker timeframe]
    - Displays the stock\'s data in a Point & Figure plot over specified timeframe.
      - Possible timeframes (multiples can be specified ex. 5D): D, W, M, Y, MAX


## How to contribute
1. Fork repo
2. Install required dependencies
2. Write additional implementations
3. Create a bot on the [Discord Developer Portal](https://discordapp.com/developers/applications/)
4. Add your bot's token to your computer's environmental variables
    - key: 'DSE_BOT_TOKEN'
    - value: 'YOUR BOT TOKEN'
5. Invite your bot to a private test server
6. Test added bot commands
7. Once working, create a pull request

## Dependencies
To install the dependencies, in the root folder, run:
`pip install -r requirements.txt`