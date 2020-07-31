import datetime

# crawlerを回す範囲
MIN_DATE = datetime.date(year=2010, month=4, day=1)
MAX_DATE = datetime.date(year=2012, month=4, day=1)

# craler並列化した際のパワーをどのくらい使用するか
MAX_THREAD = 4

### preprocessing_another.py
 #取得するファイルの制限指定 指定なしの場合0 （今使用していない）
FILE_NUM = 1
### preprocessing_another.py, random_forest.py共通
# どのプロフラムを使用するか
# [1] = (レース, 出馬, 過去10レース, 特徴量), [2] = (過去レース, 特徴量)
SWITTCH_NUM = 2

# Link
CSV_DATA_PATH = 'data/horse_blank_data/'
HOME_URL = 'https://www.nankankeiba.com'
CALENDER_URL = 'https://www.nankankeiba.com/calendar/'

#URL = 'https://www.nankankeiba.com/race_info/2020060120040101.do'
#BLANK_URL = 'https://www.nankankeiba.com/uma_info/2017100322.do'
#RACE_LIST_HELF_PERIOD = 'https://www.nankankeiba.com/calendar/202004.do'
