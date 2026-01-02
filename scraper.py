import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

def run_crawling():
    # 1. 유경용 님이 지정하신 상세 통계 페이지 URL
    url = "https://www.kobis.or.kr/kobis/business/stat/boxs/findRealTicketList.do"
    filename = 'kobis_reservation_data.csv'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 실제 브라우저와 유사한 환경 설정
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print(f"상세 통계 페이지 접속 중: {url}")
        page.goto(url, wait_until="networkidle")

        try:
            # 2. 이미지(image_a7cf42.png)에 보이는 테이블이 로드될 때까지 대기
            # KOBIS 통계 표는 보통 'tbl_type02' 클래스를 사용합니다.
            page.wait_for_selector(".tbl_type02", timeout=30000)
            print("데이터 테이블 확인 완료.")
        except Exception as e:
            print(f"테이블 로딩 실패: {e}")
            page.screenshot(path="debug_screenshot.png")
            browser.close()
            return

        # 3. 테이블의 모든 행(tr) 추출
        rows = page.query_selector_all(".tbl_type02 tbody tr")
        print(f"수집된 데이터 행: {len(rows)}개")
        
        movie_list = []
        for row in rows:
            cols = row.query_selector_all("td")
            # 이미지 구조 기준: 2번째 열(영화명), 4번째 열(예매율)
            if len(cols) >= 4:
                try:
                    # 영화명 추출 (두 번째 칸)
                    title = cols[1].inner_text().strip()
                    # 예매율 추출 (네 번째 칸)
                    rate = cols[3].inner_text().replace('%', '').strip()
                    
                    if title and rate:
                        movie_list.append([current_time, title, rate])
                        print(f"✅ 수집 성공: {title} ({rate}%)")
                except:
                    continue

        browser.close()

        # 4. 데이터 저장 (기존 파일에 누적)
        if movie_list:
            df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
            if os.path.exists(filename):
                df_old = pd.read_csv(filename, encoding='utf-8-sig')
                df = pd.concat([df_old, df], ignore_index=True)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[{current_time}] 총 {len(movie_list)}건의 상세 데이터 저장 완료!")
        else:
            print("수집된 영화 데이터가 없습니다.")

if __name__ == "__main__":
    run_crawling()
