import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import os

def main():
    # 1. 대상 URL 및 7일 전 날짜 설정
    url = "https://www.whitehouse.gov/briefing-room/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    # 한국 시간 기준이 아닌 현지 시간 기준으로 넉넉하게 7일+@ 설정
    one_week_ago = datetime.now() - timedelta(days=8)
    
    print(f"📡 백악관 뉴스룸 직접 크롤링 시작: {url}")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ 페이지 접속 실패 (상태 코드: {response.status_code})")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 백악관 뉴스 아이템은 보통 'news-item' 클래스나 'article' 태그 내에 존재
        # 최신 구조에 맞춰 반복문 실행
        news_items = soup.select('article')
        all_data = []

        for item in news_items:
            try:
                # 제목 및 링크 추출
                title_tag = item.select_one('h2 a') or item.select_one('a')
                title = title_tag.get_text(strip=True)
                link = title_tag['href']

                # 날짜 추출 (보통 <time> 태그 사용)
                date_tag = item.select_one('time')
                if date_tag:
                    date_str = date_tag.get_text(strip=True) # 예: January 31, 2026
                    # 날짜 문자열을 파이썬 객체로 변환
                    pub_date = datetime.strptime(date_str, "%B %d, %Y")
                    
                    # 7일 이내 데이터만 필터링
                    if pub_date >= one_week_ago:
                        all_data.append({
                            "발행일": pub_date.strftime('%Y-%m-%d'),
                            "제목": title,
                            "링크": link
                        })
            except Exception as e:
                continue

        # 2. CSV 저장
        file_name = 'whitehouse_news_decoded.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "링크"])
            writer.writeheader()
            if all_data:
                writer.writerows(all_data)
                print(f"✅ 수집 완료: 총 {len(all_data)}건의 최신 보도자료를 확보했습니다.")
            else:
                print("⚠️ 수집된 데이터가 없습니다. (최근 7일 내 게시물이 없거나 구조 변경)")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
