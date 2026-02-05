import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 설정: 최근 7일 및 검색 키워드 최적화
    days_limit = 7
    # 큰따옴표를 제거하여 더 넓은 범위를 검색합니다.
    keyword = "人工智能 政策" 
    start_date = datetime.now() - timedelta(days=days_limit)
    
    # 2. 쿼리 최적화: 중국어(간체) 설정 유지
    encoded_query = urllib.parse.quote(keyword)
    # ceid=CN:zh-Hans 를 통해 중국어 간체 뉴스를 타겟팅합니다.
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

    print(f"📡 중국 구글 뉴스 수집 중... (키워드: {keyword})")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        for entry in feed.entries:
            try:
                # 구글 뉴스 날짜 형식 대응
                pub_date_struct = entry.published_parsed
                pub_date_obj = datetime(*pub_date_struct[:3])
            except:
                continue

            if pub_date_obj >= start_date:
                raw_title = entry.title.split(' - ')[0].strip()
                
                try:
                    # 링크 해독
                    decoded = gnewsdecoder(entry.link)
                    actual_link = decoded.get('decoded_url', entry.link)
                except:
                    actual_link = entry.link

                all_data.append({
                    "발행일": pub_date_obj.strftime('%Y-%m-%d'),
                    "언론사": entry.source.get('title', 'N/A') if hasattr(entry, 'source') else 'N/A',
                    "제목": raw_title,
                    "원문링크": actual_link
                })
                time.sleep(0.05)

        # 3. CSV 저장 (데이터가 없어도 헤더 포함 파일은 생성)
        file_name = 'china_ai_policy_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "언론사", "제목", "원문링크"])
            writer.writeheader()
            if all_data:
                all_data.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(all_data)
                print(f"✅ 성공: 총 {len(all_data)}건의 기사를 확보했습니다.")
            else:
                print(f"⚠️ 결과 없음: 키워드를 '{keyword}'로 변경하여 다시 시도했으나 데이터가 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
