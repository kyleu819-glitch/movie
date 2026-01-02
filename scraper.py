import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis_survivor():
    # 시도할 후보 URL들 (KOBIS의 다양한 경로)
    urls = [
        "https://www.kobis.or.kr/kobis/business/main/main.do", # 비즈니스 메인 (가장 유력)
        "https://www.kobis.or.kr/kobis/business/stat/boxs/findRealTicketList.do", # 통계 상세
        "https://www.kobis.or.kr/main.do" # 일반 메인
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    movie_list = []
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for url in urls:
        print(f"\n[진단] 접속 시도 중: {url}")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            print(f"[결과] 상태 코드: {res.status_code}")
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # 1. 비즈니스 메인/상세 페이지의 '순위 리스트' 태그 찾기
                items = soup.select('.main_real_ranking li') or soup.select('.sector_rank .item') or soup.select('table tbody tr')
                
                print(f"[분석] 찾은 데이터 항목: {len(items)}개")
                
                if len(items) > 1: # 헤더 외에 데이터가 있다면
                    for item in items:
                        try:
                            # 다양한 태그 패턴 대응 (태그가 바뀔 수 있으므로 여러 후보군 설정)
                            title_tag = item.select_one('strong') or item.select_one('.tit') or item.select_one('td.tal')
                            rate_tag = item.select_one('.rate') or item.select_one('span') or item.select_one('td:nth-child(6)')
                            
                            if title_tag and rate_tag:
                                title = title_tag.text.strip()
                                rate = "".join(filter(lambda x: x.isdigit() or x == '.', rate_tag.text))
                                if title and rate:
                                    movie_list.append([current_time, title, rate])
                        except:
                            continue
                    
                    if movie_list:
                        print(f"✅ 수집 성공! ({len(movie_list)}건)")
                        break # 하나라도 성공하면 루프 중단
            else:
                continue
        except Exception as e:
            print(f"[오류] {url} 접속 중 문제 발생: {e}")

    if not movie_list:
        print("\n❌ 모든 경로에서 수집 실패. 서버가 자동화 접속을 차단 중일 수 있습니다.")
        return

    # 데이터 저장
    df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
    filename = 'kobis_reservation_data.csv'
    if os.path.exists(filename):
        df_old = pd.read_csv(filename, encoding='utf-8-sig')
        df = pd.concat([df_old, df], ignore_index=True)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n데이터가 {filename}에 최종 저장되었습니다.")

if __name__ == "__main__":
    collect_kobis_survivor()
