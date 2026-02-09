import requests
from bs4 import BeautifulSoup
import csv

def scrape_eu_portal_real_data():
    # 1. 대표님이 주신 2025년 검색 결과 페이지 주소
    url = "https://op.europa.eu/en/search-results"
    params = {
        "p_p_id": "eu_europa_publications_portlet_facet_search_result_FacetedSearchResultPortlet_INSTANCE_TTTP7nyqSt8X",
        "p_p_lifecycle": "0",
        "facet.documentYear": "2025",
        "facet.collection": "EUPub",
        "resultsPerPage": "100"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print("⛏️ 2025년 실제 정책 데이터를 발굴하는 중...", flush=True)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 검색 결과 아이템들 찾기
        items = soup.select('.search-result-item') # 포털의 검색 결과 아이템 클래스
        
        collected_data = []
        
        for item in items:
            title_tag = item.select_one('.result-title a')
            date_tag = item.select_one('.metadata-value') # 날짜가 포함된 메타데이터
            
            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag['href']
                date = date_tag.get_text(strip=True) if date_tag else "2025"
                
                collected_data.append({
                    "date": date,
                    "title": title,
                    "link": link if link.startswith('http') else f"https://op.europa.eu{link}"
                })

        # 2. 파일 저장 (샘플 데이터 대신 실제 데이터 저장)
        file_name = 'EU_Policy_2025_Full.csv'
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            
            if collected_data:
                writer.writerows(collected_data)
                print(f"✅ 성공! 실제 2025년 정책 {len(collected_data)}건을 수집했습니다.", flush=True)
            else:
                # 데이터가 안 잡힐 경우를 대비한 최소한의 기록
                writer.writerow({"date": "2025-02-09", "title": "Check: Data exists on web but scraping needs adjustment", "link": url})
                print("⚠️ 웹페이지 구조가 예상과 달라 데이터를 추출하지 못했습니다.", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    scrape_eu_portal_real_data()
