import urllib
import requests
import datetime
from bs4 import BeautifulSoup

HOME_URL = 'https://www.nankankeiba.com'
RACE_PROGRAM_URL = 'https://www.nankankeiba.com/program/20200710200605.do'
RACE_LIST_HELF_PERIOD = 'https://www.nankankeiba.com/calendar/202004.do'
# RACE_PROGRAM_URL = '/program/20190401210101.do'
MAX_DATE = datetime.date(year=2020, month=7, day=10)

# 1日のレース一覧ページを渡すと12R全てリンクを取得してくる
def race_list_day(race_program_url): #
    race_list = []
    soup = BeautifulSoup(requests.get(race_program_url).content, 'html.parser')
    table = soup.find_all("table")
    for tab in table:
        table_class = tab.get("class")
        if table_class[0] == "tb01c": # レースtable取得
            rows = tab.find_all("tr")
            for row in rows:
                for cell in row.findAll(['td', 'th']):
                    for a in cell.find_all('a'):
                        if 'race_info' in a.get('href'): # href=''リンク内に[race_info]があるURLのみ取得 レースの出走表
                            race_day = give_date(a.get('href')) # レース日取得
                            race_list.append(HOME_URL + a.get('href'))
    print('{}：レース数：{}  リンクを取得しました。'.format(race_day, len(race_list)))
    return race_list


# 半期のレースページを渡すと全ての日程のレースurlを取得してくる
def race_half_program_list(race_half_period_calendar_url): #
    race_program_list = []
    half_period = ""
    msg = ""
    soup = BeautifulSoup(requests.get(race_half_period_calendar_url).content, 'html.parser')
    table = soup.find_all("table")
    for tab in table:
        table_class = tab.get("class")
        if table_class[0] == "tb-calendar": # 月の開催日程table取得
            rows = tab.find_all("tr")
            for row in rows:
                for cell in row.findAll(['td', 'th']):
                    for a in cell.find_all('a'):
                        if 'program' in a.get('href'): # href=''リンク内に[program]があるURLのみ取得 当日レースのプログラム12R
                            race_day = give_date(a.get('href')) # レース日取得
                            if race_day <= MAX_DATE:            # MAX_DATE以前のレースをリストに入れる
                                race_program_list.append(HOME_URL + a.get('href'))
                            else:
                                msg = "\n指定した取得最大日程：{}に達しました。".format(MAX_DATE)
    if race_day.month in (4, 5, 6, 7, 8, 9):
        half_period = "前期(4～9月)"
    elif race_day.month in (1, 2, 3, 10, 11, 12):
        half_period = "後期(10～3月)"
    print('{}年レース年間開催日程 {}から{}日分のリンクを取得しました。{}'.format( race_day.year, half_period, str(len(race_program_list)), msg))
    return race_program_list


def give_date(race_program_url): # urlからレース日を取得
    day = ""
    if 'program' in race_program_url:
        day = datetime.date(year=int(race_program_url[9:13]), month=int(race_program_url[13:15]), day=int(race_program_url[15:17]))
    elif 'race_info' in race_program_url:
        day = datetime.date(year=int(race_program_url[11:15]), month=int(race_program_url[15:17]), day=int(race_program_url[17:19]))
    return day


def main():
    #race_program_url_list = race_half_program_list(RACE_LIST_HELF_PERIOD)
    race_list_day(RACE_PROGRAM_URL)
    #for i in  range(len(race_program_url_list)):
        #race_list_day(race_program_url_list[i])
    #print(race_program_url)
    #race_program_list = race_list_day(RACE_PROGRAM_URL)
    #print(MAX_DATE)


if __name__ == '__main__':
    main()
