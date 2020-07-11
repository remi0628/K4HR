import re
import datetime
import requests
from bs4 import BeautifulSoup as bs4
from urllib.request import urlopen, urljoin, urlparse

HOME_URL = 'https://www.nankankeiba.com'
####  https://www.nankankeiba.com/uma_shosai/
URL = 'https://www.nankankeiba.com/uma_shosai/2020071020060501.do'

TXT_PATH = './data/uma.txt'

def main():
    day, list = horse_page_link(URL)
    text_write(day)


def url_to_soup(url): # レース情報ページ取得
    html = urlopen(URL)
    return bs4(html, 'lxml')

def horse_page_link(url): # 各馬の過去情報URL取得 　return（レース日[y-m-d], 過去情報[URL]）
    blank_link_list = []
    soup = url_to_soup(url)
    race_today = race_day(soup)
    for tx_mid in soup.find_all('span', class_='tx-mid'):
        for uma_data_link in tx_mid.find_all('a'):
            blank_link_list.append(HOME_URL + uma_data_link.get('href'))
    print(race_today, blank_link_list)
    return race_today, blank_link_list

def race_day(soup): # レース日 datetimeオブジェクトに変換 return[y-m-d]
    race_len = int(soup.find(id="race-data01-a").get_text().replace('\n','').split('　')[3].replace(',','')[1:5])
    condition = soup.find(id="race-data02").get_text().replace('\n','').split('　')[2][0:1]
    today = soup.find('span', class_='tx-small').text.strip()
    today = re.split('[年月日]', today)
    del today[-1]
    race_day = datetime.date(year=int(today[0]), month=int(today[1]), day=int(today[2]))
    return race_day

def horse_race_data(soup):
    soup = url_to_soup(url)
    #for tx_mid in soup.find_all('span', class_='tx-mid'):


def text_write(data): # 入ってきたものをtxtに記述　確認用
    with open(TXT_PATH, 'w', encoding='UTF-8') as file:
        file.write(str(data))


if __name__ == '__main__':
    main()
