import feedparser
import csv
from datetime import datetime, timedelta
import os

def main():
    # 1. 수집 기간 설정 (최근 7일)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # 2. 백악관 공식 RSS 주소 (구글 우회보다 훨씬 정확함)
    rss_url = "https://www.whitehouse.gov/briefing-room/feed/"
    
    print(f"📡 백악관 공식 뉴스룸 직접 수집 중... ({start_date.strftime('%Y-%m-%d')} 이후)")

    try:
        # RSS 데이터 파싱
        feed = feedparser.parse(rss_url)
        all_data = []

        if not feed.entries:
            print("⚠️ 수집된 데이터가 없습니다. 피드 주소를 확인하거나 잠시 후 다시 시도하세요.")
            return

        for entry in feed.entries:
            # 날짜 파싱 및 필터링
            pub_date_struct = entry.published_parsed
            pub_date = datetime(*pub_date_struct[:3])

            if pub_date >= start_date:
                all_data.append({
                    "발행일": pub_date.strftime('%Y-%m-%d'),
                    "제목": entry.title,
                    "링크": entry.link
                })

        # 3. CSV 저장
        file_name = 'whitehouse_news_decoded.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "링크"])
            writer.writeheader()
            writer.writerows(all_data)

        print(f"✅ 수집 완료! {len(all_data)}건의 데이터를 '{file_name}'에 저장했습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
