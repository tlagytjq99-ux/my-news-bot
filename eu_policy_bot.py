import requests
import csv
import os
import time

def fetch_eu_policy_final():
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # [전략 변경] 복잡한 필터 대신, 검색어(q)를 통해 '정책 문서'를 직접 타격합니다.
    params = {
        "q": "policy OR strategy OR report OR proposal", # 정책 핵심 키워드
        "filters": "catalogue:cellar", # EU 공식 간행물 저장소(Cellar) 지정
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,issued",
        "limit": 50,
        "page": 0,
        "sort": "issued-desc"
    }

    file_name = 'EU_Policy_2025_Full.csv'
    all_records = []
    
    print(f"📡 [최종 승부] 2025년 정책 키워드 검색을 시작합니다...", flush=True)

    try:
        # 우선 첫 페이지만 시도해서 데이터가 있는지 확인
        response = requests.get(api_url, params=params, timeout=30)
        print(f"🔍 API 응답 상태: {response.status_code}", flush=True)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('result', {}).get('results', [])
            
            if not results:
                print("⚠️ 검색 결과가 없습니다. 필터를 완화하여 재시도합니다...", flush=True)
                # 필터를 더 넓게 잡아서 재요청
                params.pop("filters")
                response = requests.get(api_url, params=params, timeout=30)
                data = response.json()
                results = data.get('result', {}).get('results', [])

            # 데이터 처리 루프
            while results:
                for item in results:
                    title_data = item.get('title', {})
                    title = title_data.get('en') if isinstance(title_data, dict) else str(title_data)
                    
                    if title and title != 'None':
                        issued_date = item.get('issued', '2025-XX-XX')
                        doc_id = item.get('id', '')
                        link = f"https://data.europa.eu/data/datasets/{doc_id}?locale=en"
                        
                        all_records.append({
                            "date": issued_date[:10],
                            "title": title.strip(),
                            "link": link
                        })
                
                print(f"✅ {params['page'] + 1}페이지 완료 (누적 {len(all_records)}건)", flush=True)
                
                # 다음 페이지 준비
                params['page'] += 1
                if params['page'] > 10: break # 안정성을 위해 우선 500건만
                
                time.sleep(0.3)
                response = requests.get(api_url, params=params, timeout=30)
                results = response.json().get('result', {}).get('results', [])
        else:
            print(f"❌ API 연결 실패: {response.text}", flush=True)

    except Exception as e:
        print(f"❌ 실행 오류: {e}", flush=True)

    # 결과 저장
    if all_records:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_records)
        print(f"💾 [성공] {len(all_records)}건의 정책 데이터를 {file_name}에 저장했습니다!", flush=True)
    else:
        print("⚠️ 최종적으로 수집된 데이터가 없습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_policy_final()
