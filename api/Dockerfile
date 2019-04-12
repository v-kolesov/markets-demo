FROM python:3.6.7-slim-stretch
WORKDIR /app
RUN mkdir /data
RUN apt-get update
RUN apt-get -y install gcc sqlite
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
VOLUME [ "/app", "/data" ]
EXPOSE 5000
ENTRYPOINT [ "./run" ]