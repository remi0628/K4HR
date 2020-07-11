import requests
from bs4 import BeautifulSoup

def url_to_soup(url):
    req = requests.get(url)
    return BeautifulSoup(req.content, 'html.parser')

def horse_page_link(url):
    soup = url_to_soup(url)
    link_list = [HOME_URL + x.get('href') for x in soup.find_all('a', class_='tx-mid tx-low') ]
    return link_list
tag_to_text = lambda x: p.sub("", x).split('\n')
split_tr = lambda x: str(x).split('</tr>')

def get_previous_race_row(soup):
    race_table = soup.select("table.tb01")[2]
    return [tag_to_text(x)  for x in split_tr(race_table)]

def horse_data(url, race_date):
    soup = url_to_soup(url)

    # 過去のレースデータ
    pre_race_data = get_previous_race_row(soup)
    df = pd.DataFrame(pre_race_data)[1:][[2,3,10,11,13,14,15,19,23]].dropna().rename(columns={
        2:'date', 3:'place', 10:'len', 11:'wether', 13:'popularity', 14:'rank', 15:'time',19:'weight',23:'money'})
    return df
