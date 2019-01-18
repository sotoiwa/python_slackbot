import re
import subprocess

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


# kubectl
@respond_to(r'^kubectl (.*)')
def mention_kubectl(message, command):

    try:
        completed_process = subprocess.run('kubectl {}'.format(command),
                                           shell=True,
                                           check=True,
                                           capture_output=True)
        result_str = completed_process.stdout.decode('utf-8')

    except subprocess.CalledProcessError as e:
        result_str = e.stderr.decode('utf-8')

    msg = '```\n' + result_str + '```'
    message.reply(msg)
