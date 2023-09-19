# https://github.com/joyzoursky/docker-python-chromedriver
# https://github.com/TomRoush/python-selenium-firefox-docker
# FROM tomroush/python-selenium-firefox-docker:latest
FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
  python3 python3-pip \
  firefox-geckodriver \
  xvfb \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir selenium

ENV SELENIUM_HEADLESS=true

ADD page_perf_timer.py /opt/page_timer/

WORKDIR /opt/page_timer

ENTRYPOINT ["python3", "page_perf_timer.py"]
