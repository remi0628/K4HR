import datetime

# crawlerを回す範囲
MIN_DATE = datetime.date(year=2020, month=1, day=3)
MAX_DATE = datetime.date(year=2020, month=1, day=4)

# craler並列化した際のパワーをどのくらい使用するか
MAX_THREAD = 4

# Link
CSV_DATA_PATH = 'data/horse_blank_data/'
HOME_URL = 'https://www.nankankeiba.com'
CALENDER_URL = 'https://www.nankankeiba.com/calendar/'

#URL = 'https://www.nankankeiba.com/race_info/2020060120040101.do'
#BLANK_URL = 'https://www.nankankeiba.com/uma_info/2017100322.do'
#RACE_LIST_HELF_PERIOD = 'https://www.nankankeiba.com/calendar/202004.do'
