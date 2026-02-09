import requests
import csv
import json

def fetch_eu_hub_final():
    # 대표님이 주신 공식 검색 엔드포인트
    url = "https://data.europa.eu/api/hub/search/search"
    
    # 2025년 데이터를 타겟으로 하는 정밀 파라미터
    params = {
        "q": "policy", # 정책 키워드
        "filters": "catalogue,dataset,resource",
        "limit": 100,
        "sort": "modified-desc", # 최신순
        # 대표님 링크에 있던 핵심: 모든 항목을 리스트로 명시해야 에러가 안 납니다.
        "facets": json.dumps({
            "country": ["eu"],
            "catalog": [],
            "format": [],
            "scoring": [],
            "license": [],
            "categories": [],
            "publisher": [],
            "subject": [],
            "keywords": [],
            "is_hvd": [],
            "hvdCategory": [],
            "superCatalog": [],
            "mostLiked": []
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    print("🇪🇺 [최종 공략] EU 데이터 허브에서 2025년 정책 데이터셋을 전수 조사합니다...", flush=True)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            datasets = data.get('result', {}).get('datasets', [])
            
            results = []
            for ds in datasets:
                modified_date = ds.get('modified', 'N/A')
                
                # 2025년 데이터만 선별
                if "2025" in modified_date:
                    results.append({
                        "수정일": modified_date[:10],
                        "제목": ds.get('title', {}).get('en', 'No Title'),
                        "기관": ds.get('publisher', {}).get('name', 'N/A'),
                        "상세주소": f"https://data.europa.eu/data/datasets/{ds.get('id')}"
                    })
            
            if results:
                file_name = 'EU_2025_Policy_Final.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["수정일", "제목", "기관", "상세주소"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 대성공! 2025년 정책 데이터 {len(results)}건 수집 완료!", flush=True)
            else:
                print("⚪ 접속은 성공했으나, 2025년 날짜의 데이터셋은 아직 등록 전입니다.", flush=True)
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            print(f"📡 서버 메시지: {response.text[:200]}", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_hub_final()
