#!/usr/bin/python
from tweet_archiveur import scrapper
from tweet_archiveur import database
import pandas as pd
from os import getenv
from dotenv import load_dotenv
from pathlib import Path
from sys import exit
import logging
import time
import tweepy
import random

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
    logger.warning("No env variable found, loading .env...")
    env_path = Path('.') / '.env'
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path)
    else:
        logger.error(f"No env set and no {env_path} found !")
        exit(1)

df_users = scrapper.get_users_accounts()

conn = database.db_connect()

database.create_tables_if_not_exist(conn)

database.insert_twitter_users(conn, df_users)

users_id = df_users.twitter_id.tolist()
total_users = len(users_id)
total_tweet = 0
logger.info(f'Getting all tweet...')

# Do a while loop to handle retry on error
# We store a list of remaining id to process
users_id_to_process = users_id
consecutive_fail = 0
while len(users_id_to_process) > 0:
    user_id = users_id_to_process[0]
    try:
        # Get tweets
        tweets, hashtags = scrapper.get_user_tweets(user_id)
        total_tweet += len(tweets)
    except tweepy.TweepError as e:
        if e.response.status == 401 :
            logger.warning(f'Error processing {user_id} : The user have a private account, skipping.')
            users_id_to_process.pop(0)
            continue
        logger.warning(f'Error processing {user_id} : tweepy.TweepError={e.reason} We will retry in 16 minutes to respect twitter API Rate Limit')
        consecutive_fail += 1
        if consecutive_fail > 3:
            logger.error(f'We fail {consecutive_fail} consecutive times, exiting.')
            exit(3)
        time.sleep(16*60*consecutive_fail)
        # We shuffle the list to try another user next time
        random.shuffle(users_id_to_process)
        continue
    except:
        e = sys.exc_info()[0]
        logger.error(f'UNKNOW ERROR processing {user_id} STOPPING : Error={e}')
        exit(2)
    try:
        # Save them to database
        database.insert_tweets(conn, pd.DataFrame(tweets))
        database.insert_hashtags(conn, pd.DataFrame(hashtags))
    except:
        e = sys.exc_info()[0]
        logger.error(f'UNKNOW ERROR processing {user_id} STOPPING : Error={e}')
        exit(2)
    # Yes, we succeded
    consecutive_fail = 0
    # Remove user from the list to process
    users_id_to_process.pop(0)
    total_tweet += len(tweets)
    i = total_users - len(users_id_to_process)
    if i % 10 == 0:
        logger.debug(f'We got {total_tweet} tweets for now. Processing user {i} / {total_users} ({(i*100//total_users*100)/100}%) {user_id=} ...')

logger.info(f'Done archiving')