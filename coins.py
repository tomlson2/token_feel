import requests
import json
import ccxt
import matplotlib.pyplot as plt
import numpy as np
import datetime

# Load repos
with open('repos.txt', 'r') as f:
    repos = [tuple(line.strip().split(',')) for line in f]

# Define the cryptocurrency exchange and pair
exchange = ccxt.binanceus()

# Define the timeframe and number of candles to retrieve
timeframe = '1m'
limit = 12

# Loop through the repos
for repo in repos:
    # Define the GitHub API URL
    print(repo[0])
    url = f'https://api.github.com/repos/{repo[0].strip()}/stats/commit_activity'

    # Make a request to the GitHub API
    response = requests.get(url)

    # Parse the JSON data from the response
    data = json.loads(response.text)
    print(data)

    # Extract the number of commits per week
    commits = [0] * 12
    for week in data:
        # Get the start of the week as a datetime object
        week_start = datetime.datetime.fromtimestamp(week['week'])

        # Add the number of commits to the corresponding month
        month_index = week_start.month - 1
        commits[month_index] += week['total']

    # Retrieve the price data from the exchange
    symbol = f"{repo[1].strip()}/BTC"
    print(symbol)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    # Extract the closing prices
    prices = [candle[4] for candle in ohlcv]

    # Calculate the correlation between the commits and prices
    corr = np.corrcoef(commits, prices)[0, 1]

    # Plot the data on a graph
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Weeks')
    ax1.set_ylabel('Commits', color=color)
    ax1.plot(commits, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel('Price (BTC)', color=color)
    ax2.plot(prices, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()

    plt.title(f'{repo[0].strip()} (Correlation: {corr:.2f})')
    plt.show()