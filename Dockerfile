FROM python:3.6-slim
MAINTAINER Tyler Levine <tylevine@cisco.com>

# install build and runtime deps
RUN apt-get update && apt-get -y install gcc ssh netcat-openbsd

RUN mkdir /flasktoria
COPY requirements.txt /flasktoria

# install python runtime deps
RUN pip install -r /flasktoria/requirements.txt

# remove build deps and clean house
RUN apt-get -y purge --auto-remove gcc && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# copy the rest of the app over
COPY . /flasktoria

# expose ports and set entry point
EXPOSE 8080
EXPOSE 18081
CMD ["/flasktoria/docker-entry.sh"]
