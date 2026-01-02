import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright
# 임포트 방식을 변경하여 에러를 방지합니다.
import playwright_stealth

def run_crawling():
    url = "https://www.kobis.or.kr/kobis/business/stat/boxs/findRealTicketList.do"
    filename = 'kobis_reservation_data.csv'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        # stealth_sync 대신 직접 호출 방식을 사용합니다.
        playwright_stealth.stealth_sync(page)
        
        print(f"상세 통계 페이지 접속 시도: {url}")
        page.goto(url, wait_until="networkidle")

        try:
            # KOBIS 페이지의 특성상 로딩 시간이 필요하므로 5초간 대기합니다.
            page.wait_for_timeout(5000)
            
            # 모든 프레임을 탐색하여 표 데이터를 찾습니다.
            target_frame = None
            for frame in page.frames:
                if frame.query_selector(".tbl_type02"):
                    target_frame = frame
                    break
            
            if not target_frame:
                if page.query_selector(".tbl_type02"):
                    target_frame = page
                else:
                    raise Exception("데이터 테이블(tbl_type02)을 찾을 수 없습니다.")

            # 데이터 행(tr) 수집
            rows = target_frame.query_selector_all(".tbl_type02 tbody tr")
            print(f"데이터 행 발견: {len(rows)}개")
            
            movie_list = []
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) >= 4:
                    # 2번 열: 영화명, 4번 열: 예매율
                    title = cols[1].inner_text().strip()
                    rate = cols[3].inner_text().replace('%', '').strip()
                    if title and rate:
                        movie_list.append([current_time, title, rate])
                        print(f"수집: {title} ({rate}%)")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            page.screenshot(path="debug_screenshot.png")
            browser.close()
            return

        browser.close()

        if movie_list:
            df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
            if os.path.exists(filename):
                df_old = pd.read_csv(filename, encoding='utf-8-sig')
                df = pd.concat([df_old, df], ignore_index=True)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"최종 {len(movie_list)}건 저장 완료.")

if __name__ == "__main__":
    run_crawling()
