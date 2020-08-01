import time
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import joblib
import seaborn as sns
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import sys
sys.path.append('../')
import crawler_settings
from random_forest import forest_2
LOAD_MODEL_FILE_NAME = crawler_settings.LOAD_MODEL_FILE_NAME


def validation():
    # loaded model
    model = joblib.load(LOAD_MODEL_FILE_NAME)
    train_x, test_x, train_y, test_y = forest_2()
    pred_y = model.predict(test_x)
    accuracy_random_forest = accuracy_score(test_y, pred_y)
    print('--- 評価データセットを入れた場合の精度')
    print('Accuracy: {:4}'.format(accuracy_random_forest))
    print('--- クラスごとの詳細データ')
    print(classification_report(test_y, pred_y))
    #confusion matrix
    print('--- コンフュージョンマトリックス')
    mat = confusion_matrix(test_y, pred_y)
    sns.heatmap(mat, square=True, annot=True, cbar=False, fmt='d', cmap='RdPu')
    plt.xlabel('predicted class')
    plt.ylabel('true value')
    plt.show()
    # 変数の重要度を可視化
    importance = pd.DataFrame({ '変数' :train_x.columns, '重要度' :model.feature_importances_})
    print(importance.head(18))




def main():
    now = time.time()
    validation()
    print('処理時間　：{:2}'.format(time.time() - now))

if __name__ == '__main__':
    main()
