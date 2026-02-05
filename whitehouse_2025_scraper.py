import feedparser
import csv
import urllib.parse
from datetime import datetime
from googlenewsdecoder import gnewsdecoder
import time

def main():
    # 1. 5G/6G 전용 정밀 쿼리 (2025년 한정)
    target_site = "whitehouse.gov/presidential-actions/"
    # 5G, 6G, 주파수(Spectrum) 관련 핵심 키워드만 검색어에 포함
    keywords = "(5G OR 6G OR Spectrum OR Wireless OR NTIA OR Connectivity)"
    query = f"site:{target_site} {keywords} after:2025-01-01 before:2026-01-01"
    
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

    print(f"📡 [5G/6G 전용 모드] 2025년 주파수 및 네트워크 정책 스캔 시작...")

    try:
        feed = feedparser.parse(rss_url)
        results = []

        for entry in feed.entries:
            try:
                pub_date = datetime(*entry.published_parsed[:3])
                if pub_date.year != 2025: continue

                title = entry.title.split(' - ')[0].strip()
                
                # 'Archives' 등 목록 페이지 제거
                if any(noise in title for noise in ["Archives", "Page", "Presidential Actions"]):
                    continue

                # 구글 우회 디코딩
                try:
                    decoded = gnewsdecoder(entry.link)
                    actual_url = decoded.get('decoded_url', entry.link)
                except:
                    actual_url = entry.link

                # 5G/6G 키워드가 실제 제목에 있는지 최종 확인 (정밀도 향상)
                if any(kw.lower() in title.lower() for kw in ["5g", "6g", "spectrum", "wireless", "network"]):
                    results.append({
                        "발행일": pub_date.strftime('%Y-%m-%d'),
                        "카테고리": "1. 5G/6G Network",
                        "제목": title,
                        "원문링크": actual_url
                    })
                time.sleep(0.05)
            except: continue

        # 3. CSV 저장
        file_name = 'whitehouse_5G6G_2025_report.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["발행일", "카테고리", "제목", "원문링크"])
            writer.writeheader()
            
            if results:
                results.sort(key=lambda x: x['발행일'], reverse=True)
                writer.writerows(results)
                print(f"✅ 성공: 총 {len(results)}건의 5G/6G 관련 정책을 찾았습니다.")
            else:
                print("⚠️ 해당 카테고리의 2025년 정책을 찾지 못했습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
