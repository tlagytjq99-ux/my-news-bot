import requests
import csv

def fetch_eu_ckan_2025():
    # EU 데이터 허브의 표준 CKAN 통로입니다. (검증된 주소)
    url = "https://data.europa.eu/api/hub/search/search"
    
    # 파라미터 구조를 CKAN 표준에 맞춰서 다시 짰습니다.
    params = {
        "q": "policy",
        "rows": 100,               # limit 대신 rows 사용
        "sort": "metadata_modified desc" # 수정일 기준 내림차순
    }
    
    print("🇪🇺 EU 데이터 허브(CKAN 표준) 접속 시도 중...", flush=True)
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        # 로그로 주소를 확인합니다.
        print(f"📡 시도 URL: {response.url}", flush=True)
        print(f"📡 응답 코드: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            # CKAN 표준 응답 구조: result -> results
            datasets = data.get('result', {}).get('results', [])
            
            results = []
            for ds in datasets:
                modified = ds.get('metadata_modified', '')
                
                # 2025년 데이터만 필터링
                if "2025" in modified:
                    results.append({
                        "발행일": modified,
                        "제목": ds.get('title', 'No Title'),
                        "기관": ds.get('organization', {}).get('title', 'N/A'),
                        "링크": f"https://data.europa.eu/data/datasets/{ds.get('name')}"
                    })
            
            if results:
                file_name = 'EU_Hub_Standard_2025.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["발행일", "제목", "기관", "링크"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"🎉 성공! 2025년 정책 데이터셋 {len(results)}건 수집 완료!", flush=True)
            else:
                print("⚪ 2025년 날짜가 포함된 데이터셋을 찾지 못했습니다.", flush=True)
        else:
            print(f"❌ 또 400 에러가 난다면, 서버가 해당 파라미터 조합을 막은 것입니다.", flush=True)

    except Exception as e:
        print(f"❌ 시스템 오류: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_ckan_2025()
