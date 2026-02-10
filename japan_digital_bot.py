import feedparser
import csv

def collect_from_rss():
    # 디지털청 뉴스 RSS
    rss_url = "https://www.digital.go.jp/rss/news.xml"
    file_name = "Digital_Agency_RSS_Data.csv"
    
    print("📡 RSS 피드에서 최신 데이터를 추출합니다...")
    
    # RSS 파싱
    feed = feedparser.parse(rss_url)
    
    results = []
    for entry in feed.entries:
        # RSS가 제공하는 기본 정보: 제목, 링크, 발행일
        results.append({
            "date": entry.published if 'published' in entry else "N/A",
            "title": entry.title,
            "link": entry.link
        })
    
    # CSV 저장
    if results:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ RSS 수집 완료: 총 {len(results)}건 확보 (최신순)")
    else:
        print("❌ RSS에서 데이터를 가져오지 못했습니다.")

if __name__ == "__main__":
    collect_from_rss()
