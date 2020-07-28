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
                if datetime.date(y, m, d) > date:
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


# 当日データ（払戻金）
def result_data_refund(url, dir=None):
    pdList = []
    csvRow = []
    csvRow2 = []
    count = 0
    result_url = url[0:28] + 'result' + url[-20:]
    soup = BeautifulSoup(requests.get(result_url).content, 'html.parser')
    # 払戻金テーブル一つ目
    table = soup.find_all('table', class_='tb01 w100pr bg-over')[-2]
    rows = table.find_all("tr")
    for row in rows:
        for cell in row.findAll(['td', 'th']):
            if count >= 24 and 41 >= count or count >= 45 and 47 >= count or count >= 63 and 65 >= count:
                if cell.get_text() != '-':
                    csvRow.append(cell.get_text().strip('円').replace('\n', ''))
                else:
                    csvRow.append(0)
            count += 1
    if len(csvRow) != 24: # 複勝が1, 2枠しかない場合
        i = 24 - len(csvRow)
        for add in range(i):
            csvRow.append(0)
    # 払戻金テーブル二つ目
    count = 0
    table = soup.find_all('table', class_='tb01 w100pr bg-over')[-1]
    rows = table.find_all("tr")
    for row in rows:
        for cell in row.findAll(['td', 'th']):
            if count >= 14 and 25 >= count or count >= 32 and 34 >= count:
                if cell.get_text() != '-':
                    csvRow2.append(cell.get_text().strip('円').replace('\n', ''))
                else:
                    csvRow.append(0)
            count += 1
    if len(csvRow2) != 15: # ワイドが1, 2枠しかない場合（実際あるか分からない）
        i = 15 - len(csvRow2)
        for add in range(i):
            csvRow.append(0)
    # データ結合
    csvRow += csvRow2
    pdList.append(csvRow)
    # dfへ整えてからcsv保存
    df = pd.DataFrame(pdList, index=[0], columns=['単勝_組番', '単勝_金額', '単勝_人気', '複勝_組番', '複勝_金額', '複勝_人気',
                                                             '枠複_組番', '枠複_金額', '枠複_人気', '普通馬腹_組番', '普通馬腹_金額', '普通馬腹_人気',
                                                             '枠単_組番', '枠単_金額', '枠単_人気', '馬単_組番', '馬単_金額', '馬単_人気',
                                                             '複勝2_組番', '複勝2_金額', '複勝2_人気', '複勝3_組番', '複勝3_金額', '複勝3_人気',
                                                             'ワイド_組番', 'ワイド_金額', 'ワイド_人気', '三連複_組番', '三連複_金額', '三連複_人気',
                                                             '三連単_組番', '三連単_金額', '三連単_人気', 'ワイド2_組番', 'ワイド2_金額', 'ワイド2_人気',
                                                             'ワイド3_組番', 'ワイド3_金額', 'ワイド3_人気',])
    if dir:
        os.makedirs(dir, exist_ok=True)
        df.to_csv(dir +"refund" + ".csv", encoding="SHIFT-JIS")


def main():
    result_data_refund("https://www.nankankeiba.com/race_info/2019040121010101.do", f"data/")
    """
    BLANK_URL = 'https://www.nankankeiba.com/uma_info/2017102763.do'
    day = datetime.date(2019, 11, 9)
    df = horse_data_csv(BLANK_URL, day)
    print(df)
    """


if __name__ == '__main__':
    main()
