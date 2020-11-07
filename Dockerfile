# https://github.com/joyzoursky/docker-python-chromedriver
FROM joyzoursky/python-chromedriver:3.8

ENV SELENIUM_HEADLESS=true

RUN pip install selenium

ADD page_perf_timer.py /opt/page_timer/

WORKDIR /opt/page_timer

ENTRYPOINT ["python", "page_perf_timer.py"]