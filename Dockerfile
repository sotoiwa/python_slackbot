FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk --no-cache add gcc libc-dev libxml2-dev libxslt-dev
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY run.py slackbot_settings.py ./
COPY ./plugins ./plugins

RUN wget https://storage.googleapis.com/kubernetes-release/release/$(wget https://storage.googleapis.com/kubernetes-release/release/stable.txt -O -)/bin/linux/amd64/kubectl \
  && mv kubectl /usr/local/bin/kubectl \
  && chmod +x /usr/local/bin/kubectl

ENTRYPOINT [ "python", "./run.py" ]
