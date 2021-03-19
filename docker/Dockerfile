FROM python:3.9
#RUN apk --update add postgresql-client
RUN apt-get update && apt-get -y install postgresql-client && apt-get clean
WORKDIR /opt/tweet_archiveur
# Tips : relative path is from root project folder as we use context in docker-compose
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./docker/entrypoint.sh .
RUN chmod a+x entrypoint.sh
COPY tweet_archiveur .
COPY archiveur.py .
#EXPOSE 5000
ENTRYPOINT ["/opt/tweet_archiveur/docker/entrypoint.sh"]