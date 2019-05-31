import datetime
import json
import os
import re
import subprocess

from kubernetes import client, config
from slackbot.bot import listen_to
from slackbot.bot import respond_to


# ojichatコマンドを実行する
@respond_to(r'^ojichat(.*)')
def mention_ojichat(message, ojichat_args):
    try:
        cmd = 'ojichat{}'.format(ojichat_args)
        completed_process = subprocess.run(cmd.split(),
                                           check=True,
                                           capture_output=True)
        result_str = completed_process.stdout.decode('utf-8') + completed_process.stderr.decode('utf-8')

    except subprocess.CalledProcessError as e:
        result_str = e.stdout.decode('utf-8') + e.stderr.decode('utf-8')

    message.reply(result_str)
