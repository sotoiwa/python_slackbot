import json
import re
import subprocess

from slackbot.bot import listen_to
from slackbot.bot import respond_to


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


# kubectlコマンドを実行する
@respond_to(r'^kubectl (.*)')
def mention_kubectl(message, kubectl_args):

    try:
        cmd = 'kubectl {}'.format(kubectl_args)
        completed_process = subprocess.run(cmd.split(),
                                           check=True,
                                           capture_output=True)
        result_str = completed_process.stdout.decode('utf-8') + completed_process.stderr.decode('utf-8')
        color = 'good'

    except subprocess.CalledProcessError as e:
        result_str = e.stdout.decode('utf-8') + e.stderr.decode('utf-8')
        color = 'warning'

    msg = '```\n{}```'.format(result_str)

    attachments = [{
        'text': msg,
        'color': color,
        'mrkdwn_in': [
            'text'
        ]
    }]
    message.reply_webapi('', json.dumps(attachments))
