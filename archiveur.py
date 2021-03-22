#!/usr/bin/python
from tweet_archiveur.scrapper import Scrapper
from tweet_archiveur.database import Database
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

logger.info(f'Getting all tweet...')

scrapper = Scrapper()
df_users = scrapper.get_users_accounts()
users_id = df_users.twitter_id.tolist()
database = Database()
database.create_tables_if_not_exist()
database.insert_twitter_users(df_users)
scrapper.get_all_tweet_and_store_them(database, users_id)
del database
del scrapper

logger.info(f'Done archiving')