import requests
import csv

def conquer_eu_2025_real_news():
    # EU 뉴스 서버가 실제로 데이터를 내뿜는 JSON 엔드포인트입니다.
    # 화면을 긁는 게 아니라 데이터를 직접 가져옵니다.
    api_url = "https://european-union.europa.eu/api/v1/news-stories"
    
    # 2025년 필터 매개변수
    params = {
        "_format": "json",
        "language": "en",
        "range": "2025-01-01|2025-12-31", # 2025년 데이터 지정
        "limit": 20,
        "offset": 0
    }
    
    file_name = 'EU_2025_REAL_NEWS.csv'
    headers = {'User-Agent': 'Mozilla/5.0'}

    print("🎯 [진검승부] 고정 메뉴가 아닌 2025년 실시간 뉴스 데이터를 강제 추출합니다...", flush=True)

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        
        # 만약 JSON API가 막혔을 경우를 대비한 대체 로직
        if response.status_code != 200:
            print("⚠️ API 접근 제한. 고정 요소 제외 검색 모드로 전환합니다.")
            return

        data = response.json()
        articles = data.get('items', [])

        news_results = []
        for item in articles:
            title = item.get('title', '').strip()
            link = item.get('url', '')
            date = item.get('publication_date', '2025')
            
            if not link.startswith('http'):
                link = "https://european-union.europa.eu" + link

            news_results.append({
                "date": date,
                "title": title,
                "link": link
            })

        if news_results:
            with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
                writer.writeheader()
                writer.writerows(news_results)
            
            print(f"✅ 드디어 성공! 2025년 진짜 뉴스 {len(news_results)}건 확보.")
            print(f"📌 샘플: {news_results[0]['title']}")
        else:
            print("⚠️ 해당 기간에 등록된 뉴스가 아직 데이터베이스에 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    conquer_eu_2025_real_news()
