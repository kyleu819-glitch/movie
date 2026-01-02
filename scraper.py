import os
import pandas as pd
from datetime import datetime
from playwright.sync_api import sync_playwright

def run_crawling():
    url = "https://www.kobis.or.kr/kobis/business/main/main.do"
    filename = 'kobis_reservation_data.csv'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"브라우저로 접속 중: {url}")
        page.goto(url, wait_until="networkidle") # 네트워크가 조용해질 때까지 대기

        # 예매율 데이터가 있는 셀렉터가 나타날 때까지 명시적으로 기다림 (최대 10초)
        try:
            page.wait_for_selector(".main_real_ranking", timeout=10000)
        except:
            print("데이터 로딩 시간이 초과되었습니다.")
            browser.close()
            return

        # 화면에 보이는 영화 아이템들을 수집
        items = page.query_selector_all(".main_real_ranking li")
        
        movie_list = []
        for item in items:
            title_el = item.query_selector("strong")
            rate_el = item.query_selector(".rate")
            
            if title_el and rate_el:
                title = title_el.inner_text().strip()
                rate = rate_el.inner_text().replace('예매율', '').replace('%', '').strip()
                if title:
                    movie_list.append([current_time, title, rate])
                    print(f"수집 성공: {title} ({rate}%)")

        browser.close()

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
