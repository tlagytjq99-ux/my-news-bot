import requests
import csv
import os
import time

def fetch_eu_publications_2025_all():
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    params = {
        "filters": "catalogue:cellar", 
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,issued",
        "limit": 100,
        "page": 0
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_publications = []
    
    print(f"🚀 [시작] 2025년 데이터 수집을 가동합니다. (파일명: {file_name})", flush=True)

    try:
        while True:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"⚠️ API 응답 이상: {response.status_code}", flush=True)
                break
            
            data = response.json()
            results = data.get('result', {}).get('results', [])
            
            if not results:
                print("🏁 더 이상 가져올 데이터가 없습니다.", flush=True)
                break
            
            for item in results:
                title = item.get('title', {}).get('en', 'No English Title')
                issued_date = item.get('issued', 'N/A')
                doc_id = item.get('id', '')
                link = f"https://data.europa.eu/data/datasets/{doc_id}?locale=en"
                
                all_publications.append({
                    "date": issued_date[:10],
                    "title": title,
                    "link": link
                })
            
            print(f"📦 현재 {len(all_publications)}건 확보 중... (페이지 {params['page'] + 1})", flush=True)
            
            # 테스트를 위해 너무 많이 돌지 않도록 임시 제한 (성공 확인용)
            if params['page'] >= 10: 
                print("💡 테스트 수집 한도(10페이지) 도달. 저장을 시작합니다.", flush=True)
                break
                
            params['page'] += 1
            time.sleep(0.2)

    except Exception as e:
        print(f"❌ 실행 중 에러 발생: {e}", flush=True)

    # [저장 로직 강화]
    if all_publications:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_publications)
        
        # 파일이 실제로 생성되었는지 체크
        if os.path.exists(file_name):
            print(f"✅ [성공] {file_name} 파일이 {os.path.getsize(file_name)} 바이트 크기로 생성되었습니다!", flush=True)
        else:
            print(f"❌ [실패] 파일 쓰기에 실패했습니다.", flush=True)
    else:
        print("⚠️ 수집된 데이터가 없어 파일을 만들지 않았습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_publications_2025_all()
