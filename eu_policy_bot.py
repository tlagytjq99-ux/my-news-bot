import requests
from bs4 import BeautifulSoup
import csv

def crawl_eu_2025_news():
    # 대표님이 주신 2025년 필터링 URL
    target_url = "https://european-union.europa.eu/news-and-events/news-and-stories_en?f%5B0%5D=oe_news_publication_date%3Abt%7C2025-01-01T02%3A12%3A07%2B01%3A00%7C2025-12-31T02%3A12%3A07%2B01%3A00"
    file_name = 'EU_News_2025_List.csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print("🚀 [2025 뉴스 사냥] 데이터를 수집 중입니다...", flush=True)

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 기사 아이템들을 찾습니다 (보통 특정 클래스를 가진 div 내에 존재)
        articles = soup.select('div.views-row') # 페이지 구조에 따른 선택자

        news_list = []
        for article in articles:
            # 제목과 링크 추출
            title_tag = article.select_one('h3 a') or article.select_one('h2 a')
            if not title_tag: continue
            
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            if not link.startswith('http'):
                link = "https://european-union.europa.eu" + link

            # 날짜 추출
            date_tag = article.select_one('span.oe-news-publication-date') or article.select_one('time')
            date = date_tag.get_text(strip=True) if date_tag else "2025"

            news_list.append({
                "date": date,
                "title": title,
                "link": link
            })

        if news_list:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(news_list)
            
            print(f"✅ 성공! 2025년 주요 뉴스 {len(news_list)}건을 수집했습니다.")
            print(f"📂 파일명: {file_name}")
            # 샘플 출력
            print(f"\n📌 최신 뉴스 예시: {news_list[0]['title']}")
        else:
            print("⚠️ 데이터를 찾지 못했습니다. 페이지 구조를 다시 분석해야 합니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    crawl_eu_2025_news()
