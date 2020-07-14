

![alt text](https://github.com/luchpa/tsla_dash/blob/master/tsla_dash.png?raw=true)

# tsla_dash
Simple dash app with Bootstrap components; displays TSLA stock closings and newest tweets about #Tesla

## What does this app use
Python 3.6 and the following packages:
* [Yahoo! finance market data downloader](https://pypi.org/project/yfinance/) to access historical Tesla closing stock prices 
* [Tweepy](http://docs.tweepy.org/en/latest/) to fetch today's tweets about #Tesla 
* [Pandas](https://pandas.pydata.org/) to read and sort tweets as a dataframe 
* [Dash](https://plotly.com/dash/) (with Bootstrap components) to plot the closing stock prices and wrap everything as an app


## Settings 
All of the required libraries to run the app can be found in the requirements.txt.
