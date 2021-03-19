#!/usr/bin/python3
from tweet_archiveur import scrapper
from tweet_archiveur import database
import pandas as pd
from os import getenv
from dotenv import load_dotenv
from pathlib import Path
from sys import exit
import logging
from psycopg2.errors import DuplicateTable

# Logging
logger = logging.getLogger("tweet-archiveur")
logFormatter = logging.Formatter("%(asctime)s -  %(name)-12s %(levelname)-8s %(message)s")
logger.setLevel(logging.DEBUG)
if not len(logger.handlers):
    # Console logger
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
logger.info(f'Start archiving')

# Load env if not set
if getenv('DATABASE_USER') is None:
    print("No env variable found, loading .env...")
    env_path = Path('.') / '.env'
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path)
    else:
        logger.error(f"No env set and no {env_path} found !")
        exit(1)

df_users = scrapper.get_users_accounts()

conn = database.db_connect()

try:
    database.create_tables_if_not_exist(conn)
except DuplicateTable:
    logger.info(f'Good, tables already exist.')


fields = { # pandas : database
    'twitter_id' : 'twitter_id',
    'nom' : 'name',
    'twitter_followers' : 'twitter_followers',
    'twitter_tweets' : 'twitter_tweets' 
}
database.insert_pandas(conn, 'twitter_users', df_users, fields)

users_id = df_users.twitter_id.tolist()

logger.info(f'Getting all tweet...')
tweets = scrapper.get_all_tweet(users_id, logger)

df_tweets = pd.DataFrame(tweets)
# Escape unwanted character from tweet (% for)
df_tweets['text_new'] = df_tweets.text.apply(database.filter_str)
fields = { # pandas : database
    'tweet_id' : 'tweet_id',
    'user_id' : 'twitter_id',
    'datetime_utc' : 'datetime_utc',
    'datetime_local' : 'datetime_local',
    'retweet' : 'retweet',
    'favorite' : 'favorite',
    'text_new' : 'text',
}
database.insert_pandas(conn, 'tweets', df_tweets, fields)

logger.info(f'Done archiving')