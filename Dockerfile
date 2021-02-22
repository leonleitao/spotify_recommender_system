FROM python:3.7.9

WORKDIR /opt/application

ENV FLASK_APP run.py
ENV CLIENT_SECRET=$CLIENT_SECRET
ENV CLIENT_ID=$CLIENT_ID
ENV REDIRECT_URI=$REDIRECT_URI

ADD . /opt/application
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

RUN chmod +x run.sh

EXPOSE 5000

CMD ["bash", "run.sh"]