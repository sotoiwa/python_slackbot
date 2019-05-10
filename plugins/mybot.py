import re

from slackbot.bot import default_reply
from slackbot.bot import respond_to


default_word = '何言ってんだこいつ'


# デフォルトの返事
@default_reply()
def default_func(message):
    message.reply(default_word)


# こんにちはに応答する
@respond_to('hello', re.IGNORECASE)
@respond_to('こんにちは|こんにちわ')
def mention_hello(message):
    message.reply('こんにちは！')


# こんばんはに応答する
@respond_to('こんばんは|こんばんわ')
def mention_goodeveing(message):
    message.reply('こんばんは！')


# おはように応答する
@respond_to('おはよう')
def mention_goodmoring(message):
    message.reply('おはよう！')


# ありがとうに応答する
@respond_to('ありがとう')
def mention_goodmoring(message):
    message.reply('どういたしまして！')
