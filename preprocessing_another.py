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
        horses = sorted(horses[0:-1], key=lambda x: int(re.findall("\d+", os.path.basename(x))[0])) # 馬番号順にソート
        race_horse = []
        for i in range(16): # 馬番が多くても16まで
            if len(horses) > i:
                df = pd.read_csv(horses[i], encoding="cp932") # カンマ区切りのデータを読み込むのでread_csv
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

def make_race_data(df, l=10): # 取得するのは過去のデータ10件まで
    # ゼロ埋めのpandasデータフレーム作成 (rows=1, columns=16)
    df_ = pd.DataFrame(np.zeros((1, 16)), columns=["horse_cnt", "result_rank", "racecourse", "len", "weather", "soil_condition",
                                                    "popularity", "weight", "borden_weight",
                                                    "sec", "diff_accident", "threeF", "corner_order_1", "corner_order_2", "corner_order_3", "money"])

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
                df_.loc[idx, 'soil_condition'] = float(0.25)
            elif row['天候馬場'][-2:] == '/重':
                df_.loc[idx, 'soil_condition'] = float(0.5)
            elif row['天候馬場'][-2:] == '稍重':
                df_.loc[idx, 'soil_condition'] = float(0.75)
            elif row['天候馬場'][-2:] == '不良':
                df_.loc[idx, 'soil_condition'] = float(1)
            else:
                df_.loc[idx, 'soil_condition'] = 0

            # 天気
            if row['天候馬場'][0] == '晴':
                df_.loc[idx, 'weather'] = float(0.3)
            elif row['天候馬場'][0] == '曇':
                df_.loc[idx, 'weather'] = float(0.6)
            elif row['天候馬場'][0] == '雨':
                df_.loc[idx, 'weather'] = float(0.9)
            else:
                df_.loc[idx, 'weather'] = 0

            df_.loc[idx, 'money'] = inZeroOne(float(str(row['獲得賞金（円）']).replace(',', '')) / 110000000)
            df_.loc[idx, 'horse_cnt'] = float(str(row['着順']).split('/')[1]) / 16
            df_.loc[idx, 'result_rank'] = float(row['着順'].split('/')[0]) / 16
            df_.loc[idx, 'len'] = inZeroOne((float(re.findall("\d+", str(row['距離']))[0]) - 800) / 3000)
            df_.loc[idx, 'popularity'] = float(row['人気']) / 16
            df_.loc[idx, 'borden_weight'] = inZeroOne((float(row['負担重量']) - 50) / 10)
            if row['体重'] == "計不":
                df_.loc[idx, 'weight'] = weightLog
                """
                if weightLog == 0:
                    dropList.append(idx)
                """
            else:
                df_.loc[idx, 'weight'] = inZeroOne((float(row['体重']) - 300) / 300)
                weightLog = inZeroOne((float(row['体重']) - 300) / 300)

            # 　競馬場
            if row['競馬場'][:2] == "浦和" or row['競馬場'][:2] == "浦和☆":
                df_.loc[idx, 'racecourse'] = float(0.25)
            elif row['競馬場'][:2] == "船橋" or row['競馬場'][:2] == "船橋☆":
                df_.loc[idx, 'racecourse'] = float(0.5)
            elif row['競馬場'][:2] == "大井" or row['競馬場'][:2] == "大井☆":
                df_.loc[idx, 'racecourse'] = float(0.75)
            elif row['競馬場'][:2] == "川崎" or row['競馬場'][:2] == "川崎☆":
                df_.loc[idx, 'racecourse'] = float(1)
            else:
                df_.loc[idx, 'racecourse'] = 0

            # 差/事故
            try:
                df_.loc[idx, 'diff_accident'] = inZeroOne(float(row['差/事故']) / 10)
            except:
                df_.loc[idx, 'diff_accident'] = 0

            # 上3F（3ハロン）
            try:
                df_.loc[idx, 'threeF'] = inZeroOne((float(row['上3F']) - 30) / 30)
            except:
                df_.loc[idx, 'threeF'] = 0

            # コーナー通過順
            try:
                df_.loc[idx, 'corner_order_1'] = float(row['コーナー通過順'].split('-')[0]) / 16
            except:
                df_.loc[idx, 'corner_order_1'] = 0
            try:
                df_.loc[idx, 'corner_order_2'] = float(row['コーナー通過順'].split('-')[1]) / 16
            except:
                df_.loc[idx, 'corner_order_2'] = 0
            try:
                df_.loc[idx, 'corner_order_3'] = float(row['コーナー通過順'].split('-')[2]) / 16
            except:
                df_.loc[idx, 'corner_order_3'] = 0

            # タイム(秒)
            try:
                time = datetime.datetime.strptime(str(row['タイム']), '%M:%S.%f')
                df_.loc[idx, 'sec'] = inZeroOne(
                    (float(time.minute * 60 + time.second + time.microsecond / 1000000) - 40) / 250)
            except:
                time = datetime.datetime.strptime(str(row['タイム']), '%S.%f')
                df_.loc[idx, 'sec'] = inZeroOne((float(time.second + time.microsecond / 1000000) - 40) / 250)

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
