import os
import re

from kubernetes import client, config
import prettytable
from slackbot.bot import respond_to
from slackbot.bot import listen_to


# こんにちはに応答する
@respond_to('hello', re.IGNORECASE)
@respond_to('こんにちは|こんにちわ')
def mention_hello(message):
    message.reply('こんにちは！')


# kubernetesに反応する
@listen_to('kubernetes', re.IGNORECASE)
def listen_kubernetes(message):
    message.reply('kubernetesかっこいい！')
    message.react('+1')


# helmに反応する
@listen_to('helm', re.IGNORECASE)
def listen_helm(message):
    message.reply('helmかっこいい！')
    message.react('+1')


# get pod
@respond_to(r'^get\s+(po|pod|pods)\s+(-n|--namespace)\s+(.*)$')
def mention_get_po(message, arg2, arg3, namespace):

    # kubernetes上で動いているかを環境変数から判断する
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


# get ns
@respond_to(r'^get\s+(ns|namespace|namespaces)$')
def mention_get_ns(message, arg2):

    # kubernetes上で動いているかを環境変数から判断する
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
