import json
import os

import requests
from slackbot.bot import listen_to
from slackbot.bot import respond_to

BASE_URL = 'https://api.ce-cotoha.com/api/dev/nlp/'
COTOHA_CLIENT_ID = os.environ['COTOHA_CLIENT_ID']
COTOHA_CLIENT_SECRET = os.environ['COTOHA_CLIENT_SECRET']


def auth(client_id, client_secret):
    token_url = 'https://api.ce-cotoha.com/v1/oauth/accesstokens'
    headers = {
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    data = {
        'grantType': 'client_credentials',
        'clientId': client_id,
        'clientSecret': client_secret
    }
    r = requests.post(token_url,
                      headers=headers,
                      data=json.dumps(data))
    return r.json()['access_token']


def parse(sentence, access_token):
    base_url = BASE_URL
    headers = {
        'Content-Type': 'application/json',
        'charset': 'UTF-8',
        'Authorization': 'Bearer {}'.format(access_token)
    }
    data = {
        'sentence': sentence,
        'type': 'default'
    }
    r = requests.post(base_url + 'v1/parse',
                      headers=headers,
                      data=json.dumps(data))
    return r.json()


# 原始人機能
@listen_to(r'^genshijin (.*)')
@respond_to(r'^genshijin (.*)')
def mention_genshijin(message, document):
    access_token = auth(COTOHA_CLIENT_ID, COTOHA_CLIENT_SECRET)
    parse_document = parse(document, access_token)
    result_list = list()
    for chunks in parse_document['result']:
        for token in chunks['tokens']:
            if token['pos'] != '格助詞' and token['pos'] != '連用助詞' and token['pos'] != '引用助詞' and token['pos'] != '終助詞':
                result_list.append(token['kana'])

    genshijin_text = ' '.join(result_list)

    attachments = [{
        'author_name': '原始人',
        'text': genshijin_text
    }]
    message.send_webapi('', json.dumps(attachments))
