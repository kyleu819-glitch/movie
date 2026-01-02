import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis_public():
    # 404가 발생하지 않는 공식 메인 페이지 주소입니다.
    url = "https://www.kobis.or.kr/kobis/main/main.do"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    print(f"KOBIS 공식 메인 페이지 접속 중: {url}")
    
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        
        if res.status_code != 200:
            print(f"접속 실패! (에러 코드: {res.status_code})")
            return

        soup = BeautifulSoup(res.text, 'html.parser')
        
        movie_list = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 메인 페이지의 '실시간 예매율' 리스트 영역을 찾습니다.
        # 보통 .ov-all 클래스 하위의 li 태그에 영화 정보가 들어있습니다.
        items = soup.select('.ov-all li')
        
        print(f"페이지 분석 중... 찾은 아이템 개수: {len(items)}")

        for item in items:
            try:
                # 영화 제목 (strong.tit 태그)
                title_tag = item.select_one('.tit') or item.select_one('strong')
                # 예매율 (span.rate 태그)
                rate_tag = item.select_one('.rate') or item.select_one('span')
                
                if title_tag and rate_tag:
                    title = title_tag.text.strip()
                    # "예매율 25.4%" 에서 숫자와 소수점만 추출
                    rate_text = rate_tag.text.strip()
                    rate = "".join(filter(lambda x: x.isdigit() or x == '.', rate_text))
                    
                    if title and rate:
                        movie_list.append([current_time, title, rate])
                        print(f"수집 성공: {title} ({rate}%)")
            except:
                continue

        if not movie_list:
            print("데이터를 찾을 수 없습니다. 선택자(Selector)를 재점검합니다.")
            return

        # CSV 저장 로직
        df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
        filename = 'kobis_reservation_data.csv'
        
        if os.path.exists(filename):
            df_old = pd.read_csv(filename, encoding='utf-8-sig')
            df = pd.concat([df_old, df], ignore_index=True)
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"[{current_time}] 총 {len(movie_list)}건 저장 완료!")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    collect_kobis_public()
