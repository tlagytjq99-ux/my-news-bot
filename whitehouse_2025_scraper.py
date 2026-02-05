import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 2025년 데이터만 정밀 타겟팅하는 쿼리
    target_site = "whitehouse.gov/presidential-actions/"
    # 2025-01-01 이후 데이터만 가져오도록 구글에 명령
    query = f"site:{target_site} after:2025-01-01"
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    # 2. 사진 속 46개 카테고리 (핵심 키워드 매핑)
    category_db = {
        "1. 5G/6G Network": ["5G", "6G", "Open RAN", "Terahertz", "Network slicing"]
    }

    print(f"📅 2025년 백악관 정책 데이터 정밀 수집 시작...")

    try:
        feed = feedparser.parse(rss_url)
        results = []

        for entry in feed.entries:
            try:
                # 발행일 파싱 및 2025년 검증
                pub_date = datetime(*entry.published_parsed[:3])
                if pub_date.year < 2025:
                    continue # 2025년 이전 데이터는 과감히 삭제

                title = entry.title.split(' - ')[0].strip()
                
                # 아카이브/목차 페이지 제거 (진짜 문서만 수집)
                if any(noise in title for noise in ["Archives", "Page", "Presidential Actions"]):
                    continue

                # 구글 링크 우회 디코딩
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_url = decoded.get('decoded_url', entry.link)
                except:
                    actual_url = entry.link

                # 카테고리 매칭 (46개 필터링)
                matched_cats = []
                for cat, kws in category_db.items():
                    if any(kw.lower() in title.lower() for kw in kws):
                        matched_cats.append(cat)

                results.append({
                    "발행일": pub_date.strftime('%Y-%m-%d'),
                    "카테고리": ", ".join(matched_cats) if matched_cats else "일반 정책",
                    "문서유형": "Executive Order" if "/executive-orders/" in actual_url else "Presidential Action",
                    "제목": title,
                    "원문링크": actual_url
                })
                time.sleep(0.05)
            except: continue

        # 3. CSV 저장
        file_name = 'whitehouse_2025_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "카테고리", "문서유형", "제목", "원문링크"])
            writer.writeheader()
            
            if results:
                # 최신 날짜순 정렬
                results.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(results)
                print(f"✅ 성공: 총 {len(results)}건의 2025년 데이터를 수집 완료했습니다.")
            else:
                print("⚠️ 2025년 조건에 맞는 데이터가 검색 결과에 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
