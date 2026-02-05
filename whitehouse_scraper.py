import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
from googlenewsdecoder import gnewsdecoder  # 👈 링크 해독을 위해 필수
import time

def main():
    # 1. 최근 1주일 기간 설정
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime("%Y-%m-%d")

    # 2. 구글 뉴스 검색 쿼리 (백악관 뉴스룸 전체 소식)
    # 키워드 없이 site만 지정하여 전수 수집
    query = f"site:whitehouse.gov/briefing-room after:{start_str}"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US"

    print(f"📡 구글 뉴스를 통해 백악관 소식 우회 수집 중... ({start_str} 이후)")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        for entry in feed.entries:
            raw_title = entry.title.split(' - ')[0].strip()
            pub_date = datetime(*entry.published_parsed[:3]).strftime('%Y-%m-%d')
            
            # 3. 🔥 구글 뉴스 링크 해독 (Decoding)
            try:
                # 구글의 암호화된 링크를 실제 원문 주소로 변환
                decoded = gnewsdecoder(entry.link)
                actual_link = decoded.get('decoded_url', entry.link)
            except:
                actual_link = entry.link  # 실패 시 원본 유지

            all_data.append({
                "발행일": pub_date,
                "제목": raw_title,
                "원문링크": actual_link
            })
            # 구글 서버 부하 방지를 위해 아주 잠깐 대기
            time.sleep(0.1)

        # 4. CSV 저장
        file_name = 'whitehouse_news_decoded.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "원문링크"])
            writer.writeheader()
            writer.writerows(all_data)

        print(f"✅ 해독 완료: 총 {len(all_data)}건 저장됨.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
