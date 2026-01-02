import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis_stats():
    # 유경용 님이 알려주신 통계 상세 페이지 URL
    url = "https://www.kobis.or.kr/kobis/business/stat/boxs/findRealTicketList.do"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.kobis.or.kr/'
    }
    
    print(f"통계 페이지 접속 시도: {url}")
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    movie_list = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # KOBIS 통계 페이지는 보통 'tbl_type02' 또는 'board_list' 클래스의 table을 사용합니다.
    # 테이블 내의 모든 행(tr)을 찾습니다.
    rows = soup.select('table.tbl_type02 tbody tr')
    
    if not rows:
        # 다른 클래스명 후보군으로 재시도
        rows = soup.select('table tbody tr')

    print(f"찾은 데이터 행 개수: {len(rows)}")

    for row in rows:
        cols = row.find_all('td')
        # 보통 1번 열에 순위, 2번 열에 영화명, 5~7번 열 사이에 예매율이 있습니다.
        if len(cols) > 5:
            try:
                # 영화명 추출 (보통 2번째 td)
                title = cols[1].text.strip()
                # 예매점유율 추출 (보통 5~6번째 td, '예매점유율' 헤더 확인 필요)
                # 이 페이지 구조상 실시간 예매율은 보통 뒤쪽 컬럼에 위치합니다.
                rate = cols[5].text.strip().replace('%', '')
                
                if title and rate:
                    movie_list.append([current_time, title, rate])
                    print(f"수집 성공: {title} ({rate}%)")
            except Exception as e:
                continue

    if not movie_list:
        print("데이터를 찾을 수 없습니다. 페이지 소스를 확인해야 합니다.")
        return

    # 데이터 저장
    df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
    filename = 'kobis_reservation_data.csv'
    
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df = pd.concat([df_old, df], ignore_index=True)
    
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"[{current_time}] 총 {len(movie_list)}개 영화 데이터 저장 완료!")

if __name__ == "__main__":
    collect_kobis_stats()
