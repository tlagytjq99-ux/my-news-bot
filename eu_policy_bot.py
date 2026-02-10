import requests
from bs4 import BeautifulSoup
import csv
import re

def crawl_eu_2025_news_v2():
    # 2025년 필터가 적용된 URL
    target_url = "https://european-union.europa.eu/news-and-events/news-and-stories_en?f%5B0%5D=oe_news_publication_date%3Abt%7C2025-01-01T02%3A12%3A07%2B01%3A00%7C2025-12-31T02%3A12%3A07%2B01%3A00"
    file_name = 'EU_News_2025_Final.csv'
    
    # 브라우저인 척 속이기 위한 강력한 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    print("🚀 [2025 정밀 사냥] 이번에는 놓치지 않습니다. 스캔 시작...", flush=True)

    try:
        response = requests.get(target_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 모든 링크 중에서 '/news/'가 포함된 뉴스 기사 링크만 필터링
        # EU 뉴스는 주소에 반드시 '/news/'가 들어갑니다.
        news_links = soup.find_all('a', href=re.compile(r'/news/'))
        
        final_news = []
        seen_links = set()

        for link_tag in news_links:
            url = link_tag['href']
            # 절대 경로로 변환
            full_url = url if url.startswith('http') else "https://european-union.europa.eu" + url
            
            # 제목 추출 (이미지 링크 등은 제외하기 위해 텍스트가 있는 경우만)
            title = link_tag.get_text(strip=True)
            
            # 중복 제거 및 짧은 제목(더보기 등) 필터링
            if full_url not in seen_links and len(title) > 20:
                final_news.append({
                    "date": "2025",
                    "title": title,
                    "link": full_url
                })
                seen_links.add(full_url)

        if final_news:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(final_news)
            
            print("\n" + "🏆"*20)
            print(f"2025년 데이터 정복 성공! 총 {len(final_news)}건 확보")
            print(f"저장된 파일: {file_name}")
            print("🏆"*20)
            for i, item in enumerate(final_news[:5], 1):
                print(f"{i}. {item['title']}")
                print(f"   🔗 {item['link']}\n")
        else:
            # 실패 시 소스 코드 일부를 출력하여 제가 분석할 수 있게 합니다.
            print("⚠️ 여전히 데이터를 찾지 못했습니다. 소스 분석을 위해 일부 내용을 확인합니다.")
            print(f"검색된 총 링크 수: {len(soup.find_all('a'))}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    crawl_eu_2025_news_v2()
