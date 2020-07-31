import glob
import time
import datetime
import numpy as np
import pandas as pd
import os
import re
import traceback
from concurrent import futures
from decimal import Decimal, ROUND_DOWN

import crawler_settings
FILE_NUM = crawler_settings.FILE_NUM
SWITTCH_NUM = crawler_settings.SWITTCH_NUM


### (レース数, 過去レース数, 特徴量)
global horse_id
global race_horse_2
race_horse_2 = []
horse_id = 0
def read_csv_2(race, date):
    print(os.path.basename(race))
    horses = glob.glob(race + "/*.csv")
    horses = sorted(horses[0:-1], key=lambda x: int(re.findall("\d+", os.path.basename(x))[0]))

    global horse_id
    for i in range(16):
        if len(horses) > i:
            global race_horse_2
            horse_id += float(0.00001)# [0.00001]最大10万馬まで登録
            birth = [int(x) for x in re.findall("\d+", horses[i])[-3:]]
            df = pd.read_csv(horses[i], encoding="cp932")
            df = make_race_data_2(df, date, birth, 10)
            # print('{0:.5f}'.format(Decimal(horse_id))) # 馬のid
            race_horse_2.append(df[:10].values)
        else:
            race_horse_2.append(np.zeros((10, 18)))
    return race_horse_2


def make_npy_2():
    races = glob.glob("data/data_jupyter_race/*")

    global race_horse_2
    future_list = []
    with futures.ProcessPoolExecutor(max_workers=None) as executor:
        for i in range(len(races)):
            year, month, day, roundNumber, length, roadState, top = os.path.basename(races[i]).split("-")
            read_csv_2(race=races[i], date=[year, month, day])

    print('格納データ数：' + str(len(race_horse_2)) )
    X = np.array(race_horse_2)
    X = X.astype("float")
    np.save("data/data_jupyter/dim_2/X.npy", X)


def make_race_data_2(df, date, birth, l=10):
    df_ = pd.DataFrame(np.zeros((1, 18)), columns=["horse_id", "horse_cnt", "result_rank", "racecourse", "len", "weather", "soil_condition",
                                                    "popularity", "weight", "borden_weight", "birth_days",
                                                    "sec", "diff_accident", "threeF", "corner_order_1", "corner_order_2", "corner_order_3", "money"])
    weightLog = 0
    dropList = []
    check = False
    ranking = 0
    for idx, row in df.iterrows():
        check = True
        if str(row['着順']) == "nan" or str(row['人気']) == "nan" or str(row['タイム']) == "nan":
            dropList.append(idx)
            df_.loc[idx] = 0
            continue

        try:
            # 馬id登録
            df_.loc[idx, 'horse_id'] = float(horse_id)

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

            # タイム(秒)
            try:
                time = datetime.datetime.strptime(str(row['タイム']), '%M:%S.%f')
                df_.loc[idx, 'sec'] = inZeroOne(
                    (float(time.minute * 60 + time.second + time.microsecond / 1000000) - 40) / 250)
            except:
                time = datetime.datetime.strptime(str(row['タイム']), '%S.%f')
                df_.loc[idx, 'sec'] = inZeroOne((float(time.second + time.microsecond / 1000000) - 40) / 250)

            # 上3F（3ハロン）
            try:
                df_.loc[idx, 'threeF'] = inZeroOne((float(row['上3F']) - 30) / 30)
            except ValueError:
                df_.loc[idx, 'threeF'] = 0

            # 差/事故
            try:
                df_.loc[idx, 'diff_accident'] = inZeroOne(float(row['差/事故']) / 10)
            except ValueError:
                df_.loc[idx, 'diff_accident'] = 0

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

            # レース日
            raceDay = [int(x) for x in row['年月日'].split("/")]
            date = [int(x) for x in date]
            if raceDay[0] < 50:
                raceDay[0] += 2000
            elif raceDay[0] < 1900:
                raceDay[0] += 1900

            birthDate = datetime.date(raceDay[0], raceDay[1], raceDay[2]) - datetime.date(birth[0], birth[1], birth[2])
            df_.loc[idx, 'birth_days'] = inZeroOne((birthDate.days - 700) / 1000)

        except:  # エラーなら全部0
            traceback.print_exc()
            dropList.append(idx)
            df_.loc[idx] = 0

    for i in dropList:
        df_.drop(i, axis=0, inplace=True)
    if not check:
        df_.drop(0, axis=0, inplace=True)


    while len(df_) < l:
        df_.loc[len(df_) + len(dropList)] = 0

    return df_



### (当日レース, 出馬数, 過去10レース, 特徴量)
def read_csv(race, date):
    print(os.path.basename(race))
    horses = glob.glob(race + "/*.csv")
    horses = sorted(horses[0:-1], key=lambda x: int(re.findall("\d+", os.path.basename(x))[0]))

    race_horse = []
    rankings = np.zeros(16)
    for i in range(16):
        if len(horses) > i:
            birth = [int(x) for x in re.findall("\d+", horses[i])[-3:]]
            df = pd.read_csv(horses[i], encoding="cp932")
            df, ranking = make_race_data(df, date, birth, 10)
            print(ranking)
            if ranking != 0:  # 欠場等でないなら
                if rankings[ranking - 1] == 0:  # 同着の場合来た順に次に、本来払い戻し等どう処理されるか調べる必要性あり
                    rankings[ranking - 1] = int(re.findall("\d+", os.path.basename(horses[i]))[0])
                else:
                    rankings[ranking] = int(re.findall("\d+", os.path.basename(horses[i]))[0])

            race_horse.append(df[:10].values)
        else:
            race_horse.append(np.zeros((10, 17)))

    return race_horse, rankings


def make_npy():
    races = glob.glob("data/data_jupyter_race/*")

    future_list = []
    with futures.ProcessPoolExecutor(max_workers=None) as executor:
        for i in range(len(races)):
            year, month, day, roundNumber, length, roadState, top = os.path.basename(races[i]).split("-")
            future = executor.submit(fn=read_csv, race=races[i], date=[year, month, day])
            future_list.append(future)
        _ = futures.as_completed(fs=future_list)

    X = [future.result()[0] for future in future_list]
    Y = [future.result()[1] for future in future_list]

    X = np.array(X)
    Y = np.array(Y)
    X = X.astype("float")
    np.save("data/data_jupyter/dim_4/X.npy", X)
    np.save("data/data_jupyter/dim_4/Y.npy", Y)

def inZeroOne(num):
    if num > 1:
        return 1
    elif num < 0:
        return 0
    else:
        return num


def make_race_data(df, date, birth, l=10):
    df_ = pd.DataFrame(np.zeros((1, 17)), columns=["horse_cnt", "result_rank", "racecourse", "len", "weather", "soil_condition",
                                                    "popularity", "weight", "borden_weight", "birth_days",
                                                    "sec", "diff_accident", "threeF", "corner_order_1", "corner_order_2", "corner_order_3", "money"])
    weightLog = 0
    dropList = []
    check = False
    ranking = 0
    for idx, row in df.iterrows():
        check = True
        if str(row['着順']) == "nan" or str(row['人気']) == "nan" or str(row['タイム']) == "nan":
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

            # タイム(秒)
            try:
                time = datetime.datetime.strptime(str(row['タイム']), '%M:%S.%f')
                df_.loc[idx, 'sec'] = inZeroOne(
                    (float(time.minute * 60 + time.second + time.microsecond / 1000000) - 40) / 250)
            except:
                time = datetime.datetime.strptime(str(row['タイム']), '%S.%f')
                df_.loc[idx, 'sec'] = inZeroOne((float(time.second + time.microsecond / 1000000) - 40) / 250)

            # 上3F（3ハロン）
            try:
                df_.loc[idx, 'threeF'] = inZeroOne((float(row['上3F']) - 30) / 30)
            except ValueError:
                df_.loc[idx, 'threeF'] = 0

            # 差/事故
            try:
                df_.loc[idx, 'diff_accident'] = inZeroOne(float(row['差/事故']) / 10)
            except ValueError:
                df_.loc[idx, 'diff_accident'] = 0

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

            # レース日
            raceDay = [int(x) for x in row['年月日'].split("/")]
            date = [int(x) for x in date]
            if raceDay[0] < 50:
                raceDay[0] += 2000
            elif raceDay[0] < 1900:
                raceDay[0] += 1900

            birthDate = datetime.date(raceDay[0], raceDay[1], raceDay[2]) - datetime.date(birth[0], birth[1], birth[2])
            df_.loc[idx, 'birth_days'] = inZeroOne((birthDate.days - 700) / 1000)

            if raceDay == date:  # 当日の場合不明なもの
                ranking = int(row['着順'].split('/')[0])
                df_.loc[idx, 'money'] = 0
                df_.loc[idx, 'result_rank'] = 0
                df_.loc[idx, 'popularity'] = 0
                df_.loc[idx, 'sec'] = 0
                df_.loc[idx, 'weight'] = 0
                df_.loc[idx, 'diff_accident'] = 0
                df_.loc[idx, 'threeF'] = 0

        except:  # エラーなら全部0
            traceback.print_exc()
            dropList.append(idx)
            df_.loc[idx] = 0

    for i in dropList:
        df_.drop(i, axis=0, inplace=True)
    if not check:
        df_.drop(0, axis=0, inplace=True)


    while len(df_) < l:
        df_.loc[len(df_) + len(dropList)] = 0

    return df_, ranking


def program_switch():
    if SWITTCH_NUM == 1:
        make_npy()
    if SWITTCH_NUM == 2:
        make_npy_2()


def main():
    now = time.time()
    program_switch()
    print("レースデータ前処理時間　：", time.time() - now)


if __name__ == '__main__':
    main()
