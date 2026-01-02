import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis_realtime():
    # 1. KOBIS 비즈니스 페이지가 실시간 예매율 데이터를 가져올 때 사용하는 실제 내부 주소입니다.
    # 이 주소는 HTML 조각(fragment)을 직접 반환하므로 파싱이 훨씬 정확합니다.
    url = "https://www.kobis.or.kr/kobis/business/main/searchRealTicketOrder.do"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.kobis.or.kr/kobis/business/main/main.do',
        'X-Requested-With': 'XMLHttpRequest' # 브라우저 공식 요청임을 명시
    }
    
    print(f"실시간 데이터 전용 엔드포인트 접속 시도 중...")
    
    try:
        # 세션(Session)을 사용하여 쿠키를 유지합니다. (보안 통과 핵심)
        session = requests.Session()
        # 먼저 메인 페이지에 한 번 접속해서 세션 쿠키를 굽습니다.
        session.get("https://www.kobis.or.kr/kobis/business/main/main.do", headers=headers)
        
        # 실제 데이터 요청 (POST)
        res = session.post(url, headers=headers)
        res.encoding = 'utf-8'
        
        if res.status_code != 200:
            print(f"서버 접속 실패 (코드: {res.status_code})")
            return

        soup = BeautifulSoup(res.text, 'html.parser')
        
        movie_list = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 이 엔드포인트는 영화 목록을 <li> 태그 형태로 반환합니다.
        items = soup.select('li')
        print(f"찾은 영화 아이템 개수: {len(items)}")

        for item in items:
            # 제목 추출 (<strong> 태그)
            title_tag = item.select_one('strong')
            # 예매율 추출 (class="rate"인 <span> 태그)
            rate_tag = item.select_one('.rate')
            
            if title_tag and rate_tag:
                title = title_tag.text.strip()
                # '예매율 24.5%' 문자열에서 숫자만 추출
                rate = rate_tag.text.replace('예매율', '').replace('%', '').strip()
                
                movie_list.append([current_time, title, rate])
                print(f"수집 성공: {title} ({rate}%)")

        if not movie_list:
            print("데이터 수집 실패. 서버 응답 내용 일부:")
            print(res.text[:300]) # 차단 메시지 여부 확인용
            return

        # CSV 파일 저장 (기존 데이터가 있으면 누적)
        df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
        filename = 'kobis_reservation_data.csv'
        
        if os.path.exists(filename):
            df_old = pd.read_csv(filename)
            df = pd.concat([df_old, df], ignore_index=True)
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"[{current_time}] 총 {len(movie_list)}건의 실시간 예매 데이터 저장 완료!")
        
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")

if __name__ == "__main__":
    collect_kobis_realtime()
