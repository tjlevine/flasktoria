FROM python:3.5-slim
MAINTAINER Tyler Levine <tylevine@cisco.com>

COPY . /flasktoria

WORKDIR /flasktoria
RUN ["pip", "install", "-r", "requirements.txt"]

EXPOSE 8080
CMD ["python3", "app.py"]