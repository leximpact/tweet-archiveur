# AUTOGENERATED! DO NOT EDIT! File to edit: notebooks/05_database.ipynb (unless otherwise specified).

__all__ = ['logger', 'logFormatter', 'database_config', 'database_url', 'db_connect', 'ENV', 'exec_query',
           'is_table_exist', 'create_tables_if_not_exist', 'insert_pandas', 'filter_str', 'printable']

# Cell
from os import getenv, environ
from dotenv import load_dotenv
import psycopg2
import logging
import pandas as pd

# Cell
# Logging
logger = logging.getLogger("tweet-archiveur")
logFormatter = logging.Formatter("%(asctime)s -  %(name)-12s %(levelname)-8s %(message)s")
# logger.setLevel(logging.DEBUG)
# # File logger
# fh = logging.FileHandler("tweet-archiveur.log")
# fh.setLevel(logging.DEBUG)
# fh.setFormatter(logFormatter)
# logger.addHandler(fh)
if not len(logger.handlers):
    # Console logger
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
logger.info(f'Loading database module...')

# Cell
ENV = [
    "DATABASE_USER",
    "DATABASE_PASS",
    "DATABASE_HOST",
    "DATABASE_PORT",
    "DATABASE_NAME",
    "DATABASE_URL",
]


def database_config():
    return tuple(getenv(env) for env in ENV)


def database_url() -> str:
    user, pswd, host, port, name, url = database_config()
    logger.debug(f"DEBUG : connect(user={user}, password=XXXX, host={host}, port={port}, database={name}, url={url})")
    if user is None and url is None:
        logger.error("Empty .env : no user or URL !")
        return None
    if url:
        return url
    else:
        return f"postgresql://{user}:{pswd}@{host}:{port}/{name}"

def db_connect():
    return psycopg2.connect(database_url())


# Cell

def exec_query(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

# https://stackoverflow.com/questions/1874113/checking-if-a-postgresql-table-exists-under-python-and-probably-psycopg2
def is_table_exist(con, table_str):
    exists = False
    try:
        cur = con.cursor()
        cur.execute("select * from information_schema.tables where table_schema='public' and  table_name='" + table_str + "';")
        exists = cur.fetchone()[0]
        cur.close()
    except psycopg2.Error as e:
        logger.error(e)
        return False
    return exists

def create_tables_if_not_exist(conn, force = False):
    DATABASE_USER = getenv('DATABASE_USER')
    if force :
        logger.info("Cleaning database")
        # Drop table if exist
        exec_query(conn, 'DROP TABLE IF EXISTS public.twitter_users;')
        exec_query(conn, 'DROP TABLE IF EXISTS public.tweets;')

    # Create table
    if not is_table_exist(conn, 'twitter_users'):
        users = '''
        CREATE TABLE public.twitter_users
        (
            twitter_id bigint NOT NULL,
            name character varying(50) NOT NULL,
            twitter_followers integer,
            twitter_tweets integer,
            PRIMARY KEY (twitter_id)
        );
        '''
        exec_query(conn, users)
        exec_query(conn, f'ALTER TABLE public.twitter_users OWNER to "{DATABASE_USER}";')
    if not is_table_exist(conn, 'tweets'):
        tweets = '''
        CREATE TABLE public.tweets
        (
            tweet_id bigint NOT NULL,
            twitter_id bigint NOT NULL,
            datetime_utc timestamp without time zone,
            datetime_local timestamp with time zone,
            retweet integer,
            favorite integer,
            text character varying(500),
            PRIMARY KEY (tweet_id)
        );'''
        exec_query(conn, tweets)
        exec_query(conn, f'ALTER TABLE public.tweets OWNER to "{DATABASE_USER}";')

# Cell

# Bulk INSERT of values in a table
def insert_pandas(conn, table, df, fields):
    """
    Using cursor.mogrify() to build the bulk insert query
    then cursor.execute() to execute the query
    Thanks to https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
    """
    # Create a list of tupples from the dataframe values
    col = "'" + "', '".join(fields.keys()) + "'"
    df = eval("df[[" + col + "]]")
    logger.debug(f"Bulk insert of {len(df)} lines of {len(df.columns)} columns.")
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(fields.values())
    # SQL quert to execute
    cursor = conn.cursor()
    param_type = param = "(" + ",".join(['%s' for i in range(len(df.columns))]) + ")"
    values = [cursor.mogrify(param_type, tup).decode('utf8') for tup in tuples]
    query  = "INSERT INTO %s(%s) VALUES " % (table, cols) + ",".join(values)
    # Get the primary key, we suppose it is the first one
    primary_key = list(fields.values())[0]
    # Get the list of other column, excluding the primary
    other_fields = list(fields.values())[1:]
    # Build the query to UPDATE if the line already exist
    query += f' ON CONFLICT ({primary_key}) DO UPDATE SET '
    query += "(" + ", ".join(other_fields) + ")"
    excluded = ['EXCLUDED.' + col for col in other_fields]
    query += ' = (' + ", ".join(excluded) + ");"
    try:
        cursor.execute(query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()

# Cell
import string
printable = set(string.printable)
printable.remove('%')
# https://www.programiz.com/python-programming/methods/built-in/filter"
def filter_str(s):
    #return "".join(filter(lambda x: x in printable, s))
    s = s.replace('%', '%%')
    return s