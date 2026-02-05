import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
import time

def main():
    # 1. 넉넉하게 최근 10일치 설정 (누락 방지)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    start_str = start_date.strftime("%Y-%m-%d")

    # 2. 가장 안정적인 구글 뉴스 RSS 쿼리 (백악관 브리핑룸 타겟)
    # after 조건을 제거하고 코드 내에서 필터링하는 것이 훨씬 안정적입니다.
    query = "site:whitehouse.gov/briefing-room"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    print(f"📡 구글 검색 엔진을 통해 백악관 데이터 강제 수집 중...")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        if not feed.entries:
            print("⚠️ 구글 뉴스에서도 데이터를 찾지 못했습니다. 쿼리를 확인하세요.")
            return

        for entry in feed.entries:
            # 발행일 파싱
            pub_date_struct = entry.published_parsed
            pub_date_obj = datetime(*pub_date_struct[:3])
            pub_date_str = pub_date_obj.strftime('%Y-%m-%d')

            # 최근 10일 이내 데이터만 보관
            if pub_date_obj >= start_date:
                # 구글 뉴스 링크는 해독기 없이도 일단 클릭은 가능하므로 그대로 담습니다.
                all_data.append({
                    "발행일": pub_date_str,
                    "제목": entry.title.split(' - ')[0].strip(),
                    "링크": entry.link
                })

        # 3. CSV 저장 (데이터가 없어도 헤더는 생성하도록)
        file_name = 'whitehouse_news_decoded.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "링크"])
            writer.writeheader()
            if all_data:
                writer.writerows(all_data)
                print(f"✅ 성공: 총 {len(all_data)}건의 데이터를 찾아냈습니다!")
            else:
                print("⚠️ 조건에 맞는 최신 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
