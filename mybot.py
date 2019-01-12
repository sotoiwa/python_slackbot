import json
import os
import re

from kubernetes import client, config
import prettytable
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply


default_word = '何言ってんだこいつ'


# デフォルトの返事
@default_reply()
def default_func(message):
    message.reply(default_word)


# デフォルトの返事を変える
@respond_to('set default (.*)')
def mention_set_default(message, new_default_word):
    global default_word
    default_word = new_default_word
    msg = 'デフォルトの返事を以下に変更しました\n```' + new_default_word + '```'
    message.reply(msg)


# デフォルトの返事を確認
@respond_to('get default')
def mention_ge_default(message):
    global default_word
    msg = 'デフォルトの返事は以下です\n```' + default_word + '```'
    message.reply(msg)


# こんにちはに応答する
@respond_to('hello', re.IGNORECASE)
@respond_to('こんにちは|こんにちわ')
def mention_hello(message):
    message.reply('こんにちは！')


# 遅れに反応する
@listen_to('遅延|遅れ')
def listen_late(message):
    message.reply('ゆっくりどうぞ！')


# kubectlに反応する
@listen_to('kubectl', re.IGNORECASE)
def listen_kubectl(message):
    # message.reply('kubectlかっこいい！')
    message.react('kubernetes')


# helmに反応する
@listen_to('helm', re.IGNORECASE)
def listen_helm(message):
    # message.reply('helmかっこいい！')
    message.react('helm')


# 引数を使う
@listen_to('Give me (.*)')
def listen_give(message, something):
    message.reply('Here is {}'.format(something))


# 添付のテスト
@respond_to('github', re.IGNORECASE)
def github(message):
    attachments = [
    {
        'fallback': 'Fallback text',
        'author_name': 'Author',
        'author_link': 'http://www.github.com',
        'text': 'Some text',
        'color': '#59afe1'
    }]
    message.reply
    message.send_webapi('', json.dumps(attachments))


# kubectl get pod
@respond_to(r'^kubectl\s+get\s+(po|pod|pods)\s+(-n|--namespace)\s+(.*)$')
def mention_kubectl_get_po(message, arg2, arg3, namespace):

    if os.getenv('KUBERNETES_SERVICE_HOST'):
        # ServiceAccountの権限で実行する
        config.load_incluster_config()
    else:
        # $HOME/.kube/config から読み込む
        config.load_kube_config()

    v1 = client.CoreV1Api()
    ret = v1.list_namespaced_pod(namespace=namespace, watch=False)

    table = prettytable.PrettyTable()
    table.field_names = ['name', 'phase']
    table.align['name'] = 'l'
    table.align['phase'] = 'l'

    for i in ret.items:
        table.add_row([i.metadata.name,
                       i.status.phase
                       ])

    msg = '```\n' + table.get_string() + '\n```'
    message.reply(msg)


# kubectl get ns
@respond_to(r'^kubectl\s+get\s+(ns|namespace|namespaces)$')
def mention_kubectl_get_ns(message, arg2):

    if os.getenv('KUBERNETES_SERVICE_HOST'):
        # ServiceAccountの権限で実行する
        config.load_incluster_config()
    else:
        # $HOME/.kube/config から読み込む
        config.load_kube_config()

    v1 = client.CoreV1Api()
    ret = v1.list_namespace(watch=False)

    table = prettytable.PrettyTable()
    table.field_names = ['name']
    table.align['name'] = 'l'

    for i in ret.items:
        table.add_row([i.metadata.name])

    msg = '```\n' + table.get_string() + '\n```'
    message.reply(msg)
