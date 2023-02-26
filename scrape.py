import requests
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pathlib import Path

class Connection():

    def __init__(self, auth_dir: Path = Path("token.txt")):
        with open(auth_dir) as f:
            self.token = f.read()
        
        self.headers = { 'authorization': self.token }
        self.url = 'https://discord.com/api/v8'
        
    def req(self, url, params={}):
        r = requests.get(url, headers=self.headers, params=params)
        return json.loads(r.text)
   


class Channel():
    
    def __init__(self, id, conn: Connection):
        self.id = id
        self.conn = conn
        self.messages = []
        self.name = None
        self.set_channel_name()
    
    def retrieve_messages(self, amount, before=None):
        url = f'{self.conn.url}/channels/{self.id}/messages'
        params = {"limit": 100}
        if before:
            params['before'] = before
        data = self.conn.req(url, params)
        if not before:
            before = data[-1]['id']
        self.messages.extend(data)
        if len(self.messages) < amount:
            self.retrieve_messages(amount, before)
    
    def set_channel_name(self):
        if not self.name:
            url = f'{self.conn.url}/channels/{self.id}'
            data = self.conn.req(url) 
            guild_id = data['guild_id']
            data = self.conn.req(f'{self.conn.url}/guilds/{guild_id}')
            self.name = data['name']


conn = Connection()

def load_channels():
    with open("channels.txt", "r") as f:
        channels = [Channel(channel.strip(), conn) for channel in f.readlines()]  
    return channels


def calculate_sentiment(text):
    sent = SentimentIntensityAnalyzer()
    scores = sent.polarity_scores(text)
    return scores['compound']

channels = load_channels()
sentiment_scores = []
for channel in channels:
    channel.retrieve_messages(1000)
    print(f'num messages: {len(channel.messages)}')
    channel_sentiments = [calculate_sentiment(msg["content"]) for msg in channel.messages]
    channel_average = sum(channel_sentiments) / len(channel_sentiments)
    print(f"Average sentiment score for {channel.name}: {channel_average:.2f}")
    positive = [s for s in channel_sentiments if s > 0]
    neutral = [s for s in channel_sentiments if s == 0]
    negative = [s for s in channel_sentiments if s < 0]
    total = len(channel_sentiments)
    pct_positive = len(positive) / total * 100
    pct_neutral = len(neutral) / total * 100
    pct_negative = len(negative) / total * 100
    print(f"{pct_positive:.2f}% positive, {pct_neutral:.2f}% neutral, {pct_negative:.2f}% negative\n")

