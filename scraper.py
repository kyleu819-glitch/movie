import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def collect_kobis():
    url = "https://www.kobis.or.kr/kobis/business/main/main.do"
    # 실제 브라우저처럼 보이게 하여 차단을 방지합니다.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.kobis.or.kr/'
    }
    
    print("페이지 접속 시도 중...")
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8' # 한글 깨짐 방지
    soup = BeautifulSoup(res.text, 'html.parser')
    
    movie_list = []
    
    # 1. 실시간 예매율 순위 영역을 정밀하게 타겟팅합니다.
    # KOBIS 비즈니스 메인은 보통 'ov-all' 또는 'main_real_ranking' 클래스를 사용합니다.
    items = soup.select('.main_real_ranking li') or soup.select('.sector_rank .item') or soup.select('div.ov-all li')
    
    print(f"찾은 아이템 개수: {len(items)}")

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for item in items:
        try:
            # 제목과 예매율 추출 (KOBIS 구조상 strong 태그와 span.rate를 주로 사용)
            title_tag = item.select_one('strong') or item.select_one('.tit')
            rate_tag = item.select_one('.rate') or item.select_one('span')
            
            if title_tag and rate_tag:
                title = title_tag.text.strip()
                rate = rate_tag.text.replace('예매율', '').replace('%', '').strip()
                
                # '1위', '2위' 같은 텍스트가 섞여있을 수 있어 정제합니다.
                movie_list.append([current_time, title, rate])
                print(f"수집 성공: {title} ({rate}%)")
        except Exception as e:
            continue

    if not movie_list:
        print("수집된 데이터가 없습니다. (페이지 소스 구조를 다시 확인해야 합니다.)")
        # 디버깅을 위해 페이지 소스 일부 출력
        print("--- 페이지 소스 일부 (디버깅용) ---")
        print(res.text[:500]) 
        return

    # 데이터 저장 로직
    df = pd.DataFrame(movie_list, columns=['check_time', 'title', 'rate'])
    filename = 'kobis_reservation_data.csv'
    
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df = pd.concat([df_old, df], ignore_index=True)
    
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"최종 저장 완료: {len(df)}개의 데이터가 파일에 있습니다.")

if __name__ == "__main__":
    collect_kobis()
