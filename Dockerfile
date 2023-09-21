# https://github.com/joyzoursky/docker-python-chromedriver
# https://github.com/TomRoush/python-selenium-firefox-docker
FROM tomroush/python-selenium-firefox-docker:latest

ENV SELENIUM_HEADLESS=true

ADD page_perf_timer.py /opt/page_timer/

WORKDIR /opt/page_timer

ENTRYPOINT ["python3", "page_perf_timer.py"]
