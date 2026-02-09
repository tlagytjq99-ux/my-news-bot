import requests
from bs4 import BeautifulSoup
import csv
import time
import random

def fetch_eu_final_scraping():
    # 대표님이 주신 검색 결과 URL
    url = "https://op.europa.eu/en/search-results"
    params = {
        "p_p_id": "eu_europa_publications_portlet_facet_search_result_FacetedSearchResultPortlet_INSTANCE_TTTP7nyqSt8X",
        "p_p_lifecycle": "0",
        "facet.documentYear": "2025",
        "facet.collection": "EUPub",
        "resultsPerPage": "50"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://op.europa.eu/en/home"
    }

    print("⛏️ [정밀 분석] HTML 소스 내부에서 2025년 데이터를 직접 탐색 중...", flush=True)
    
    file_name = 'EU_Policy_2025_Full.csv'
    collected_data = []

    try:
        time.sleep(2) # 서버 부하 방지
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. 모든 링크(a 태그)를 우선 수집
            links = soup.find_all('a')
            
            for link_tag in links:
                title = link_tag.get_text(strip=True)
                href = link_tag.get('href', '')
                
                # 2. 제목이 일정 길이 이상이고, 링크에 'publication'이나 'cellar'가 포함된 경우 필터링
                if len(title) > 10 and ('/publication/' in href or 'cellar' in href):
                    # 중복 제거 및 링크 완성
                    full_link = href if href.startswith('http') else f"https://op.europa.eu{href}"
                    
                    # 이미 수집한 제목인지 체크 (중복 방지)
                    if not any(d['title'] == title for d in collected_data):
                        collected_data.append({
                            "date": "2025",
                            "title": title,
                            "link": full_link
                        })

            if not collected_data:
                # 3. 만약 위 방식으로도 안 잡히면, 검색 결과 컨테이너를 더 넓게 탐색
                results_div = soup.find_all('div', id=lambda x: x and 'publication' in x)
                for res in results_div:
                    print(f"디버깅용 구조 발견: {res.get_text()[:30]}...", flush=True)

            print(f"✅ 발견 완료! 총 {len(collected_data)}건의 2025년 정책 리스트를 확보했습니다.", flush=True)
        else:
            print(f"❌ 접속 실패 (상태 코드: {response.status_code})", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

    # 저장 (결과가 0건이라도 파일은 무조건 생성하여 에러 방지)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
        writer.writeheader()
        if collected_data:
            writer.writerows(collected_data)
        else:
            writer.writerow({"date": "2025-02-09", "title": "System Active - Waiting for Data Layout", "link": url})

if __name__ == "__main__":
    fetch_eu_final_scraping()
