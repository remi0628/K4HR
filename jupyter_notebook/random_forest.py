import time
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier



import sys
sys.path.append('../')
import crawler_settings
SWITTCH_NUM = crawler_settings.SWITTCH_NUM


global x_train, x_test, y_train, y_test
def forest_1():
    X = np.load("../data/data_jupyter/dim_4/X.npy")
    Y = np.load("../data/data_jupyter/dim_4/Y.npy")
    X.reshape((X.shape[0], -1))
    #print('X.shape：' + str(len(X)) + ',' + str(len(X[0])) + ',' + str(len(X[0][0])) + ',' + str(len(X[0][0][0])))
    #print('Y.shape：' + str(len(Y)))
    y = Y[:, 0] - 1  # 一位のみ取得
    x= np.reshape(X, (-1, len(X[0])*len(X[0][0])*len(X[0][0][0]) ))
    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.85)

def forest_2():
    global x_train, x_test, y_train, y_test
    X = np.load("../data/data_jupyter/dim_2/X.npy")
    data = np.reshape(X, (len(X)*len(X[0]), -1)) # レース数*過去10レース, 特徴量
    print(len(data))
    # カラムに名前を付ける　のちにどの特徴量が深く影響しているのか調べる用
    df = pd.DataFrame(data, columns=["horse_id", "horse_cnt", "result_rank", "racecourse", "len", "weather", "soil_condition",
                                                        "popularity", "weight", "borden_weight", "birth_days",
                                                        "sec", "diff_accident", "threeF", "corner_order_1", "corner_order_2", "corner_order_3", "money"])

    # 機械学習のモデルを作成するトレーニング用と評価用の2種類に分割する
    drop_col = ['result_rank', 'money']
    #x = df.drop(['result_rank'],axis=1) # 説明変数のみ入れる (1位の馬番)
    x = df.drop(drop_col, axis=1) # 説明変数のみ入れる (1位の馬番)
    y = df['result_rank']*16 # 正解クラス
    print(x.count())
    # 訓練用の説明変数と正解クラス、評価用の説明変数と正解クラスに分割
    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.85)

def random_forest():
    if SWITTCH_NUM == 1:
        forest_1()
    if SWITTCH_NUM == 2:
        forest_2()

    accuracy = []
    n_estimators = np.arange(1,300)
    for n in n_estimators:
        model =  RandomForestClassifier(n_estimators=n, random_state=42)
        model.fit(x_train, y_train)                 # モデル作成実行
        pred_y = model.predict(x_test)              # 予測実行
        accuracy.append(accuracy_score(y_test, pred_y)) # 精度格納
        print('...' + str(n))
    # モデルを保存
    filename = 'random_forest_model.sav'
    joblib.dump(model, filename)
    plt.plot(n_estimators, accuracy)
    plt.show()


def main():
    now = time.time()
    random_forest()
    print("ランダムフォレスト処理時間　：", time.time() - now)


if __name__ == '__main__':
    main()
