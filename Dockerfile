FROM python:3.5-slim
MAINTAINER Tyler Levine <tylevine@cisco.com>

RUN apt-get update && apt-get -y install gcc && rm -rf /var/lib/apt/lists/*

RUN mkdir /flasktoria
COPY requirements.txt /flasktoria/requirements.txt

RUN ["pip", "install", "-r", "/flasktoria/requirements.txt"]

COPY . /flasktoria
WORKDIR /flasktoria

EXPOSE 8080
EXPOSE 18081
CMD ["python3", "app.py"]
