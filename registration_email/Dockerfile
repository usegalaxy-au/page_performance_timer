# https://github.com/joyzoursky/docker-python-chromedriver
FROM joyzoursky/python-chromedriver:3.9

ENV SELENIUM_HEADLESS=true

ADD requirements.txt /opt/page_timer/
ADD registration_email_perf_timer.py /opt/page_timer/

WORKDIR /opt/page_timer

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "registration_email_perf_timer.py"]
