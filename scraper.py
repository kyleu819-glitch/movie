import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis():
    url = "https://www.kobis.or.kr/kobis/business/main/main.do"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("페이지 접속 시도 중...")
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    movie_list = []
    
    # KOBIS 메인 페이지의 '실시간 예매율' 순위 영역을 다시 타겟팅합니다.
    # 현재 사이트 구조에 맞춰 가장 확실한 클래스명을 찾아야 합니다.
    items = soup.find_all('div', class_='mov_list_box') # 구조에 따라 변경 필요
    
    print(f"찾은 아이템 개수: {len(items)}") # 여기서 0이 나오면 셀렉터 문제임

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for item in items:
        try:
            # 영화 제목과 예매율 추출 시도
            title = item.find('strong', class_='tit').text.strip()
            rate = item.find('span', class_='rate').text.strip()
            movie_list.append([current_time, title, rate])
            print(f"수집 성공: {title} ({rate})")
        except Exception as e:
            continue

    if not movie_list:
        print("수집된 데이터가 없습니다. 셀렉터를 점검해야 합니다.")
        return

    df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
    filename = 'kobis_reservation_data.csv'
    
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df = pd.concat([df_old, df], ignore_index=True)
    
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"최종 저장 완료: {len(df)}개의 데이터가 파일에 있습니다.")

if __name__ == "__main__":
    collect_kobis()
