import glob
import datetime
import numpy as np
import pandas as pd
import os
import re
import traceback


def read_csv():
    races = glob.glob("data/test_race/*")


    for race in races:
        year, month, day, roundNumber, length, roadState, top = os.path.basename(race).split("-") # raceファイル名から情報を取得
        print(os.path.basename(race))
        horses = glob.glob(race + "/*.csv") # ファイル内全csvファイルpath取得
        horses = sorted(horses, key=lambda x: int(re.findall("\d+", os.path.basename(x))[0])) # 馬番号順にソート
        race_horse = []
        for i in range(16): # 馬番が多くても16まで
            if len(horses) > i:
                df = pd.read_csv(horses[i], encoding="SHIFT-JIS") # カンマ区切りのデータを読み込むのでread_csv
                df, check = make_race_data(df, 10)

                race_horse.append(df[:10].values)
            else:
                race_horse.append(np.zeros((10, 16)))
        print(df.head())
    print(df.count())


def inZeroOne(num):
    if num > 1:
        return 1
    elif num < 0:
        return 0
    else:
        return num

def make_race_data(df, l=10):
    # ゼロ埋めのpandasデータフレーム作成 (rows=1, columns=16)
    df_ = pd.DataFrame(np.zeros((1, 12)), columns=["horse_cnt", "result_rank", "racecourse", "len", "weather", "soil_condition",
                                                    "popularity", "weight", "sec", "difference", "3_halong", "money"])

    weightLog = 0
    dropList = []
    check = False
    for idx, row in df.iterrows(): # 1行ずつ取り出す
        check = True
        if str(row['着順']) == "nan" or str(row['人気']) == "nan": # nonの場合0
            dropList.append(idx)
            df_.loc[idx] = 0
            continue

        try:
            # 馬場状態
            if row['天候馬場'][-2:] == '/良':
                df_.loc[idx, 'soil_condition'] = 1
            elif row['天候馬場'][-2:] == '/重':
                df_.loc[idx, 'soil_condition'] = 2
            elif row['天候馬場'][-2:] == '稍重':
                df_.loc[idx, 'soil_condition'] = 3
            elif row['天候馬場'][-2:] == '不良':
                df_.loc[idx, 'soil_condition'] = 4
            else:
                df_.loc[idx, 'soil_condition'] = 0

            # 天気
            if row['天候馬場'][0] == '晴':
                df_.loc[idx, 'weather'] = 1
            elif row['天候馬場'][0] == '曇':
                df_.loc[idx, 'weather'] = 2
            elif row['天候馬場'][0] == '雨':
                df_.loc[idx, 'weather'] = 3
            else:
                df_.loc[idx, 'weather'] = 0

            df_.loc[idx, 'money'] = inZeroOne(float(str(row['獲得賞金（円）']).replace(',', '')) / 100000000)
            df_.loc[idx, 'horse_cnt'] = float(str(row['着順']).split('/')[1])
            df_.loc[idx, 'result_rank'] = float(row['着順'].split('/')[0])
            df_.loc[idx, 'len'] = float(re.findall("\d+", str(row['距離']))[0]) / 100
            df_.loc[idx, 'popularity'] = float(row['人気'])
            if row['体重'] == "計不":
                df_.loc[idx, 'weight'] = weightLog
                """
                if weightLog == 0:
                    dropList.append(idx)
                """

            else:
                df_.loc[idx, 'weight'] = (float(row['体重']))
                weightLog = (float(row['体重']))

            # 　競馬場
            if row['競馬場'][:2] == "浦和":
                df_.loc[idx, 'racecourse'] = 1
            elif row['競馬場'][:2] == "船橋":
                df_.loc[idx, 'racecourse'] = 2
            elif row['競馬場'][:2] == "大井":
                df_.loc[idx, 'racecourse'] = 3
            elif row['競馬場'][:2] == "川崎":
                df_.loc[idx, 'racecourse'] = 4
            else:
                df_.loc[idx, 'racecourse'] = 0

            # 差/事故
            try:
                df_.loc[idx, 'difference'] = float(row['差/事故'])
            except:
                df_.loc[idx, 'difference'] = 0

            # 上3F（3ハロン）
            try:
                df_.loc[idx, '3_halong'] = float(row['上3F'])
            except:
                df_.loc[idx, '3_halong'] = 0

            print(row['コーナー通過順'])

            # タイム(秒)
            try:
                time = datetime.datetime.strptime(str(row['タイム']), '%M:%S.%f')
                df_.loc[idx, 'sec'] = float(time.minute * 60 + time.second + time.microsecond / 1000000)
            except:
                time = datetime.datetime.strptime(str(row['タイム']), '%S.%f')
                df_.loc[idx, 'sec'] = float(time.second + time.microsecond / 1000000)

        except:  # エラーなら全部0
            traceback.print_exc()
            dropList.append(idx)
            df_.loc[idx] = 0

    for i in dropList:
        df_.drop(i, axis=0, inplace=True)
    if not check:
        df_.drop(0, axis=0, inplace=True)

    leng = len(df_)
    if leng == 0:
        check = False
    else:
        check = True

    while len(df_) < l:
        df_.loc[len(df_) + len(dropList)] = 0

    return df_, check


def main():
    read_csv()


if __name__ == '__main__':
    main()
