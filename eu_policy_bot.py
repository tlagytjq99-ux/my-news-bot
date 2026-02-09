import requests
import csv

def search_eu_hub():
    # EU Data Hub 검색 엔드포인트
    url = "https://data.europa.eu/api/hub/search/datasets"
    
    # 검색 조건 설정
    params = {
        "q": "policy",             # 검색어
        "limit": 50,               # 가져올 개수
        "sort": "modified-desc",    # 최근 수정순
        "facets": '{"issued_after":["2025-01-01T00:00:00Z"]}' # 2025년 이후 발행
    }
    
    print("🇪🇺 EU Data Hub에서 2025년 정책 데이터셋 검색 중...", flush=True)
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # 검색 결과는 result['datasets'] 안에 들어있습니다.
            datasets = data.get('result', {}).get('datasets', [])
            
            results = []
            for ds in datasets:
                results.append({
                    "제목": ds.get('title', {}).get('en', 'No Title'),
                    "설명": ds.get('description', {}).get('en', 'No Description')[:100] + "...",
                    "발행기관": ds.get('publisher', {}).get('name', 'N/A'),
                    "수정일": ds.get('modified', 'N/A'),
                    "상세링크": f"https://data.europa.eu/data/datasets/{ds.get('id')}"
                })
            
            if results:
                with open('EU_Hub_Datasets_2025.csv', 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["제목", "설명", "발행기관", "수정일", "상세링크"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 총 {len(results)}개의 정책 데이터셋 목록을 저장했습니다!", flush=True)
            else:
                print("⚪ 조건에 맞는 데이터셋을 찾지 못했습니다.", flush=True)
        else:
            print(f"❌ 에러 발생: {response.status_code}", flush=True)
            
    except Exception as e:
        print(f"❌ 오류: {e}", flush=True)

if __name__ == "__main__":
    search_eu_hub()
