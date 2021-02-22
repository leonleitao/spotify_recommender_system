FROM python:3.7.9

WORKDIR /opt/application

ENV FLASK_APP run.py

ADD . /opt/application
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

RUN chmod +x run.sh

EXPOSE 5000

CMD ["bash", "run.sh"]