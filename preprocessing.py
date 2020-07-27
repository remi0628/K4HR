import glob
import datetime
import numpy as np
import pandas as pd
import os
import re
import traceback


def read_csv():
    races = glob.glob("data/race/*")

    X = []
    Y = []
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
        X.append(race_horse)

    X = np.array(X)
    Y = np.array(Y)
    X = X.astype("float")
    np.save("data/X.npy", X)
    np.save("data/Y.npy", Y)


def inZeroOne(num):
    if num > 1:
        return 1
    elif num < 0:
        return 0
    else:
        return num


def make_race_data(df, l=10):
    # ゼロ埋めのpandasデータフレーム作成 (rows=1, columns=16)
    df_ = pd.DataFrame(np.zeros((1, 16)), columns=["horse_cnt", "money", "result_rank", "len", "popularity", "weight", "sec",
                                                   "place_Urawa", "place_Funabashi", "place_Ooi", "place_Kawasaki", "place_other",
                                                   "soil_heavy", "soil_s_heavy", "soil_good", "soil_bad"])
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
            df_.loc[idx, 'soil_heavy'] = 1 if row['天候馬場'][-2:] == '/重' else 0
            df_.loc[idx, 'soil_s_heavy'] = 1 if row['天候馬場'][-2:] == '稍重' else 0
            df_.loc[idx, 'soil_good'] = 1 if row['天候馬場'][-2:] == '/良' else 0
            df_.loc[idx, 'soil_bad'] = 1 if row['天候馬場'][-2:] == '不良' else 0

            df_.loc[idx, 'money'] = inZeroOne(float(str(row['獲得賞金（円）']).replace(',', '')) / 110000000)
            df_.loc[idx, 'horse_cnt'] = float(str(row['着順']).split('/')[1]) / 16
            df_.loc[idx, 'result_rank'] = float(row['着順'].split('/')[0]) / 16
            df_.loc[idx, 'len'] = inZeroOne((float(re.findall("\d+", str(row['距離']))[0]) - 800) / 3000)
            df_.loc[idx, 'popularity'] = float(row['人気']) / 16
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
            df_.loc[idx, 'place_Urawa'] = 1 if row['競馬場'][:2] == "浦和" else 0
            df_.loc[idx, 'place_Funabashi'] = 1 if row['競馬場'][:2] == "船橋" else 0
            df_.loc[idx, 'place_Ooi'] = 1 if row['競馬場'][:2] == "大井" else 0
            df_.loc[idx, 'place_Kawasaki'] = 1 if row['競馬場'][:2] == "川崎" else 0

            if df_.loc[idx, 'place_Urawa'] + df_.loc[idx, 'place_Funabashi'] + df_.loc[idx, 'place_Ooi'] + df_.loc[
                idx, 'place_Kawasaki'] == 0:
                df_.loc[idx, 'place_other'] = 1
            else:
                df_.loc[idx, 'place_other'] = 0

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
