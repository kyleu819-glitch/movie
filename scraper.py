import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

def run_crawling():
    url = "https://www.kobis.or.kr/kobis/business/main/main.do"
    filename = 'kobis_reservation_data.csv'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sync_playwright() as p:
        # 1. 사람처럼 보이도록 브라우저 설정 강화
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        print(f"브라우저 접속 시도: {url}")
        try:
            # 접속 시 대기 시간을 30초로 넉넉히 설정
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 2. 데이터가 나타날 때까지 최대 20초간 대기 (여러 후보 셀렉터 확인)
            print("데이터 로딩 대기 중...")
            page.wait_for_timeout(5000) # 일단 5초간 무조건 대기 (안정성)
            
            # 실시간 예매율 순위 영역이 나타나는지 확인
            target_selector = ".main_real_ranking"
            page.wait_for_selector(target_selector, timeout=20000)
            
        except Exception as e:
            print(f"로딩 실패 또는 타임아웃: {e}")
            # [핵심] 실패 원인을 알기 위해 현재 화면을 스크린샷으로 저장합니다.
            page.screenshot(path="debug_screenshot.png")
            print("디버깅용 스크린샷을 저장했습니다 (debug_screenshot.png)")
            browser.close()
            return

        # 3. 데이터 추출
        items = page.query_selector_all(f"{target_selector} li")
        print(f"찾은 항목 개수: {len(items)}")
        
        movie_list = []
        for item in items:
            try:
                title_el = item.query_selector("strong")
                rate_el = item.query_selector(".rate")
                
                if title_el and rate_el:
                    title = title_el.inner_text().strip()
                    rate = rate_text = rate_el.inner_text().replace('예매율', '').replace('%', '').strip()
                    if title:
                        movie_list.append([current_time, title, rate])
                        print(f"수집 성공: {title} ({rate}%)")
            except:
                continue

        browser.close()

        # 4. 저장 로직
        if movie_list:
            df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
            if os.path.exists(filename):
                df_old = pd.read_csv(filename, encoding='utf-8-sig')
                df = pd.concat([df_old, df], ignore_index=True)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[{current_time}] 총 {len(movie_list)}건 저장 완료!")
        else:
            print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    run_crawling()
