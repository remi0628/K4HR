import re
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs4
from urllib.request import urlopen, urljoin, urlparse

HOME_URL = 'https://www.nankankeiba.com'
#### https://www.nankankeiba.com/race_info/
URL = 'https://www.nankankeiba.com/race_info/2020071020060501.do'
BLANK_URL = 'https://www.nankankeiba.com/uma_info/2017100322.do'


def main():
    soup = url_to_soup(BLANK_URL)
    print(horse_data(BLANK_URL))
    #print(result_data(URL))


def url_to_soup(url): # レース情報ページ取得
    req = requests.get(url)
    return bs4(req.content, 'html.parser')

def horse_page_link(url): # 各馬の過去情報URL取得
    soup = url_to_soup(url)
    link_list = [HOME_URL + x.get('href') for x in soup.find_all('a', class_='tx-mid tx-low') ]
    return link_list

tag_to_text = lambda x: x.split('\n')
split_tr = lambda x: str(x).split('</tr>')

def get_previous_race_row(soup):
    race_table = soup.find_all('table', class_='tb01 w100pr bg-over stripe al-center')[2]
    return [tag_to_text(x) for x in split_tr(race_table)]

def horse_data(url):
    soup = url_to_soup(url)
    # 過去のレースデータ
    pre_race_data = get_previous_race_row(soup)
    df = pd.DataFrame(pre_race_data)[1:][[2,3,10,11,13,14,15,19,23]].dropna().rename(columns={
        2:'date', 3:'place', 10:'len', 11:'wether', 13:'popularity', 14:'rank', 15:'time',19:'weight',23:'money'})
    return df



def result_data(url): # レース結果取得 return[1着馬, 土の状態, レースの長さ, レース日]
    soup = url_to_soup(url)
    condition = soup.find(id="race-data02").get_text().replace('\n','').split('　')[2][0:1] # 土の状態
    race_len = int(soup.find(id="race-data01-a").get_text().replace('\n','').split('　')[3].replace(',','')[1:5]) # レースの長さ
    top = soup.find('td', class_='bg-3 al-center').get_text() # 1位
    race_date = race_day(soup)
    return top, condition, race_len, race_date

def race_day(soup): # レース日 datetimeオブジェクトに変換 return datetime.date[y-m-d]
    today = soup.find('span', class_='tx-small').text.strip()
    today = re.split('[年月日]', today)
    del today[-1]
    race_day = datetime.date(year=int(today[0]), month=int(today[1]), day=int(today[2]))
    return race_day
    

if __name__ == '__main__':
    main()
