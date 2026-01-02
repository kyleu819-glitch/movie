import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis_realtime():
    url = "https://www.kobis.or.kr/kobis/business/stat/boxs/findRealTicketList.do"
    
    # KOBIS 서버에 보낼 조회 조건 (POST 데이터)
    # 별도의 날짜 지정이 없으면 서버는 최신 데이터를 반환합니다.
    payload = {
        'choiceDate': datetime.now().strftime('%Y-%m-%d'),
        'searchType': 'real',
        'curPage': '1'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Origin': 'https://www.kobis.or.kr',
        'Referer': 'https://www.kobis.or.kr/kobis/business/stat/boxs/findRealTicketList.do',
        'X-Requested-With': 'XMLHttpRequest' # AJAX 요청임을 명시
    }
    
    print(f"데이터 요청 중: {url}")
    
    # GET이 아닌 POST로 요청을 보냅니다.
    res = requests.post(url, data=payload, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    movie_list = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 데이터가 포함된 행(tr)을 찾습니다.
    # KOBIS 통계 리스트는 보통 tbody 안의 tr에 데이터가 있습니다.
    rows = soup.select('tbody tr')
    
    print(f"응답 결과 확인 - 찾은 데이터 행 개수: {len(rows)}")

    for row in rows:
        try:
            cols = row.find_all('td')
            if len(cols) > 5:
                # 1:순위, 2:영화명, 3:개봉일, 4:예매율 순서인 경우가 많습니다.
                # 'title' 클래스나 특정 위치를 타겟팅
                title = cols[1].find('span').text.strip() if cols[1].find('span') else cols[1].text.strip()
                # 예매율은 보통 % 기호가 붙은 열을 찾습니다.
                rate = ""
                for col in cols:
                    if '%' in col.text:
                        rate = col.text.replace('%', '').strip()
                        break
                
                if title and rate:
                    movie_list.append([current_time, title, rate])
                    print(f"수집 성공: {title} ({rate}%)")
        except Exception as e:
            continue

    if not movie_list:
        print("여전히 데이터를 찾을 수 없습니다. 로그 확인이 필요합니다.")
        # 만약 실패하면 응답받은 HTML의 일부를 출력해 원인을 파악합니다.
        print("HTML 요약:", res.text[:300])
        return

    # 데이터 저장 로직
    df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
    filename = 'kobis_reservation_data.csv'
    
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df = pd.concat([df_old, df], ignore_index=True)
    
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"[{current_time}] 총 {len(movie_list)}개 영화 데이터 저장 완료!")

if __name__ == "__main__":
    collect_kobis_realtime()
