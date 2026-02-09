import requests
import csv
import time

def search_eu_hub_2025():
    # 데이터 허브 검색 엔드포인트
    url = "https://data.europa.eu/api/hub/search/datasets"
    
    # 400 에러 방지를 위해 가장 안정적인 파라미터만 사용
    params = {
        "q": "policy",               # 검색어
        "limit": "100",              # 한 번에 100개씩
        "sort": "modified-desc",      # 최근 수정된 순서대로 (2025년이 위로 오게)
        "language": "en"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    print("🇪🇺 EU Data Hub 정밀 검색 시작 (2025년 데이터 필터링)...", flush=True)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # API 응답 구조: result -> datasets
            datasets = data.get('result', {}).get('datasets', [])
            
            results = []
            for ds in datasets:
                modified_date = ds.get('modified', '') # 수정일 확인
                
                # 2025년에 생성되거나 수정된 데이터만 골라냅니다.
                if "2025" in modified_date:
                    results.append({
                        "발행일": modified_date,
                        "제목": ds.get('title', {}).get('en', 'No Title'),
                        "발행처": ds.get('publisher', {}).get('name', 'N/A'),
                        "상세주소": f"https://data.europa.eu/data/datasets/{ds.get('id')}"
                    })
            
            if results:
                file_name = 'EU_Hub_Policy_2025.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "발행처", "상세주소"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 성공! 2025년 관련 데이터셋 {len(results)}개를 찾았습니다.", flush=True)
            else:
                print("⚪ 검색 결과 중 2025년 데이터가 아직 없습니다.", flush=True)
                
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            print(f"🔗 시도한 URL: {response.url}", flush=True)
            
    except Exception as e:
        print(f"❌ 시스템 오류: {e}", flush=True)

if __name__ == "__main__":
    search_eu_hub_2025()
