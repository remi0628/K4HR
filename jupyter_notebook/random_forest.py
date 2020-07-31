import time
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import sys
sys.path.append('../')
import crawler_settings
SWITTCH_NUM = crawler_settings.SWITTCH_NUM



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
    X = np.load("../data/data_jupyter/dim_2/X.npy")


def random_forest():
    if SWITTCH_NUM == 1:
        forest_1()
    if SWITTCH_NUM == 2:
        forest_2()
    """
    accuracy = []
    n_estimators = np.arange(1,50)
    for n in n_estimators:
        model =  RandomForestClassifier(n_estimators=n, random_state=42)
        model.fit(x_train, y_train)                 # モデル作成実行
        pred_y = model.predict(x_test)              # 予測実行
        accuracy.append(accuracy_score(y_test, pred_y)) # 精度格納
        print('...' + str(n))
    plt.plot(n_estimators, accuracy)
    plt.show()
    """

def main():
    now = time.time()
    random_forest()
    print("ランダムフォレスト処理時間　：", time.time() - now)


if __name__ == '__main__':
    main()
