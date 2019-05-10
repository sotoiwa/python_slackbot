import datetime
import json
import re

from bs4 import BeautifulSoup
import requests
from slackbot.bot import listen_to
from slackbot.bot import respond_to

import plugins.flickr

# Yahoo!路線情報の関東の運行情報
url = 'https://transit.yahoo.co.jp/traininfo/area/4/'


def get_neko():
    return plugins.flickr.random_search('猫')


@listen_to('電車遅れてる？')
@listen_to('電車遅延してる？')
@respond_to('電車遅れてる？')
@respond_to('電車遅延してる？')
def mention_all_train(message):
    html = requests.get(url)
    html.raise_for_status()

    soup = BeautifulSoup(html.text, 'html.parser')

    # 遅延情報が含まれたtableを抽出
    trouble_div = soup.find('div', class_='elmTblLstLine trouble')
    trouble_table = trouble_div.table

    # 遅延がなければ終了
    if trouble_table is None:
        attachments = [{
            'pretext': '遅れていないようです。',
            'text': trouble_div.text,
            'color': 'good',
            'footer': '<https://transit.yahoo.co.jp/traininfo/area/4/|Yahoo!路線情報>',
            'footer_icon': 'https://transit.yahoo.co.jp/favicon.ico',
            'ts': datetime.datetime.now().strftime('%s')
        }]
        message.send_webapi('', json.dumps(attachments))
        return

    # 行を抽出
    toulble_tr_list = trouble_table.find_all('tr')

    fields = []
    for tr in toulble_tr_list:
        # 路線列の内容
        train = tr.find('a')
        # ヘッダ列はNoneとなるのでスキップ
        if train is None:
            continue
        # 状況列
        status = tr.find('span', class_='colTrouble')
        # 添付に入れるフィールドを作成
        field = {
            'title': train.text,
            'value': '<{}|{}>'.format(train['href'], status.text),
            'short': 'true'
        }
        fields.append(field)

    attachments = [{
        'pretext': '次の電車が遅れています。',
        'fields': fields,
        'color': 'warning',
        'footer': '<https://transit.yahoo.co.jp/traininfo/area/4/|Yahoo!路線情報>',
        'footer_icon': 'https://transit.yahoo.co.jp/favicon.ico',
        'ts': datetime.datetime.now().strftime('%s')
    }]
    message.send_webapi('', json.dumps(attachments))


@listen_to(r'^(.*(線|ライン|ライナー|シャトル))(遅れ|遅延し)てる？')
@respond_to(r'^(.*(線|ライン|ライナー|シャトル))(遅れ|遅延し)てる？')
def mention_train(message, train_name, arg2, arg3):
    html = requests.get(url)
    html.raise_for_status()

    soup = BeautifulSoup(html.text, 'lxml')

    # 路線のtableを含むdivをすべて抽出
    all_div = soup.find_all('div', class_='elmTblLstLine')

    # 全ての路線行を抽出する
    all_tr_list = []
    for div in all_div:
        table = div.table
        if table is None:
            continue
        all_tr_list.extend(table.find_all('tr'))

    for tr in all_tr_list:
        # 路線列の内容
        train = tr.find('a')
        # ヘッダ列はNoneとなるのでスキップ
        if train is None:
            continue
        # 引数の路線にマッチした場合のメッセージ
        if re.compile(train_name).search(train.text):
            # 詳細を取得する
            detail_html = requests.get(train['href'])
            detail_html.raise_for_status()
            detail_soup = BeautifulSoup(detail_html.text, 'lxml')
            status_div = detail_soup.find('div', id='mdServiceStatus')
            status = status_div.find('dt').contents[-1]
            # 平常運転の場合のメッセージ
            normal = status_div.find('dd', class_='normal')
            # トラブル時のメッセージ
            trouble = status_div.find('dd', class_='trouble')

            if trouble is None:
                color = 'good'
                pretext = '{}は遅れていないようです。'.format(train.text)
                text = normal.p.contents[0]
            else:
                color = 'warning'
                pretext = '{}は遅れています。'.format(train.text)
                text = trouble.p.contents[0]

            attachments = [{
                'pretext': pretext,
                'title': status,
                'title_link': train['href'],
                'text': text,
                'color': color,
                'footer': '<https://transit.yahoo.co.jp/traininfo/area/4/|Yahoo!路線情報>',
                'footer_icon': 'https://transit.yahoo.co.jp/favicon.ico',
                'ts': datetime.datetime.now().strftime('%s')
            }]
            message.send_webapi('', json.dumps(attachments))

            return

    # どの路線にもマッチしなかった場合
    attachments = [{
        'pretext': 'そのような路線はありません。',
        'text': train_name,
        'color': 'danger',
        'image_url': get_neko(),
        'footer': '<https://transit.yahoo.co.jp/traininfo/area/4/|Yahoo!路線情報>',
        'footer_icon': 'https://transit.yahoo.co.jp/favicon.ico',
        'ts': datetime.datetime.now().strftime('%s')
    }]
    message.send_webapi('', json.dumps(attachments))
