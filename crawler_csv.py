import csv
import requests
from bs4 import BeautifulSoup
import datetime


def horse_data_csv(url, date=datetime.date.today(), folder=""):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    horse_name = soup.find('h2', id="tl-prof").text  # 馬の名称
    horse_birth = soup.find_all('td', class_="w30pr")[0].text  # 馬の誕生日

    csv_name = folder + horse_birth + horse_name + date.strftime('%Y-%m-%d') + ".csv"

    # 競走馬詳細データサイト内には表が3つ　その内3つめの出走履歴を取得
    tab = soup.find_all('table', class_='tb01 w100pr bg-over stripe al-center')[2]
    with open(csv_name, "w", newline="", encoding='SHIFT-JIS') as file:
        writer = csv.writer(file)
        rows = tab.find_all("tr")
        for i, row in enumerate(rows):
            if i == 0:
                writer.writerow(['年月日', '競馬場', 'R', 'レース名', '距離', '天候馬場', '馬番', '人気',
                                 '着順', 'タイム', '差/事故', '上3F', 'コーナー通過順', '体重', '騎手',
                                 '負担重量', '調教師', '獲得賞金（円）', 'レース名url', '騎手url', '調教師url'])
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
                    urls.append(cell.find("a").get('href'))

                csvRow.append(cell.get_text().replace('\n', ''))

            if csvRow:
                csvRow += urls
                writer.writerow(csvRow)

    return csv_name


def main():
    BLANK_URL = 'https://www.nankankeiba.com/uma_info/2017102763.do'

    day = datetime.date(2019, 12, 9)
    horse_path = horse_data_csv(BLANK_URL, day, "data/")
    print(horse_path)

    import pandas as pd
    df = pd.read_csv(horse_path)
    print(df)


if __name__ == '__main__':
    main()
