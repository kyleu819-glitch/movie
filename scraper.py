import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis():
    url = "https://www.kobis.or.kr/kobis/business/main/main.do"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 예매율 순위 데이터 파싱 (KOBIS 메인 구조에 맞게 선택자 설정)
    # 아래 선택자는 예시이며, 실제 사이트 구조에 따라 조정될 수 있습니다.
    movie_list = []
    items = soup.select('.sector_rank .item') 
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for item in items:
        title = item.select_one('.title').text.strip()
        rate = item.select_one('.rate').text.strip().replace('%', '')
        movie_list.append([current_time, title, rate])

    df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])

    # 데이터 누적 저장 (기존 파일이 있으면 합치고, 없으면 새로 생성)
    filename = 'kobis_reservation_data.csv'
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df_new = pd.concat([df_old, df], ignore_index=True)
        df_new.to_csv(filename, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(filename, index=False, encoding='utf-8-sig')

    print(f"{current_time} 데이터 수집 완료")

if __name__ == "__main__":
    collect_kobis()
