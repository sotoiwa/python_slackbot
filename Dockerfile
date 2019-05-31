FROM golang:1.12.5-alpine3.9 as builder

WORKDIR /go/src/app
RUN apk add --update alpine-sdk
RUN go get -u github.com/greymd/ojichat

FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN wget -q https://storage.googleapis.com/kubernetes-release/release/$(wget https://storage.googleapis.com/kubernetes-release/release/stable.txt -O -)/bin/linux/amd64/kubectl \
  && mv kubectl /usr/local/bin/kubectl \
  && chmod +x /usr/local/bin/kubectl

COPY --from=builder /go/bin/ojichat /usr/local/bin/

COPY run.py slackbot_settings.py ./
COPY ./plugins ./plugins

ENTRYPOINT [ "python", "./run.py" ]
