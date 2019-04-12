import json
import random
import os

import flickrapi
from slackbot.bot import respond_to

FLICKR_API_KEY = os.environ['FLICKR_API_KEY']
FLICKR_API_SECRET = os.environ['FLICKR_API_SECRET']
SLACKBOT_API_TOKEN = os.environ['SLACKBOT_API_TOKEN']


# ランダム検索
def random_search(keyword):
    flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_API_SECRET, format='parsed-json')

    # See: http://westplain.sakuraweb.com/translate/flickr/APIMethods/photos/search.cgi
    result = flickr.photos.search(
        # 検索キーワード
        text=keyword,
        # 取得するデータ件数
        per_page=400,
        # 検索するデータの種類
        media='photos',
        # データの並び順
        sort='relevance',
        # 安全検索設定
        safe_search=1,
        # 取得したいオプションの値
        extras='url_m'
    )

    # 画像をランダムに一枚選ぶ
    return random.choice(result['photos']['photo'])['url_m']


# 画像検索機能
@respond_to(r'^(.*)下さい')
@respond_to(r'^(.*)ください')
def mention_flickr(message, keyword):

    if keyword in ['美女', '美人']:
        cwd = os.path.abspath(os.path.dirname(__file__))
        filename = os.path.join(cwd, 'photo1.jpg')
        message.channel.upload_file(keyword, filename)
        return

    # 画像をランダムに一枚選ぶ
    try:
        photo_url = random_search(keyword)
    except IndexError as e:
        # 写真が見つからなかった場合
        text = 'ごめんなさい、{}はみつかりませんでした。'.format(keyword)
        message.reply(text)
        return

    # file.upload apiを利用して画像を送るパターン
    #
    # # 画像を取得してインメモリーのバイナリストリームに格納
    # data = requests.get(photo_url)
    # data.raise_for_status()
    # f = io.BytesIO(data.content)
    #
    # # Slackにアップロードする
    # files = {
    #     'file': f
    # }
    # param = {
    #     'token': slack_token,
    #     'channels': '#sandbox'
    # }
    # res = requests.post(url='https://slack.com/api/files.upload', params=param, files=files)
    # res.raise_for_status()

    # 添付でURLを送るパターン
    attachments = [{
        'title': keyword,
        'image_url': photo_url
    }]

    message.reply_webapi('', json.dumps(attachments))
