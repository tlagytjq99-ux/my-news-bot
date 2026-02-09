import requests
import csv
import os

def fetch_eu_data_hub_all_2025():
    # 1. API 엔드포인트 및 대표님이 주신 파라미터 설정
    api_url = "https://data.europa.eu/api/hub/search/search"
    
    # 2025년 전체 데이터를 가져오기 위한 설정
    params = {
        "filters": "catalogue,dataset,resource",
        "dataScope": "eu",
        "dateType": "issued",
        "minDate": "2025-01-01T00:00:00.000Z",
        "maxDate": "2025-12-31T23:59:59.000Z",
        "includes": "id,title.en,description.en,issued,modified,publisher",
        "limit": 100,  # 한 번에 100개씩 (최대한 많이)
        "page": 0      # 시작 페이지
    }

    file_name = 'EU_Data_2025_All.csv'
    all_records = []
    
    print("📡 EU DATA HUB API 접속 중... 2025년 데이터를 수집합니다.", flush=True)

    while True:
        try:
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"❌ 오류 발생: {response.status_code}", flush=True)
                break
            
            data = response.json()
            # 검색 결과에서 실제 데이터(datasets) 추출
            results = data.get('result', {}).get('results', [])
            
            if not results:
                print("🏁 수집할 데이터가 더 이상 없습니다.", flush=True)
                break
            
            for item in results:
                # 영어 제목(title.en)이 없으면 기본 제목 사용
                title = item.get('title', {}).get('en', 'No English Title')
                issued_date = item.get('issued', 'N/A')
                doc_id = item.get('id', '')
                
                # 상세 링크 생성 (Data Europa 웹사이트 링크)
                link = f"https://data.europa.eu/data/datasets/{doc_id}?locale=en"
                
                all_records.append({
                    "date": issued_date[:10], # 날짜만 추출
                    "title": title,
                    "link": link
                })
            
            print(f"📦 현재까지 {len(all_records)}건 수집 완료...", flush=True)
            
            # 다음 페이지로 이동
            params['page'] += 1
            
            # API 부하 방지 (잠시 대기)
            import time
            time.sleep(0.1)

        except Exception as e:
            print(f"❌ 루프 중단 오류: {e}", flush=True)
            break

    # 2. CSV 저장
    if all_records:
        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link"])
            writer.writeheader()
            writer.writerows(all_records)
        print(f"🎯 전수 수집 성공! 총 {len(all_records)}건이 '{file_name}'에 저장되었습니다.", flush=True)
    else:
        print("😭 수집된 데이터가 없습니다.", flush=True)

if __name__ == "__main__":
    fetch_eu_data_hub_all_2025()
