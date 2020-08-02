import glob
import numpy as np

NAME = "2010-01-01-2020-04-01"


def train_test_split(data, size=0.9):
    length = len(data)
    np.random.seed(42)
    p = np.random.permutation(length)
    data = data[p]
    return data[:int(length * size)], data[int(length * size):]


def model_load_predict_save():
    import tensorflow as tf
    X = np.load(f"data/X{NAME}.npy")
    x_train, x_test = train_test_split(X)
    model = tf.keras.models.load_model("data/horse2020-08-02-19-13-56-3076.h5", compile=False)
    ys = model.predict(x_test)
    np.save("data/predict.npy", ys)


ranking = np.load(f"data/Y{NAME}.npy")
P = np.load(f"data/P{NAME}.npy", allow_pickle=True)

y_train, y_test = train_test_split(ranking)
p_train, p_test = train_test_split(P)

# 毎回tfでpredictするの時間かかって面倒なので保存して読み込み
# model_load_predict_save()
ys = np.load("data/predict.npy")


def verification_old():
    print("                 検証数    単勝率    複勝率    馬連率    馬単率   3連複率   3連単率   ワイド率")
    for base in range(10):
        value = []
        line = base / 10
        length = len([np.argmax(ys[i]) for i in range(len(ys)) if np.max(ys[i]) > line])
        if length == 0:
            break
        value.append(length)  # 検証数

        win1 = len(
            [np.argmax(ys[i]) for i in range(len(ys)) if np.argmax(ys[i]) == y_test[i][0] - 1 and np.max(ys[i]) > line])
        value.append(round(win1 / length, 3))

        win2 = len([np.argmax(ys[i]) for i in range(len(ys)) if
                    np.argmax(ys[i]) == y_test[i][1] - 1 and np.max(ys[i]) > line and len(
                        np.where(y_test[i] > 0)[0]) >= 5]) if [i for i in range(len(ys)) if
                                                               len(np.where(y_test[i] > 0)[0]) >= 5] else -1
        win3 = len([np.argmax(ys[i]) for i in range(len(ys)) if
                    np.argmax(ys[i]) == y_test[i][2] - 1 and np.max(ys[i]) > line and len(
                        np.where(y_test[i] > 0)[0]) >= 7])
        value.append(round((win1 + win2 + win3) / length, 3)) if win2 != -1 else value.append("-")

        quinella = len([np.argmax(ys[i]) for i in range(len(ys)) if
                        all(np.sort(ys[i].argsort()[::-1][:2]) == np.sort(y_test[i][:2]) - 1) and np.max(
                            ys[i]) > line and len(np.where(y_test[i] > 0)[0]) >= 3]) if [i for i in range(len(ys)) if
                                                                                         len(np.where(y_test[i] > 0)[
                                                                                                 0]) >= 3] else -1
        value.append(round(quinella / length, 3)) if quinella != -1 else value.append("-")
        exacta = len([np.argmax(ys[i]) for i in range(len(ys)) if
                      all(ys[i].argsort()[::-1][:2] == y_test[i][:2] - 1) and np.max(ys[i]) > line and len(
                          np.where(y_test[i] > 0)[0]) >= 3]) if [i for i in range(len(ys)) if
                                                                 len(np.where(y_test[i] > 0)[0]) >= 3] else -1
        value.append(round(exacta / length, 3)) if exacta != -1 else value.append("-")

        trio = len([np.argmax(ys[i]) for i in range(len(ys)) if
                    all(np.sort(ys[i].argsort()[::-1][:3]) == np.sort(y_test[i][:3]) - 1) and np.max(
                        ys[i]) > line and len(np.where(y_test[i] > 0)[0]) >= 4]) if [i for i in range(len(ys)) if len(
            np.where(y_test[i] > 0)[0]) >= 4] else -1
        value.append(round(trio / length, 3)) if trio != -1 else value.append("-")
        tierce = len([np.argmax(ys[i]) for i in range(len(ys)) if
                      all(ys[i].argsort()[::-1][:3] == y_test[i][:3] - 1) and np.max(ys[i]) > line and len(
                          np.where(y_test[i] > 0)[0]) >= 4]) if [i for i in range(len(ys)) if
                                                                 len(np.where(y_test[i] > 0)[0]) >= 4] else -1
        value.append(round(tierce / length, 3)) if tierce != -1 else value.append("-")

        wide = len([np.argmax(ys[i]) for i in range(len(ys)) if
                    (ys[i].argsort()[::-1][0] in (np.sort(y_test[i][:3]) - 1)) and (
                            ys[i].argsort()[::-1][1] in (np.sort(y_test[i][:3]) - 1)) and np.max(
                        ys[i]) > line and len(np.where(y_test[i] > 0)[0]) >= 4]) if [i for i in range(len(ys)) if len(
            np.where(y_test[i] > 0)[0]) >= 4] else -1
        value.append(round(wide / length, 3)) if wide != -1 else value.append("-")

        print(f"Base Line {line}", [str(x).rjust(5) for x in value])


def collation(i, columns, baseLine=0.0, mode="or", count=1):
    money = 0
    moneyKey = False
    y = ys[i].argsort()[::-1]  # 確率高い順のインデックス
    for c in columns:
        if str(p_test[i][c]) != "0":
            moneyKey = True

        winKeys = [0]
        for n in range(count):
            if mode == "or":
                if y[n] + 1 in [int(m) for m in str(p_test[i][c]).split("-")]:
                    winKeys.append(1)
            elif mode == "and":
                if str(p_test[i][c]) != "0":
                    if y[n] + 1 == int(str(p_test[i][c]).split("-")[n]):
                        winKeys.append(1)

            if sum(winKeys) == count:
                money += int(str(p_test[i][c + 1]).replace(",", ""))
    if not moneyKey or np.max(ys[i]) < baseLine:
        return False, money
    money -= 100

    return True, money


def verification():
    moneys = [[], [], [], [], [], []]
    baseline = 0.0
    for i in range(len(y_test)):
        if collation(i, [1], baseline)[0]:
            moneys[0].append(collation(i, [1], baseline)[1])  # 単勝
        if collation(i, [4, 19, 22], baseline)[0]:
            moneys[1].append(collation(i, [4, 19, 22], baseline)[1])  # 複勝
        if collation(i, [10], baseline, count=2)[0]:
            moneys[2].append(collation(i, [10], baseline, count=2)[1])  # 馬複
        if collation(i, [28], baseline, count=3)[0]:
            moneys[3].append(collation(i, [28], baseline, count=3)[1])  # 三連複
        if collation(i, [31], baseline, count=3)[0]:
            moneys[4].append(collation(i, [31], baseline, count=3, mode="and")[1])  # 三連単
        if collation(i, [25, 34, 37], baseline, count=2)[0]:
            moneys[5].append(collation(i, [25, 34, 37], baseline, count=2)[1])  # ワイド


    print("    検証数  収支  正答率 平均払戻金 回収率")
    modes = ["単勝", "複勝", "馬複", "三複", "三単", "ワイド"]
    for i, money in enumerate(moneys):
        money = np.array(money)
        print(modes[i],
              len(money),
              sum(money),
              round(len(money[money > -100]) / len(money), 4),
              int(sum(money[money > -100]) / len(money[money > -100]) + 100),
              round((len(money) * 100 + sum(money)) / (len(money) * 100), 3))


def main():
    # verification_old()
    verification()


if __name__ == '__main__':
    main()
