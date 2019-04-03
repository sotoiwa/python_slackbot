import json

from gokulang.gokulang import GokuLang
from slackbot.bot import listen_to
from slackbot.bot import respond_to


# 孫悟空機能
@listen_to(r'^goku (.*)')
@respond_to(r'^goku (.*)')
def mention_goku(message, document):
    g = GokuLang()
    goku_text = g.translate(document)

    attachments = [{
        'author_name': '孫悟空',
        'text': '{} :goku:'.format(goku_text)
    }]
    message.send_webapi('', json.dumps(attachments))
