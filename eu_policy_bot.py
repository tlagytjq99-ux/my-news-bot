import requests
import csv

def fetch_eu_policy_focus_2025():
    # 검증된 CKAN 표준 검색 통로
    url = "https://data.europa.eu/api/hub/search/search"
    
    # [정책 포커스 전략] 
    # 1. 키워드: 정책, 법령, 규제 (OR 연산으로 하나라도 포함되면 수집)
    # 2. 필터: 2025년 1월 1일 이후 수정된 데이터셋
    params = {
        "q": "title:policy OR title:legislation OR title:regulation", 
        "fq": "metadata_modified:[2025-01-01T00:00:00Z TO NOW]",
        "rows": 100,
        "sort": "metadata_modified desc"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    print("🇪🇺 [정책 포커스] 2025년 EU 정책 및 법령 데이터 수집 시작...", flush=True)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            datasets = data.get('result', {}).get('results', [])
            
            results = []
            for ds in datasets:
                # 데이터 정리
                results.append({
                    "수정일": ds.get('metadata_modified', 'N/A')[:10],
                    "정책제목": ds.get('title', 'No Title'),
                    "발행처": ds.get('organization', {}).get('title', 'N/A'),
                    "카테고리": ", ".join([t.get('id', '') for t in ds.get('theme', [])]) if ds.get('theme') else "N/A",
                    "상세링크": f"https://data.europa.eu/data/datasets/{ds.get('name')}"
                })
            
            if results:
                file_name = 'EU_2025_Policy_Focus.csv'
                with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=["수정일", "정책제목", "발행처", "카테고리", "상세링크"])
                    writer.writeheader()
                    writer.writerows(results)
                print(f"✅ 수집 성공! 2025년 주요 정책 데이터 {len(results)}건을 확보했습니다.", flush=True)
            else:
                print("⚪ 2025년 날짜로 등록된 정책 데이터셋이 아직 없습니다. (추후 자동 실행 시 수집될 예정입니다.)", flush=True)
        else:
            print(f"❌ 접속 실패: {response.status_code}", flush=True)
            print(f"📡 서버 메시지: {response.text[:200]}", flush=True)

    except Exception as e:
        print(f"❌ 오류 발생: {e}", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_focus_2025()
