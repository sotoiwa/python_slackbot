import re

from slackbot.bot import listen_to
from slackbot.bot import respond_to


# こんにちはに応答する
@respond_to('hello', re.IGNORECASE)
@respond_to('こんにちは|こんにちわ')
def mention_hello(message):
    message.reply('こんにちは！')
