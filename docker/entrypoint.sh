#!/bin/bash
#cd /opt/leximpact-server
set -e
sleep 3
echo "$DATABASE_USER@$DATABASE_HOST:$DATABASE_PORT"
until PGPASSWORD=$DATABASE_PASS psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -d "$DATABASE_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 3
done
  


while PGPASSWORD=$DATABASE_PASS psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -p "$DATABASE_PORT" -d "$DATABASE_NAME" -c '\q'; do
  echo "Postgres is up, start archiving !"
  python archiveur.py
  echo "Sleeping 8 hours..."
  sleep 28800
done