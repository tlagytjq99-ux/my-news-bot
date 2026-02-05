import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 설정: 최근 90일 & 정식 키워드
    days_limit = 90
    keyword = '"artificial intelligence"'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_limit)
    
    # 2. 쿼리 최적화: 사이트 경로를 /briefing-room 으로 한정
    # 이렇게 하면 팩트시트나 보고서가 아닌 '보도자료' 위주로 수집됩니다.
    query = f'{keyword} site:whitehouse.gov/briefing-room'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    print(f"📡 백악관 '뉴스룸' 내 {keyword} 소식 정밀 수집 중...")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        for entry in feed.entries:
            try:
                pub_date_struct = entry.published_parsed
                pub_date_obj = datetime(*pub_date_struct[:3])
            except:
                continue

            if pub_date_obj >= start_date:
                raw_title = entry.title.split(' - ')[0].strip()
                
                # 3. 구글 뉴스 링크 해독
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except:
                    actual_link = entry.link

                all_data.append({
                    "발행일": pub_date_obj.strftime('%Y-%m-%d'),
                    "제목": raw_title,
                    "원문링크": actual_link
                })
                time.sleep(0.1)

        # 4. CSV 저장
        file_name = 'whitehouse_briefing_only.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "원문링크"])
            writer.writeheader()
            if all_data:
                all_data.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(all_data)
                print(f"✅ 필터링 완료: 뉴스룸 데이터 총 {len(all_data)}건 확보.")
            else:
                print("⚠️ 뉴스룸 내에는 해당 기간의 AI 소식이 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
