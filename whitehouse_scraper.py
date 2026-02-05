import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 설정: 3개월(90일) 및 정식 키워드
    days_limit = 90
    # "Artificial Intelligence" 문구가 정확히 일치하는 결과만 찾도록 설정
    keyword = '"artificial intelligence"' 
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_limit)
    
    # 2. 구글 뉴스 RSS 쿼리 생성
    # site 연산자와 키워드를 조합하여 백악관 내 정식 명칭 언급 문서 타겟팅
    query = f'{keyword} site:whitehouse.gov'
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    print(f"📡 백악관 {keyword} 관련 정책 수집 및 링크 해독 중... (최근 {days_limit}일)")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        for entry in feed.entries:
            try:
                pub_date_struct = entry.published_parsed
                pub_date_obj = datetime(*pub_date_struct[:3])
            except:
                continue

            # 기간 필터링
            if pub_date_obj >= start_date:
                raw_title = entry.title.split(' - ')[0].strip()
                
                # 3. 구글 뉴스 링크 해독 (백악관 공식 URL로 변환)
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

        # 4. CSV 파일 저장
        file_name = 'whitehouse_ai_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "원문링크"])
            writer.writeheader()
            if all_data:
                all_data.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(all_data)
                print(f"✅ 수집 성공: 총 {len(all_data)}건의 전문 정책 자료를 확보했습니다.")
            else:
                print(f"⚠️ 결과 없음: 최근 {days_limit}일 내에 해당 키워드의 자료가 인덱싱되지 않았습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
