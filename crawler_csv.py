import os

import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import numpy as np


def horse_data_csv(url, date=datetime.date.today(), number=0, dir=None):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    horse_name = soup.find('h2', id="tl-prof").text  # 馬の名称
    horse_birth = soup.find_all('td', class_="w30pr")[0].text  # 馬の誕生日

    # 競走馬詳細データサイト内には表が3つ　その内3つめの出走履歴を取得
    tab = soup.find_all('table', class_='tb01 w100pr bg-over stripe al-center')[2]
    pdList = []
    rows = tab.find_all("tr")
    for i, row in enumerate(rows):
        if i == 0:
            continue

        csvRow = []
        urls = []
        for j, cell in enumerate(row.findAll(['td', 'th'])):
            if j == 0:
                y, m, d = [int(x) for x in cell.get_text().split("/")]
                if y < 50:
                    y += 2000
                else:
                    y += 1900
                if datetime.date(y, m, d) >= date:
                    break
            if j == 3 or j == 14 or j == 16:
                try:
                    urls.append(cell.find("a").get('href'))
                except AttributeError:
                    urls.append(0)

            csvRow.append(cell.get_text().replace('\n', ''))

        if csvRow:
            csvRow += urls
            pdList.append(csvRow)

    df = pd.DataFrame(pdList, columns=['年月日', '競馬場', 'R', 'レース名', '距離', '天候馬場', '馬番', '人気',
                                       '着順', 'タイム', '差/事故', '上3F', 'コーナー通過順', '体重', '騎手',
                                       '負担重量', '調教師', '獲得賞金（円）', 'レース名url', '騎手url', '調教師url'])

    if dir:
        os.makedirs(dir, exist_ok=True)
        number=str(number+1)
        df.to_csv(dir + number + horse_name + horse_birth + ".csv", encoding="SHIFT-JIS")

    return df


def main():
    BLANK_URL = 'https://www.nankankeiba.com/uma_info/2017102763.do'

    day = datetime.date(2019, 11, 9)
    df, _, _ = horse_data_csv(BLANK_URL, day)
    print(df[:])


if __name__ == '__main__':
    main()
