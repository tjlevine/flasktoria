FROM python:3.5-slim
MAINTAINER Tyler Levine <tylevine@cisco.com>


RUN mkdir /flasktoria
COPY requirements.txt /flasktoria/requirements.txt

RUN ["pip", "install", "-r", "/flasktoria/requirements.txt"]

COPY . /flasktoria
WORKDIR /flasktoria

EXPOSE 8080
EXPOSE 18081
CMD ["python3", "app.py"]
