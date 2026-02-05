import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
import time

def main():
    # 1. 기간 설정 (최근 14일로 더 넉넉하게 - 회의용 데이터 확보)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    
    # 2. 구글이 가장 선호하는 검색 연산자로 변경
    # site 전체에서 검색하되, 제목이나 본문에 Briefing Room이 포함된 것 위주
    query = 'site:whitehouse.gov "Briefing Room"'
    encoded_query = urllib.parse.quote(query)
    
    # hl=en-US, gl=US를 명시하여 미국 본토 데이터 강제 호출
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    print(f"📡 [긴급] 구글 인덱스 강제 쿼리 실행 중...")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        if not feed.entries:
            # 만약 이것도 안 나오면 일반적인 'White House' 키워드로 3차 시도
            print("⚠️ 2차 쿼리 실패, 3차 광범위 검색 시도...")
            query = 'White House "Statements and Releases"'
            encoded_query = urllib.parse.quote(query)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            # 날짜 처리
            try:
                pub_date_struct = entry.published_parsed
                pub_date_obj = datetime(*pub_date_struct[:3])
            except:
                continue

            # 날짜 필터링
            if pub_date_obj >= start_date:
                all_data.append({
                    "발행일": pub_date_obj.strftime('%Y-%m-%d'),
                    "제목": entry.title.split(' - ')[0].strip(),
                    "링크": entry.link
                })

        # 3. CSV 저장
        file_name = 'whitehouse_news_decoded.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "링크"])
            writer.writeheader()
            if all_data:
                # 최신순 정렬
                all_data.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(all_data)
                print(f"✅ [성공] {len(all_data)}건의 데이터를 확보했습니다!")
            else:
                print("⚠️ 검색 결과는 있으나 최근 14일 이내의 글이 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
