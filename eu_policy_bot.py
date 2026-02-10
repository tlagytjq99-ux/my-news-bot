import requests
from bs4 import BeautifulSoup
import csv

def fetch_2025_news_perfect():
    # 2025년 필터링된 주소
    url = "https://european-union.europa.eu/news-and-events/news-and-stories_en?f%5B0%5D=oe_news_publication_date%3Abt%7C2025-01-01T02%3A12%3A07%2B01%3A00%7C2025-12-31T02%3A12%3A07%2B01%3A00"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print("🎯 [정밀 타격] 메뉴/푸터 무시하고 '뉴스 알맹이'만 도려냅니다...", flush=True)

    try:
        res = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')

        # [핵심] EU 뉴스 사이트에서 기사가 들어있는 구역만 딱 집어냅니다.
        # 이 구역 밖의 'Call us', 'Mission' 등은 모두 무시됩니다.
        news_items = soup.find_all('div', class_='ecl-content-block')

        results = []
        for item in news_items:
            title_tag = item.find('h2') or item.find('h3')
            link_tag = item.find('a')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                if not link.startswith('http'):
                    link = "https://european-union.europa.eu" + link
                
                # 'Call us' 같은 메뉴성 텍스트가 포함된 경우 걸러내기
                if any(x in title.lower() for x in ['call us', 'contact', 'mission', 'about']):
                    continue
                    
                results.append({"title": title, "link": link})

        if results:
            with open('EU_2025_NEWS_CLEAN.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["title", "link"])
                writer.writeheader()
                writer.writerows(results)
            print(f"✅ 성공! 진짜 2025년 뉴스 {len(results)}건 확보!")
            print(f"📌 첫 기사: {results[0]['title']}")
        else:
            print("⚠️ 뉴스 구역을 찾는 데 실패했습니다. EU가 클래스명을 숨겼을 수 있습니다.")

    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    fetch_2025_news_perfect()
