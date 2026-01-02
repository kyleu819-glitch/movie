import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def run_crawling():
    url = "https://www.kobis.or.kr/kobis/business/stat/boxs/findRealTicketList.do"
    filename = 'kobis_reservation_data.csv'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sync_playwright() as p:
        # 1. 브라우저 실행 및 스텔스 설정 (봇 차단 방지)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        stealth_sync(page) # 자동화 도구임을 숨김
        
        print(f"상세 통계 페이지 접속 시도: {url}")
        page.goto(url, wait_until="networkidle")

        # 2. 통계 표가 프레임 내부에 있는지 확인하고 접근합니다.
        # KOBIS 통계는 보통 'contentFrame'이나 특정 iframe 안에 들어있습니다.
        try:
            # 모든 프레임을 뒤져서 '.tbl_type02' 표가 있는 곳을 찾습니다.
            print("테이블 로딩 대기 중 (프레임 탐색)...")
            page.wait_for_timeout(5000) # 데이터 로딩을 위한 기초 대기
            
            target_frame = None
            for frame in page.frames:
                if frame.query_selector(".tbl_type02"):
                    target_frame = frame
                    break
            
            if not target_frame:
                # 메인 페이지에 직접 있는 경우
                if page.query_selector(".tbl_type02"):
                    target_frame = page
                else:
                    raise Exception("테이블이 포함된 프레임을 찾을 수 없습니다.")

            # 3. 데이터 추출 (행 단위)
            rows = target_frame.query_selector_all(".tbl_type02 tbody tr")
            print(f"데이터 행 발견: {len(rows)}개")
            
            movie_list = []
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) >= 4:
                    # 이미지 기준: 2번 열(영화명), 4번 열(예매율)
                    title = cols[1].inner_text().strip()
                    rate = cols[3].inner_text().replace('%', '').strip()
                    if title and rate:
                        movie_list.append([current_time, title, rate])
                        print(f"수집: {title} ({rate}%)")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            page.screenshot(path="debug_screenshot.png")
            print("원인 파악을 위해 스크린샷을 저장했습니다.")
            browser.close()
            return

        browser.close()

        # 4. CSV 저장
        if movie_list:
            df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
            if os.path.exists(filename):
                df_old = pd.read_csv(filename, encoding='utf-8-sig')
                df = pd.concat([df_old, df], ignore_index=True)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"최종 {len(movie_list)}건 저장 완료.")

if __name__ == "__main__":
    run_crawling()
