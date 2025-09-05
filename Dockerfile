# https://github.com/joyzoursky/docker-python-chromedriver
# https://github.com/TomRoush/python-selenium-firefox-docker
FROM python:3.13-slim AS selenium

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  # firefox needs the following installed on debian
  libgtk-3-common libasound2 libdbus-glib-1-2 \
  firefox-esr \
  xvfb \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir selenium requests

FROM selenium

ENV SELENIUM_HEADLESS=true
ARG DEBIAN_FRONTEND=noninteractive

ADD page_perf_timer.py /opt/page_timer/

WORKDIR /opt/page_timer

ENTRYPOINT ["python3", "page_perf_timer.py"]
