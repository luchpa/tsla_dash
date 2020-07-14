#######
# First Milestone Project: Develop a Tesla
# dashboard that  allows the user to select
# a date range for TSLA stock, uses pandas_datareader
# to look up and display stock data on a graph and collects data from Twitter with #Tesla
# hashtag, and prints them sorted from the most popular down.
######

import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import datetime
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import tweepy
import json
import csv
import os
import time
import pickle


app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server

yf.pdr_override() #use pandas_datareader
df = pd.read_csv('data/20200706_102141_Tesla_tweets.csv')
df_pop = df[['retweetcount','text']]
df_pop = df_pop.drop_duplicates(subset='text').reset_index(drop=True)
df_pop = df_pop.sort_values(by=['retweetcount'],ascending=False).reset_index(drop=True)
df2 = df_pop[['text']]
df2.columns = ['Tweeter Feed']

app.layout = dbc.Container([
    html.H1('Tesla Stock Dashboard'),
    html.Hr(),
    html.Label('Select start and end dates:'),
    html.Br(),
    dbc.Container([
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime.datetime(2015, 1, 1),
            max_date_allowed=datetime.date.today(),
            start_date=datetime.datetime(2020, 1, 1),
            end_date=datetime.date.today()
        ),
        dbc.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            color='dark',
            style={'fontSize':24, 'marginLeft':'30px'}
        ),
    ], style={'display':'inline-block'}),
    dcc.Graph(
        id='my_graph',
        figure={
            'data': [
                {'x': [1,2], 'y': [3,1]}
            ]
        }
    ),
    html.H4('Twitter feed on #Tesla - updates every hour'),
    dbc.Container([
    dash_table.DataTable(
    id='tweeter_feed',
    style_cell={'height':'auto',
    'whiteSpace': 'normal',
    'textAlign':'left',
    'width':'auto',
    'font-family':'sans-serif'},
    data=df2.to_dict('records'),
    columns=[{"name": i, "id": i
    } for i in df2.columns]
),
    dcc.Interval(
        id='interval-component',
        interval=1000*60*60, # updates every hour
        n_intervals=0
        )
      ],fluid=True)
      ],fluid=True)


@app.callback(
    Output('my_graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_date_picker', 'start_date'),
    State('my_date_picker', 'end_date')])
def update_graph(n_clicks, start_date, end_date):
    start = datetime.datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date[:10], '%Y-%m-%d')
    traces = []
    stock_ticker=['TSLA']
    for tic in stock_ticker:
        df = pdr.get_data_yahoo(tic,start,end)
        traces.append({'x':df.index, 'y': df.Close, 'name':tic, 'marker':{'color':'black'}})
    fig = {
        'data': traces,
        'layout': {'title':', '.join(stock_ticker)+' Closing Prices'}
    }
    return fig


@app.callback(Output('tweeter_feed','data'),
              [Input('interval-component', 'n_intervals')])
def update_twitter(n):
    return getData()

def getData():
    auth = Tweepy_auth()
    api = tweepy.API(auth)
    search_words = "#Tesla"
    date_since = datetime.date.today()- datetime.timedelta(days=1)
    numTweets = 2500
    numRuns = 1
    # Call the function scraptweets
    df = scraptweets(api, search_words, date_since, numTweets, numRuns)
    df_pop = df[['retweetcount','text']]
    df_pop = df_pop.drop_duplicates(subset='text').reset_index(drop=True)
    df_pop = df_pop.sort_values(by=['retweetcount'],ascending=False).reset_index(drop=True)
    df2 = df_pop[['text']]
    df2.columns = ['Tweeter Feed']
    return df2.to_dict('records')

def Tweepy_auth():
  Twitter=pickle.load(open('file.pkl','rb'))
  consumer_key = Twitter['Consumer Key']
  consumer_secret = Twitter['Consumer Secret']
  access_key = Twitter['Access Token']
  access_secret = Twitter['Access Token Secret']
  # Pass your twitter credentials to tweepy via its OAuthHandler
  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_key, access_secret)
  return auth

def scraptweets(api,search_words, date_since, numTweets, numRuns):
    #function from: https://medium.com/@leowgriffin/scraping-tweets-with-tweepy-python-59413046e788

    # Define a for-loop to generate tweets at regular intervals
    # We cannot make large API call in one go. Hence, let's try T times

    # Define a pandas dataframe to store the date:
    db_tweets = pd.DataFrame(columns = ['username', 'acctdesc', 'location', 'following',
                                        'followers', 'totaltweets', 'usercreatedts', 'tweetcreatedts',
                                        'retweetcount', 'text', 'hashtags']
                                )
    program_start = time.time()
    for i in range(0, numRuns):

        start_run = time.time()
        tweets = tweepy.Cursor(api.search, q=search_words, lang="en", since=date_since, tweet_mode='extended').items(numTweets)

        tweet_list = [tweet for tweet in tweets]

        noTweets = 0
        for tweet in tweet_list:
            # Pull the values
            username = tweet.user.screen_name
            acctdesc = tweet.user.description
            location = tweet.user.location
            following = tweet.user.friends_count
            followers = tweet.user.followers_count
            totaltweets = tweet.user.statuses_count
            usercreatedts = tweet.user.created_at
            tweetcreatedts = tweet.created_at
            retweetcount = tweet.retweet_count
            hashtags = tweet.entities['hashtags']
            try:
                text = tweet.retweeted_status.full_text
            except AttributeError:  # Not a Retweet
                text = tweet.full_text

            ith_tweet = [username, acctdesc, location, following, followers, totaltweets,
                         usercreatedts, tweetcreatedts, retweetcount, text, hashtags]

            db_tweets.loc[len(db_tweets)] = ith_tweet

            noTweets += 1

        # Run ended:
        end_run = time.time()
        duration_run = round((end_run-start_run)/60, 2)

        print('no. of tweets scraped for run {} is {}'.format(i + 1, noTweets))
        print('time take for {} run to complete is {} mins'.format(i+1, duration_run))


    # Once all runs have completed, save them to a single csv file:

    # Obtain timestamp in a readable format
    to_csv_timestamp = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
    # Define working path and filename
    path = os.getcwd()
    filename = path + '/data/' + to_csv_timestamp + '_Tesla_tweets.csv'
    # Store dataframe in csv with creation date timestamp
    db_tweets.to_csv(filename, index = False)

    program_end = time.time()
    print('Scraping has completed!')
    return db_tweets
    print('Total time taken to scrap is {} minutes.'.format(round(program_end - program_start)/60, 2))


if __name__ == '__main__':
    app.run_server()
