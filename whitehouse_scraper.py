import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 설정
    days_limit = 90
    keyword = '"artificial intelligence"'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_limit)
    
    # 2. 쿼리는 다시 넓게 잡습니다 (그래야 구글이 데이터를 뱉습니다)
    query = f'{keyword} site:whitehouse.gov'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    print(f"📡 백악관 전체에서 {keyword} 관련 '뉴스형' 소식만 추출 중...")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        # 뉴스룸 성격의 URL 패턴들
        news_patterns = ['/briefings-statements/', '/articles/', '/speeches-remarks/', '/briefing-room/']

        for entry in feed.entries:
            try:
                pub_date_struct = entry.published_parsed
                pub_date_obj = datetime(*pub_date_struct[:3])
            except:
                continue

            if pub_date_obj >= start_date:
                raw_title = entry.title.split(' - ')[0].strip()
                
                # 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except:
                    actual_link = entry.link

                # 🔥 핵심: URL을 검사해서 뉴스룸 성격의 데이터만 담습니다.
                # PDF 파일이나 정책(priorities) 페이지는 제외됩니다.
                if any(pattern in actual_link for pattern in news_patterns):
                    all_data.append({
                        "발행일": pub_date_obj.strftime('%Y-%m-%d'),
                        "제목": raw_title,
                        "원문링크": actual_link
                    })
                
                time.sleep(0.1)

        # 3. CSV 저장
        file_name = 'whitehouse_news_only.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "원문링크"])
            writer.writeheader()
            if all_data:
                all_data.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(all_data)
                print(f"✅ 필터링 완료: 뉴스 성격의 데이터 총 {len(all_data)}건 확보.")
            else:
                print("⚠️ 뉴스룸 성격의 최신 데이터가 발견되지 않았습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
