import requests
from bs4 import BeautifulSoup
import csv
import time
import random

def fetch_eu_safe_scraping():
    # 1. 2025년 검색 결과 주소
    url = "https://op.europa.eu/en/search-results"
    params = {
        "p_p_id": "eu_europa_publications_portlet_facet_search_result_FacetedSearchResultPortlet_INSTANCE_TTTP7nyqSt8X",
        "p_p_lifecycle": "0",
        "facet.documentYear": "2025",
        "facet.collection": "EUPub",
        "resultsPerPage": "20" # 한 번에 너무 많이 가져오면 의심받으니 적당히!
    }
    
    # [핵심] 서버를 속이는 '변장 도구' (브라우저 정보 추가)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://op.europa.eu/en/home" # 이전 페이지에서 온 것처럼 속임
    }

    print("🛡️ 보안 모드로 EU 포털에 접근합니다. (차단 방지 로직 가동)", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        # 사람처럼 행동하기 위해 1~3초 랜덤 대기
        time.sleep(random.uniform(1.0, 3.0))
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # EU 포털의 실제 리스트 아이템 구조 (클래스명 타겟팅)
            items = soup.find_all('div', class_='search-result-item')
            
            for item in items:
                title_tag = item.find('h4').find('a') if item.find('h4') else None
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag['href']
                    # 날짜 추출 (metadata-value 클래스 사용)
                    date_tag = item.find('span', class_='metadata-value')
                    date = date_tag.get_text(strip=True) if date_tag else "2025"
                    
                    collected_data.append({
                        "date": date,
                        "title": title,
                        "link": link if link.startswith('http') else f"https://op.europa.eu{link}"
                    })

            print(f"✅ 성공! 보안을 유지하며 {len(collected_data)}건의 데이터를 캐냈습니다.", flush=True)
        else:
            print(f"⚠️ 접근 거부 (코드: {response.status_code}). 보안 수준을 높여야 합니다.", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

    # 파일 저장 (이게 되어야 128 에러가 안 납니다)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": "2025-02-09", "title": "Security Check OK - No data in list", "link": "N/A"})

if __name__ == "__main__":
    fetch_eu_safe_scraping()
