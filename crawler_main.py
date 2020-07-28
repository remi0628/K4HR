import os
import re
import datetime
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs4
import time
from concurrent import futures
import traceback

import crawler_settings  # crawlerの設定ファイル
from crawler_csv import horse_data_csv  # 馬の詳細URL渡してcsvファイル作成
from crawler_csv import result_data_refund # 各レース毎に払戻金をcsvにまとめる
from race_link_collection import horse_race_list  # 半期開催日程URLを渡すと半期分のレースURLを返す

#### https://www.nankankeiba.com/race_info/
CSV_DATA_PATH = crawler_settings.CSV_DATA_PATH
HOME_URL = crawler_settings.HOME_URL
MAX_THREAD = crawler_settings.MAX_THREAD
condition = ''


def url_to_soup(url):  # レース情報ページ取得
    req = requests.get(url)
    return bs4(req.content, 'html.parser')  # 'lmxl'より処理が速い


def horse_page_link(url):  # 各馬の過去情報URLリスト取得
    soup = url_to_soup(url)
    link_list = [HOME_URL + x.get('href') for x in soup.find_all('a', class_='tx-mid tx-low')]  # サイト内リンクから過去情報リンクのみ取得
    if len(link_list) == 0:
        link_list = [HOME_URL + x.get('href') for x in soup.find_all('a', target="_blank") if
                     "uma_info" in x.get('href')]
    return link_list


# lamda
tag_to_text = lambda x: x.split('\n')
split_tr = lambda x: str(x).split('</tr>')


def get_previous_race_row(soup):  # 競走馬詳細データから出走履歴取得
    # 競走馬詳細データサイト内には表が3つ　その内3つめの出走履歴を取得
    race_table = soup.find_all('table', class_='tb01 w100pr bg-over stripe al-center')[2]
    return [tag_to_text(x) for x in split_tr(race_table)]


# 当日データ取得
def result_data(url):  # レース結果取得 return[1着馬, 土の状態, レースの長さ, レース日]
    global condition
    result_url = url[0:28] + 'result' + url[-20:]
    soup = url_to_soup(result_url)
    race_number = soup.find(id="race-data01-b")
    race_number = race_number.find('img').get('alt')[:2]  # レース番号
    try:
        condition_txt = str(soup.find(id="race-data02").contents[4][-4:-2].strip('　'))  # 土の状態
    except IndexError:
        condition_txt = soup.find("table", summary="天候・馬場").text.split()[-1]
    if condition_txt not in ('良', '不良', '重', '稍重'):  # これ以外の文字が入っている場合は前回の状態に合わせる
        condition_txt = condition
    condition = condition_txt

    race_len = int(re.findall("\d+m", soup.find(id="race-data01-a").get_text().replace(',', ''))[0][:-1])  # レースの長さ
    """
    race_len = int(
        soup.find(id="race-data01-a").get_text().replace('\n', '').split('　')[3].replace(',', '')[1:5].replace("m",
                                                                                                               ""))
    """
    race_top = soup.find('tr', class_='bg-1chaku').contents[5].string  # 1位
    race_date = race_day(soup)  # レース日付
    return race_top, condition, race_len, race_date, race_number


# レース日取得
def race_day(soup):  # レース日 datetimeオブジェクトに変換 return datetime.date[y-m-d]
    today = soup.find('span', class_='tx-small').text.strip()
    today = re.split('[年月日]', today)
    del today[-1]
    race_day = datetime.date(year=int(today[0]), month=int(today[1]), day=int(today[2]))
    return race_day


def create_data_frame(url):  # データフレーム作成
    try:
        race_top, condition, race_len, race_date, race_number = result_data(url)  # レース当日データ取得
        # race_top, condition, race_len, race_date, race_number = result_data(url)  理想
    except:
        traceback.print_exc()
        return 1
    print('|{} | R：{:2} | レース距離：{:4} | 1位馬番：{:2} | 土の状態：{:2} '.format(race_date, race_number, race_len, race_top, condition))
    dir = (f"data/race/{race_date}-{race_number}-{race_len}-{condition}-{race_top}/") # csv保存先ディレクトリ
    result_data_refund(url, dir) # 払戻金
    blank_link_list = horse_page_link(url)
    for i in range(len(blank_link_list)):
        horse_data_csv(blank_link_list[i], race_date, i, dir)
        # horse_data_csv(blank_link_list[i], race_date, i, f"data/race/{race_date}-{race_number}-{race_len}-{condition}-{race_top}/")  理想


def create_data():  # 半期分レースに出場した馬のCSVファイル作成
    helf_piriod_race_list = horse_race_list()
    print('--- 各レースに出場している馬(過去レースデータ)をcsvに記録します。 ---')
    print('----------------------------------------------------------------------------')
    now = time.time()
    for i in range(len(helf_piriod_race_list)):  # 半期全レースページを渡す
        create_data_frame(helf_piriod_race_list[i])
    print('レースデータを{}個保存しました。'.format(len(helf_piriod_race_list)))
    print("レースデータ取得処理時間 ：", time.time() - now)

# 並列化 (使うパワー設定は他に作業するのであれば4が良さげ)
def create_data_Thread(MAX_THREAD):  # 半期分レースに出場した馬のCSVファイル作成
    helf_piriod_race_list = horse_race_list()
    print('--- 各レースに出場している馬(過去レースデータ)をcsvに記録します。 ---')
    print('----------------------------------------------------------------------------')
    now = time.time()
    future_list = []
    with futures.ProcessPoolExecutor(max_workers=MAX_THREAD) as executor:
        for i in range(len(helf_piriod_race_list)):
            future = executor.submit(fn=create_data_frame, url=helf_piriod_race_list[i])
            future_list.append(future)
        _ = futures.as_completed(fs=future_list)

    print('レースデータを{}個保存しました。'.format(len(helf_piriod_race_list)))
    print("レースデータ取得処理時間　：", time.time() - now)


def main():
    #result_data_refund("https://www.nankankeiba.com/race_info/2020010221120201.do", f"data/")
    create_data_Thread(MAX_THREAD)
    #create_data()


if __name__ == '__main__':
    main()
