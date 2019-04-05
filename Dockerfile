FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --no-cache --virtual=build-deps gcc libc-dev libxml2-dev libxslt-dev \
  && pip install --no-cache-dir -r requirements.txt \
  && apk del build-deps

COPY run.py slackbot_settings.py ./
COPY ./plugins ./plugins

RUN wget https://storage.googleapis.com/kubernetes-release/release/$(wget https://storage.googleapis.com/kubernetes-release/release/stable.txt -O -)/bin/linux/amd64/kubectl \
  && mv kubectl /usr/local/bin/kubectl \
  && chmod +x /usr/local/bin/kubectl

ENTRYPOINT [ "python", "./run.py" ]
