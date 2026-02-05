import feedparser
import csv
import urllib.parse
from datetime import datetime, timedelta
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 설정: 최근 1주일(7일) 및 중국어 키워드
    days_limit = 7
    # "人工智能 政策" (인공지능 정책) 키워드 사용
    keyword = '"人工智能 政策"' 
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_limit)
    
    # 2. 중국 구글 뉴스 RSS 쿼리 생성
    # hl=zh-CN (중국어 간체), gl=CN (중국 지역) 설정
    encoded_query = urllib.parse.quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

    print(f"📡 중국 구글 뉴스에서 '{keyword}' 관련 소식 수집 중... (최근 {days_limit}일)")

    try:
        feed = feedparser.parse(rss_url)
        all_data = []

        for entry in feed.entries:
            try:
                pub_date_struct = entry.published_parsed
                pub_date_obj = datetime(*pub_date_struct[:3])
            except:
                continue

            # 1주일 이내 데이터 필터링
            if pub_date_obj >= start_date:
                raw_title = entry.title.split(' - ')[0].strip()
                
                # 링크 해독 (중국 언론사 원문 주소로 변환)
                try:
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
                time.sleep(0.1)

        # 3. CSV 저장
        file_name = 'china_ai_policy_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "언론사", "제목", "원문링크"])
            writer.writeheader()
            if all_data:
                all_data.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(all_data)
                print(f"✅ 수집 성공: 총 {len(all_data)}건의 중국 AI 정책 관련 소식을 확보했습니다.")
            else:
                print(f"⚠️ 결과 없음: 최근 {days_limit}일 내에 해당 키워드의 뉴스가 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
