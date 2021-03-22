# Tweet Archiveur
> This project aim at storing the tweet of all members of the French Parliament.


The goal is to use tweets to get an idea of the topics of the tweets using NLP.

## Install

TODO : push it to Pipy when :
- Rename "nom" to name in users
- reactivate unit tests (https://docs.github.com/en/actions/guides/creating-postgresql-service-containers)
- Made scrapper a Class
- Switch to SQL Alchemy
- Flake8
- Documentation

`pip install tweetarchiveur`

## How to use

There is two class :
- A Scrapper() to use the Twitter API
- A Database() to store tweets and hastags in it

```python
from tweet_archiveur.scrapper import Scrapper
from tweet_archiveur.database import Database

# Force some variable outside Docker
from os import environ
environ["DATABASE_PORT"] = '8479'
environ["DATABASE_HOST"] = 'localhost'
environ["DATABASE_USER"] = 'tweet_archiveur_user'
environ["DATABASE_PASS"] = '1234leximpact'
environ["DATABASE_NAME"] = 'tweet_archiveur'

scrapper = Scrapper()
df_users = scrapper.get_users_accounts('../tests/sample-users.csv')
users_id = df_users.twitter_id.tolist()
database = Database()
database.create_tables_if_not_exist()
database.insert_twitter_users(df_users)
scrapper.get_all_tweet_and_store_them(database, users_id[0:2])
del database
del scrapper
```

    2021-03-22 10:21:59,837 -  tweet-archiveur INFO     Scrapper ready
    2021-03-22 10:21:59,841 -  tweet-archiveur INFO     Loading database module...
    2021-03-22 10:21:59,842 -  tweet-archiveur DEBUG    DEBUG : connect(user=tweet_archiveur_user, password=XXXX, host=localhost, port=8479, database=tweet_archiveur, url=None)
    2021-03-22 10:22:03,915 -  tweet-archiveur INFO     Done scrapping, we got 400 tweets from 2 tweetos.


## What to do with it ?

- Most used hashtag (per period, per person)
- Most/Less active user
- Timeline of 
- NLP Topic detection
- Word cloud

# Annexes

Exit code :
- 1 : Unknown error when storing tweets
- 2 : Unknown error getting tweets
- 3 : Failed more than 3 consecutive times
- 4 : no env

If one thing fail no tweet will be saved.

status code = 429 : 429 'Too many requests' error is returned when you exceed the maximum number of requests allowed 
