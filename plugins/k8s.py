import datetime
import json
import os
import re
import subprocess

from kubernetes import client, config
from slackbot.bot import listen_to
from slackbot.bot import respond_to


# kubernetesに反応する
# @listen_to('kubernetes', re.IGNORECASE)
# def listen_kubernetes(message):
#     message.reply('kubernetesかっこいい！')
#     message.react('+1')


# helmに反応する
# @listen_to('helm', re.IGNORECASE)
# def listen_helm(message):
#     message.reply('helmかっこいい！')
#     message.react('+1')


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


# Pod状況照会
@respond_to('(Pod|pod|ポッド|ぽっど)(大丈夫|元気)？')
def menthon_pod(message, arg1, arg2):
    # Kubernetes上で動いているかを環境変数から判断する
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        # ServiceAccountの権限で実行する
        config.load_incluster_config()
    else:
        # $HOME/.kube/config から読み込む
        config.load_kube_config()

    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)

    attachment_text = ''
    for pod in ret.items:

        # PodのフェーズがRunningかSucceeded以外の場合
        if pod.status.phase != 'Running':
            attachment_text += '`{}/{}` が `{}` 状態です\n'.format(pod.metadata.namespace, pod.metadata.name,
                                                              pod.status.phase)

        # ready=trueではないコンテナがある場合
        container_statuses = pod.status.container_statuses
        for container_status in container_statuses:
            if container_status.ready is False:
                if container_status.state.waiting:
                    reason = container_status.state.waiting.reason
                if container_status.state.terminated:
                    reason = container_status.state.terminated.reason
                attachment_text += '`{}/{}` の `{}` コンテナが `{}` のため `ready` ではありません\n'.format(pod.metadata.namespace,
                                                                                            pod.metadata.name,
                                                                                            container_status.name,
                                                                                            reason)

    if attachment_text == '':
        color = 'good'
        pretext = '大丈夫みたいです'
    else:
        color = 'warning'
        pretext = '大丈夫じゃないみたいです'

    attachments = [{
        'pretext': pretext,
        'text': attachment_text,
        'color': color,
        'ts': datetime.datetime.now().strftime('%s')
    }]
    message.send_webapi('', json.dumps(attachments))
