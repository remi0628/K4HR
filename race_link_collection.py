import urllib
import requests
from bs4 import BeautifulSoup


def race_list_the_day(url):
    race_list = []
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    table = soup.find_all("table")
    for tab in table:
        table_class = tab.get("class")
        if table_class[0] == "tb01c": # レースtable取得
            rows = tab.find_all("tr")
            for row in rows:
                for cell in row.findAll(['td', 'th']):
                    for a in cell.find_all('a'):
                        if 'race_info' in a.get('href'): # href=''リンク内に[race_info]があるURLのみ取得 レースの出走表
                            print(a)
                            race_list.append(a.get('href'))
            print(race_list)
            break
    return race_list


def main():
    BLANK_URL = 'https://www.nankankeiba.com/program/20200710200605.do'
    horse_path = race_list_the_day(BLANK_URL)
    #print(horse_path)


if __name__ == '__main__':
    main()
