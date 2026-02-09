import requests
import csv
import os
import time

def fetch_eu_publications_2025_all():
    # 1. API 엔드포인트
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # [핵심] 대표님이 주신 RSS의 정체인 'CELLAR'(간행물) 카탈로그를 타겟팅합니다.
    params = {
        "filters": "catalogue:cellar", # 국가 데이터 제외, 간행물 전용
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,issued",
        "limit": 100,  # 한 번에 100개씩 요청
        "page": 0
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_publications = []
    
    print("🚀 2025년 EU 정책 간행물 전수 조사를 시작합니다...", flush=True)

    while True:
        try:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200:
                break
            
            data = response.json()
            results = data.get('result', {}).get('results', [])
            
            if not results:
                print("🏁 모든 데이터를 수집했습니다.", flush=True)
                break
            
            for item in results:
                title = item.get('title', {}).get('en', 'No English Title')
                issued_date = item.get('issued', 'N/A')
                doc_id = item.get('id', '')
                
                # 간행물 상세 페이지 링크
                link = f"https://data.europa.eu/data/datasets/{doc_id}?locale=en"
                
                all_publications.append({
                    "date": issued_date[:10],
                    "title": title,
                    "link": link
                })
            
            print(f"📦 {params['page'] + 1}페이지 완료 (누적 {len(all_publications)}건)...", flush=True)
            
            # 다음 페이지로 이동
            params['page'] += 1
            time.sleep(0.1) # 서버 예우용 살짝 대기

        except Exception as e:
            print(f"❌ 오류 발생: {e}", flush=True)
            break

    # 2. CSV 저장
    if all_publications:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_publications)
        print(f"🎯 전수 수집 성공! 총 {len(all_publications)}건 저장 완료.", flush=True)

if __name__ == "__main__":
    fetch_eu_publications_2025_all()
