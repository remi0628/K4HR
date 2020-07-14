import re
import datetime
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs4
from urllib.request import urlopen, urljoin, urlparse

import crawler_settings  # crawlerの設定ファイル
from crawler_csv import horse_data_csv # 馬の詳細URL渡してcsvファイル作成
from race_link_collection import horse_race_list # 半期開催日程URLを渡すと半期分のレースURLを返す

CSV_DATA_PATH = crawler_settings.CSV_DATA_PATH
HOME_URL = crawler_settings.HOME_URL
#### https://www.nankankeiba.com/race_info/
URL = 'https://www.nankankeiba.com/race_info/2020060120040101.do'
BLANK_URL = 'https://www.nankankeiba.com/uma_info/2017100322.do'
RACE_LIST_HELF_PERIOD = 'https://www.nankankeiba.com/calendar/202004.do'


def url_to_soup(url): # レース情報ページ取得
    req = requests.get(url)
    return bs4(req.content, 'html.parser') # 'lmxl'より処理が速い

def horse_page_link(url): # 各馬の過去情報URLリスト取得
    soup = url_to_soup(url)
    link_list = [HOME_URL + x.get('href') for x in soup.find_all('a', class_='tx-mid tx-low') ] # サイト内リンクから過去情報リンクのみ取得
    return link_list

# lamda
tag_to_text = lambda x: x.split('\n')
split_tr = lambda x: str(x).split('</tr>')

def get_previous_race_row(soup): # 競走馬詳細データから出走履歴取得
    race_table = soup.find_all('table', class_='tb01 w100pr bg-over stripe al-center')[2] # 競走馬詳細データサイト内には表が3つ　その内3つめの出走履歴を取得
    return [tag_to_text(x) for x in split_tr(race_table)]

'''
def horse_data(url): # 出走履歴からデータ作成
    soup = url_to_soup(url)
    blank_race_data = get_previous_race_row(soup) # 過去のレースデータ
    # print('出走履歴1番目の日付：', re.split('[<>]' ,blank_race_data[1:2][0][2])[2])
    # print(len(blank_race_data))
    #blank_race_day_calc(blank_race_data)
    #print(re.split('[<>]' ,blank_race_data))
    df =  pd.DataFrame(blank_race_data)[1:][[2,3,10,11,13,14,15,19,23]].dropna().rename(columns={
        2:'date', 3:'place', 10:'len', 11:'wether', 13:'popularity', 14:'rank', 15:'time',19:'weight',23:'money'})
    return df

def blank_race_day_calc(blank_race_data): # 出走履歴何番目を取得するかレース当日と日付計算判定
    data_len = blank_race_data[1:] # len(data_len)-1 : 出走履歴数
    for i in range((len(data_len)-1)):
        day = re.split('[<>]' ,data_len[i][2])[2].split('/')
        year = '20' + day[0]
        race_day = datetime.date(year=int(year), month=int(day[1]), day=int(day[2])) # datetime.datetimeオブジェクト y-m-d
        print(race_day)
'''

# 当日データ取得
def result_data(url): # レース結果取得 return[1着馬, 土の状態, レースの長さ, レース日]
    result_url = url[0:28] + 'result' + url[-20:]
    print(result_url)
    soup = url_to_soup(result_url)
    condition = soup.find(id="race-data02").get_text().replace('\n','').split('　')[2][0:1] # 土の状態
    race_len = int(soup.find(id="race-data01-a").get_text().replace('\n','').split('　')[3].replace(',','')[1:5]) # レースの長さ
    race_top = soup.find('tr', class_='bg-1chaku').contents[5].string # 1位
    race_date = race_day(soup) # レース日付
    return race_top, condition, race_len, race_date

# レース日取得
def race_day(soup): # レース日 datetimeオブジェクトに変換 return datetime.date[y-m-d]
    today = soup.find('span', class_='tx-small').text.strip()
    today = re.split('[年月日]', today)
    del today[-1]
    race_day = datetime.date(year=int(today[0]), month=int(today[1]), day=int(today[2]))
    return race_day


def create_data_frame(url): #データフレーム作成
    df = []
    race_top, condition, race_len, race_date = result_data(url) # レース当日データ取得
    print('#レース当日データ#\n', '日付：{}, レース距離：{}, 土の状態：{}, 1位馬番：{}'.format(race_date, race_len, condition, race_top))
    blank_link_list = horse_page_link(url)
    for i in range(len(blank_link_list)):
        horse_path = horse_data_csv(blank_link_list[i], race_date, CSV_DATA_PATH)
        #df.append(pd.read_csv(horse_path, encoding='SHIFT-JIS')) # テスト時はコメントアウト
    return horse_path


def create_data_csv(url): # 半期分レースに出場した馬のCSVファイル作成
    horse_path_list = []
    helf_piriod_race_list = horse_race_list(url)
    for i in range(len(helf_piriod_race_list)): # 半期全レースページを渡す
        horse_path_list.append(create_data_frame(helf_piriod_race_list[i]))
    print('馬のデータを{}個CSVデータにしました。'.format(len(horse_path_list)))
    return list(itertools.chain.from_iterable(horse_path_list)) # 2次元リストを1次元リストに平坦化


def main():
    create_data_csv(RACE_LIST_HELF_PERIOD)



if __name__ == '__main__':
    main()
